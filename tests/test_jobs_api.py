"""Offline HTTP contract tests; no external fetch or live DNS is used."""
import hashlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.jobs_api import dispatch


class FakeHandler:
    def __init__(self, path, method="GET", payload=None, token=None):
        self.path = path
        self.headers = {}
        self.rfile = io.BytesIO()
        self.wfile = io.BytesIO()
        self.status = None
        if payload is not None:
            data = json.dumps(payload).encode()
            self.rfile = io.BytesIO(data)
            self.headers["Content-Length"] = str(len(data))
        if token is not None:
            self.headers["Authorization"] = "Bearer " + token

    def send_response(self, status):
        self.status = status

    def send_header(self, key, value):
        pass

    def end_headers(self):
        pass

    def body(self):
        return json.loads(self.wfile.getvalue())


class JobsApiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.token = "a" * 40
        self.bob = "b" * 40
        hashes = {
            "alice": hashlib.sha256(self.token.encode()).hexdigest(),
            "bob": hashlib.sha256(self.bob.encode()).hexdigest(),
        }
        self.environment = patch.dict(os.environ, {
            "SITESCOUT_JOBS_ENABLED": "true",
            "SITESCOUT_CAPTURE_ENABLED": "true",
            "SITESCOUT_OPERATOR_TOKEN_HASHES": json.dumps(hashes),
            "SITESCOUT_JOBS_DB": str(Path(self.temp.name) / "jobs.sqlite"),
        })
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def request(self, path, method="GET", payload=None, token=None):
        handler = FakeHandler(path, method, payload, token)
        handled = dispatch(handler, method)
        self.assertTrue(handled)
        return handler

    def test_disabled_default_fails_closed_and_does_not_create_db(self):
        with patch.dict(os.environ, {"SITESCOUT_JOBS_ENABLED": "false"}):
            response = self.request("/api/jobs", token=self.token)
        self.assertEqual(response.status, 403)
        self.assertFalse(Path(os.environ["SITESCOUT_JOBS_DB"]).exists())

    def test_missing_invalid_and_unconfigured_tokens(self):
        self.assertEqual(self.request("/api/jobs").status, 401)
        self.assertEqual(self.request("/api/jobs", token="z" * 40).status, 401)
        with patch.dict(os.environ, {"SITESCOUT_OPERATOR_TOKEN_HASHES": ""}):
            self.assertEqual(self.request("/api/jobs", token=self.token).status, 503)

    def test_submit_list_owned_status_and_audit(self):
        with patch("app.jobs_api.validate_target", return_value=(None, "93.184.215.14")):
            response = self.request("/api/jobs", "POST", {"url": "https://example.org", "mode": "inventory", "authorized": True}, self.token)
        self.assertEqual(response.status, 202)
        job_id = response.body()["job_id"]
        owned = self.request("/api/jobs", token=self.token)
        self.assertEqual(owned.status, 200)
        self.assertEqual(owned.body()["jobs"][0]["id"], job_id)
        self.assertNotIn("url", owned.body()["jobs"][0])
        detail = self.request("/api/jobs/" + job_id, token=self.token)
        self.assertEqual(detail.status, 200)
        self.assertEqual(detail.body()["job"]["status"], "queued")
        self.assertNotIn("url", detail.body()["job"])
        audit = self.request("/api/jobs/" + job_id + "/audit", token=self.token)
        self.assertEqual(audit.body()["events"][0]["event"], "queued")
        self.assertEqual(self.request("/api/jobs", token=self.bob).body()["jobs"], [])
        self.assertEqual(self.request("/api/jobs/" + job_id, token=self.bob).status, 404)
        self.assertEqual(self.request("/api/jobs/" + job_id + "/audit", token=self.bob).status, 404)

    def test_invalid_body_and_methods_do_not_enqueue(self):
        for payload in ([], {"authorized": True}, {"url": None, "authorized": True}, {"url": "https://example.org", "mode": [], "authorized": True}):
            with self.subTest(payload=payload):
                self.assertEqual(self.request("/api/jobs", "POST", payload, self.token).status, 400)
        self.assertEqual(self.request("/api/jobs/no", "POST", {"url": "https://example.org", "authorized": True}, self.token).status, 405)
        self.assertEqual(self.request("/api/jobs/bad-id", token=self.token).status, 404)

    def test_disallows_private_dns_before_enqueue(self):
        with patch("app.jobs_api.validate_target", side_effect=ValueError("unsafe")):
            self.assertEqual(
                self.request("/api/jobs", "POST", {"url": "https://internal.example", "authorized": True}, self.token).status, 400
            )
        self.assertEqual(self.request("/api/jobs", token=self.token).body()["jobs"], [])

    def test_server_rejects_missing_or_nonboolean_authorization(self):
        for asserted in (None, False, 1, "true", {}, []):
            with self.subTest(asserted=asserted):
                with patch("app.jobs_api.validate_target") as resolver:
                    response = self.request(
                        "/api/jobs", "POST",
                        {"url": "https://example.org", "authorized": asserted}, self.token
                    )
                    self.assertEqual(response.status, 403)
                    resolver.assert_not_called()
        self.assertEqual(self.request("/api/jobs", token=self.token).body()["jobs"], [])

    def test_rate_limit_is_shared_for_same_actor(self):
        with patch("app.jobs_api.validate_target", return_value=(None, "93.184.215.14")):
            for _ in range(5):
                self.assertEqual(
                    self.request("/api/jobs", "POST", {"url": "https://example.org", "authorized": True}, self.token).status, 202
                )
            self.assertEqual(
                self.request("/api/jobs", "POST", {"url": "https://example.org", "authorized": True}, self.token).status, 429
            )
            self.assertEqual(
                self.request("/api/jobs", "POST", {"url": "https://example.org", "authorized": True}, self.bob).status, 202
            )
