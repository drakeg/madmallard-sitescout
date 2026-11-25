import csv
import io
import unittest

from app.remediation_review import HEADERS, review_remediation_csv


def csv_rows(rows):
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(HEADERS)
    writer.writerows(rows)
    return output.getvalue()


BASE = ["high", "missing-title", "https://example.org/", "No HTML title",
        "Add descriptive title", "Inspect rendered browser title",
        "Needs review", "", "", ""]


class RemediationReviewTests(unittest.TestCase):
    def test_needs_review_and_evidence_backed_implemented(self):
        implemented = BASE.copy()
        implemented[6:] = ["Implemented", "Website team", "ticket-123", "Reviewed in staging"]
        deferred = BASE.copy()
        deferred[6:] = ["Deferred", "Owner", "", "Approved due to replacement plans"]
        result = review_remediation_csv(csv_rows([BASE, implemented, deferred]))
        self.assertEqual(result["counts"], {
            "needs_review": 1, "in_progress": 0, "implemented": 1, "deferred": 1
        })
        self.assertEqual(len(result["follow_up"]), 2)
        self.assertIn("not independently verified", result["evidence_label"])

    def test_incomplete_evidence_rejected(self):
        for status, owner, evidence, notes in [
            ("Implemented", "", "ticket-123", "Reviewed"),
            ("Implemented", "Owner", "", "Reviewed"),
            ("Implemented", "Owner", "ticket-123", ""),
            ("Deferred", "Owner", "", ""),
            ("In progress", "", "", ""),
            ("Verified", "Owner", "ticket-123", "Reviewed"),
        ]:
            with self.subTest(status=status, owner=owner, evidence=evidence):
                row = BASE.copy()
                row[6:] = [status, owner, evidence, notes]
                with self.assertRaises(ValueError):
                    review_remediation_csv(csv_rows([row]))

    def test_rejects_bad_headers_empty_and_malformed_rows(self):
        for data in ("", "Status,Result\\nImplemented,done\\n",
                     csv_rows([]), csv_rows([BASE + ["extra"]])):
            with self.subTest(data=data[:20]), self.assertRaises(ValueError):
                review_remediation_csv(data)

    def test_preserves_quotes_commas_and_newlines_as_data(self):
        row = BASE.copy()
        row[3] = 'Page said "contact", not \n necessarily broken'
        result = review_remediation_csv(csv_rows([row]))
        self.assertEqual(result["total"], 1)
