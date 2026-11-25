import unittest

from app.site_report import site_report


class EvidenceLedNextStepsTests(unittest.TestCase):
    def test_forms_and_high_risk_findings_are_prioritized_without_delivery_claims(self):
        report=site_report([
            {"url":"https://example.org/","html":
             '<html><head></head><body><h1>Home</h1><a href="/contact">Contact</a></body></html>'},
            {"url":"https://example.org/contact","html":
             '<html><head></head><body><h1>Contact</h1><form method="get" action="http://example.org/submit">'
             '<input type="email" name="email" required></form></body></html>'},
        ])
        guidance=report["review_guidance"]
        self.assertEqual(guidance["pages_reviewed"],2)
        self.assertEqual(guidance["forms_identified"],1)
        self.assertGreater(guidance["high_priority_findings"],0)
        titles=[step["title"] for step in guidance["recommended_next_steps"]]
        self.assertEqual(titles[0],"Review high-priority source findings")
        self.assertIn("Verify inquiry delivery with a synthetic test",titles)
        self.assertTrue(all(step["status"]=="Not verified" for step in guidance["recommended_next_steps"]))
        self.assertIn("live functionality remains unverified",guidance["headline"])
        self.assertIn("Actual form, booking, payment or CRM delivery",guidance["not_tested"])

    def test_without_forms_suggest_browser_review_and_unreviewed_links(self):
        report=site_report([{"url":"https://example.org/","html":
            '<html lang="en"><head><title>Home</title><meta name="description" content="Demo">'
            '<meta name="viewport" content="width=device-width"></head><body><h1>Home</h1>'
            '<a href="/contact">Contact</a></body></html>'}])
        titles=[step["title"] for step in report["review_guidance"]["recommended_next_steps"]]
        self.assertIn("Check for client-side or embedded lead forms",titles)
        self.assertIn("Inspect additional site destinations",titles)
        self.assertNotIn("Verify inquiry delivery with a synthetic test",titles)
        self.assertEqual(report["review_guidance"]["uncaptured_internal_destinations"],1)

    def test_response_is_bounded_and_no_fabricated_score(self):
        report=site_report([{"url":"https://example.org/","html":"<title>Example</title><h1>Home</h1>"}])
        guidance=report["review_guidance"]
        self.assertLessEqual(len(guidance["recommended_next_steps"]),8)
        self.assertNotIn("score",guidance)
        self.assertNotIn("verified",guidance)
        self.assertIn("source HTML",guidance["evidence_type"])

    def test_invalid_input_does_not_claim_completed_review(self):
        from app.review_guidance import review_guidance
        for value in (None, {}, {"pages":"invalid"}, []):
            with self.subTest(value=value), self.assertRaises(ValueError):
                review_guidance(value)
