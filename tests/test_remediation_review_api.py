import csv
import io
import json
import unittest

from app.remediation_review import HEADERS
from app.remediation_review_api import MAX_REQUEST_BYTES, respond_remediation_review


class FakeHandler:
    def __init__(self, payload):
        self.headers={"Content-Length":str(len(payload))}
        self.rfile=io.BytesIO(payload)
        self.wfile=io.BytesIO()
        self.status=None

    def send_response(self, code):
        self.status=code

    def send_header(self,*args):
        pass

    def end_headers(self):
        pass

    def result(self):
        return json.loads(self.wfile.getvalue())


class RemediationReviewApiTests(unittest.TestCase):
    def test_valid_review(self):
        output=io.StringIO(newline="")
        writer=csv.writer(output)
        writer.writerow(HEADERS)
        writer.writerow(["high","missing-title","https://example.org/","No title",
                         "Add title","Inspect browser title","Needs review","","",""])
        body=json.dumps({"csv":output.getvalue()}).encode()
        handler=FakeHandler(body)
        respond_remediation_review(handler)
        self.assertEqual(handler.status,200)
        self.assertEqual(handler.result()["review"]["counts"]["needs_review"],1)

    def test_bad_json_type_evidence_and_oversized_request(self):
        for payload in (b"bad",b"{}",b"[]",json.dumps({"csv":"invalid"}).encode()):
            with self.subTest(payload=payload):
                handler=FakeHandler(payload)
                respond_remediation_review(handler)
                self.assertEqual(handler.status,400)
        handler=FakeHandler(b"")
        handler.headers["Content-Length"]=str(MAX_REQUEST_BYTES+1)
        respond_remediation_review(handler)
        self.assertEqual(handler.status,413)
