import io
import json
import unittest

from app.checklist_review_api import MAX_REQUEST_BYTES, respond_checklist_review
from app.checklist_review import HEADERS


class FakeHandler:
    def __init__(self, data):
        self.headers = {"Content-Length": str(len(data))}
        self.rfile = io.BytesIO(data)
        self.wfile = io.BytesIO()
        self.status = None

    def send_response(self, code):
        self.status = code

    def send_header(self, *args):
        pass

    def end_headers(self):
        pass

    def body(self):
        return json.loads(self.wfile.getvalue())


class ChecklistReviewApiTests(unittest.TestCase):
    def test_valid_review_is_unverified_evidence(self):
        line = ",".join('"' + x + '"' for x in HEADERS)
        row = ',"'.join([]) if False else '"https://example.org/contact","/send","POST","email","Valid desktop inquiry","","Not tested","",""'
        handler = FakeHandler(json.dumps({"csv": line + "\n" + row + "\n"}).encode())
        respond_checklist_review(handler)
        self.assertEqual(handler.status, 200)
        self.assertEqual(handler.body()["review"]["counts"]["not_tested"], 1)
        self.assertIn("not independently verified", handler.body()["review"]["evidence_label"])

    def test_rejects_malformed_and_oversized(self):
        for payload in ([], {}, {"csv": 123}, {"csv": "bad csv"}):
            with self.subTest(payload=payload):
                handler = FakeHandler(json.dumps(payload).encode())
                respond_checklist_review(handler)
                self.assertEqual(handler.status, 400)
        handler = FakeHandler(b"")
        handler.headers["Content-Length"] = str(MAX_REQUEST_BYTES + 1)
        respond_checklist_review(handler)
        self.assertEqual(handler.status, 413)
