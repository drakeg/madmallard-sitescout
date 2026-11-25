"""Default-off URL-first analysis route tests without outbound connections."""
import io
import json
import os
import unittest
from unittest.mock import Mock, patch

from app.url_report_api import respond_url_report


class FakeHandler:
    def __init__(self, payload, *, bearer="Bearer private-test-token"):
        self.headers={
            "Content-Length": str(len(payload)),
            "Authorization": bearer,
        }
        self.rfile=io.BytesIO(payload)
        self.wfile=io.BytesIO()
        self.status=None

    def send_response(self, code):
        self.status=code

    def send_header(self, *_args):
        pass

    def end_headers(self):
        pass

    def body(self):
        return json.loads(self.wfile.getvalue())


def request(payload, fn):
    handler=FakeHandler(json.dumps(payload).encode())
    respond_url_report(handler, capture_fn=fn)
    return handler


class UrlReportTests(unittest.TestCase):
    def test_disabled_by_default_even_with_bearer(self):
        capture_fn=Mock()
        with patch.dict(os.environ, {"SITESCOUT_CAPTURE_ENABLED":"false"}):
            result=request({"url":"https://example.org/","authorized":True}, capture_fn)
        self.assertEqual(result.status,403)
        self.assertIn("disabled",result.body()["error"])
        capture_fn.assert_not_called()

    def test_authorization_flag_required_before_auth_or_dns(self):
        capture_fn=Mock()
        for payload in (
            {"url":"https://example.org/"},
            {"url":"https://example.org/","authorized":"true"},
            {"url":"https://example.org/","authorized":False},
        ):
            with self.subTest(payload=payload):
                with patch.dict(os.environ, {"SITESCOUT_CAPTURE_ENABLED":"true"}):
                    with patch("app.url_report_api.capture_access") as access:
                        result=request(payload,capture_fn)
                self.assertEqual(result.status,403)
                access.assert_not_called()
        capture_fn.assert_not_called()

    def test_valid_one_page_populates_site_report_without_crawling(self):
        html='<title>Example</title><h1>Home</h1><a href="/contact">Contact</a>'
        captured=Mock(return_value=html)
        with patch.dict(os.environ, {"SITESCOUT_CAPTURE_ENABLED":"true"}):
            with patch("app.url_report_api.capture_access",return_value=(200,None)):
                result=request({"url":"https://example.org/","authorized":True},captured)
        self.assertEqual(result.status,200)
        self.assertEqual(result.body()["report"]["page_count"],1)
        self.assertIn("https://example.org/contact", result.body()["report"]["uncaptured_internal_links"])
        self.assertIn("no crawling",result.body()["capture_scope"])
        captured.assert_called_once_with("https://example.org/")

    def test_auth_rate_limit_failure_and_rejects_unsupported_url(self):
        captured=Mock()
        with patch.dict(os.environ, {"SITESCOUT_CAPTURE_ENABLED":"true"}):
            for url in ("http://example.org/","file:///etc/passwd","",None,"https://example.org/"+"a"*2048):
                with self.subTest(url=str(url)[:35]):
                    result=request({"url":url,"authorized":True},captured)
                    self.assertEqual(result.status,400)
            with patch("app.url_report_api.capture_access",return_value=(429,"Too many requests")):
                result=request({"url":"https://example.org/","authorized":True},captured)
                self.assertEqual(result.status,429)
        captured.assert_not_called()

    def test_captured_nonhtml_failure_and_request_size_bound(self):
        with patch.dict(os.environ, {"SITESCOUT_CAPTURE_ENABLED":"true"}):
            with patch("app.url_report_api.capture_access",return_value=(200,None)):
                result=request({"url":"https://example.org/","authorized":True},
                               Mock(side_effect=ValueError("No HTML")))
                self.assertEqual(result.status,400)
                self.assertNotIn("No HTML", result.body()["error"])
            fake=FakeHandler(b"")
            fake.headers["Content-Length"]="5000"
            respond_url_report(fake,capture_fn=Mock())
            self.assertEqual(fake.status,413)

    def test_malformed_request_fails_closed(self):
        with patch.dict(os.environ, {"SITESCOUT_CAPTURE_ENABLED":"true"}):
            for bad in (b"not-json", b"[]", b"{}", b""):
                fake=FakeHandler(bad)
                respond_url_report(fake,capture_fn=Mock())
                self.assertIn(fake.status,(400,413))
