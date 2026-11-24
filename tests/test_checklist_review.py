import csv
import io
import unittest

from app.checklist_review import review_checklist, HEADERS, MAX_CSV_BYTES


def rows_to_csv(rows):
    stream = io.StringIO(newline="")
    writer = csv.writer(stream)
    writer.writerow(HEADERS)
    writer.writerows(rows)
    return stream.getvalue()


BASE = ["https://example.org/contact", "https://example.org/send", "POST", "email",
        "Send valid synthetic inquiry", "", "Not tested", "", ""]


class ChecklistReviewTests(unittest.TestCase):
    def test_self_reported_pass_fail_and_follow_up(self):
        passed = BASE.copy()
        passed[5], passed[6], passed[7] = "Received test identifier in authorized inbox", "Passed", "QA Owner"
        failed = BASE.copy()
        failed[5], failed[6], failed[7], failed[8] = "Nothing received", "Failed", "QA Owner", "Investigate routing"
        blocked = BASE.copy()
        blocked[5], blocked[6], blocked[7] = "Destination unavailable", "Blocked", "QA Owner"
        result = review_checklist(rows_to_csv([BASE, passed, failed, blocked]))
        self.assertEqual(result["counts"], {"not_tested": 1, "passed": 1, "failed": 1, "blocked": 1})
        self.assertEqual(len(result["follow_up"]), 2)
        self.assertEqual(result["follow_up"][0]["row"], 4)
        self.assertIn("not independently verified", result["evidence_label"])

    def test_requires_reviewer_and_observation_for_non_untested(self):
        for index in (5, 7):
            row = BASE.copy()
            row[5], row[6], row[7] = "Observed", "Passed", "Reviewer"
            row[index] = ""
            with self.subTest(index=index), self.assertRaises(ValueError):
                review_checklist(rows_to_csv([row]))

    def test_rejects_unsupported_status_and_bad_headers(self):
        row = BASE.copy()
        row[6] = "Complete"
        with self.assertRaises(ValueError):
            review_checklist(rows_to_csv([row]))
        with self.assertRaises(ValueError):
            review_checklist("Status,Observed result\nPassed,Yes\n")
        with self.assertRaises(ValueError):
            review_checklist(rows_to_csv([]))

    def test_quote_and_newline_fields_do_not_break_csv(self):
        row = BASE.copy()
        row[4] = 'Submit quote, verify "confirmation"\non mobile'
        result = review_checklist(rows_to_csv([row]))
        self.assertEqual(result["total_tests"], 1)

    def test_rejects_extra_columns_and_oversized_input(self):
        with self.assertRaises(ValueError):
            review_checklist(rows_to_csv([BASE + ["extra"]]))
        with self.assertRaises(ValueError):
            review_checklist("x" * (MAX_CSV_BYTES + 1))

    def test_limit_rows(self):
        with self.assertRaises(ValueError):
            review_checklist(rows_to_csv([BASE] * 1001))
