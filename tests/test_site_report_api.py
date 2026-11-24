"""Offline site-report HTTP contract; no external requests."""
import io
import json
import unittest

from app.site_report_api import MAX_REPORT_REQUEST_BYTES, respond_site_report


class FakeHandler:
    def __init__(self, raw):
        self.headers = {"Content-Length": str(len(raw))}
        self.rfile = io.BytesIO(raw)
        self.wfile = io.BytesIO()
        self.status = None

    def send_response(self, code):
        self.status = code

    def send_header(self, *args):
        pass

    def end_headers(self):
        pass

    def result(self):
        return json.loads(self.wfile.getvalue())


class SiteReportApiTests(unittest.TestCase):
    def test_successful_multi_page_report(self):
        payload = [
            {"url": "https://example.org/", "html": '<a href="/contact">Contact</a>'},
            {"url": "https://example.org/contact", "html": '<h1>Contact</h1>'},
        ]
        handler = FakeHandler(json.dumps(payload).encode())
        respond_site_report(handler)
        self.assertEqual(handler.status, 200)
        report = handler.result()["report"]
        self.assertEqual(report["page_count"], 2)
        self.assertEqual(report["candidate_contact_booking_pages"], ["https://example.org/contact"])

    def test_rejects_invalid_request_and_oversized_body(self):
        for raw in (b"bad json", b"{}", b"[]"):
            with self.subTest(raw=raw):
                handler = FakeHandler(raw)
                respond_site_report(handler)
                self.assertEqual(handler.status, 400)
        huge = FakeHandler(b"")
        huge.headers["Content-Length"] = str(MAX_REPORT_REQUEST_BYTES + 1)
        respond_site_report(huge)
        self.assertEqual(huge.status, 413)

    def test_invalid_content_length_is_reported_safely(self):
        handler = FakeHandler(b"[]")
        handler.headers["Content-Length"] = "not-a-number"
        respond_site_report(handler)
        self.assertEqual(handler.status, 400)
