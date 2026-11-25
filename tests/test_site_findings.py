import unittest

from app.site_findings import remediation_plan
from app.site_report import site_report


class EvidenceBasedRemediationTests(unittest.TestCase):
    def test_priority_findings_with_actionable_manual_verification(self):
        report = site_report([{
            "url": "https://example.org/",
            "html": '<a href="/about">About</a><h2>Services</h2>'
                    '<img src="/hero.png"><img src="/decoration.svg" alt="">'
                    '<form method="get" action="http://example.org/send">'
                    '<input name="email" type="email" required></form>',
        }])
        plan = report["remediation_plan"]
        codes = [finding["code"] for finding in plan["findings"]]
        self.assertIn("missing-title", codes)
        self.assertIn("missing-h1", codes)
        self.assertIn("image-alt-review", codes)
        self.assertIn("insecure-form-action", codes)
        self.assertIn("get-sensitive-form", codes)
        self.assertIn("unreviewed-internal-destinations", codes)
        self.assertEqual(plan["counts"]["high"], 3)
        self.assertTrue(all(finding["status"] == "Needs review" for finding in plan["findings"]))
        self.assertTrue(all("verification" in finding for finding in plan["findings"]))
        self.assertIn("unverified", plan["scope"])
        priorities = [f["priority"] for f in plan["findings"]]
        self.assertEqual(priorities, sorted(priorities, key={"high":0,"medium":1,"low":2}.get))

    def test_decorative_empty_alt_is_review_not_a_claimed_violation(self):
        report = site_report([{
            "url": "https://example.org/",
            "html": '<title>Home</title><h1>Welcome</h1><img src="/decor.png" alt="">',
        }])
        alt = next(f for f in report["remediation_plan"]["findings"] if f["code"] == "image-alt-review")
        self.assertIn("decorative", alt["recommendation"])
        self.assertNotIn("violation", alt["evidence"])

    def test_well_structured_saved_page_has_no_automatic_failures(self):
        report = site_report([{
            "url": "https://example.org/",
            "html": '<html lang="en"><head><title>Example</title><meta name="description" content="An example"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body><h1>Example</h1><img src="/logo.png" alt="Brand logo"></body></html>',
        }])
        self.assertEqual(report["remediation_plan"]["total"], 0)
        self.assertEqual(report["remediation_plan"]["counts"], {"high":0,"medium":0,"low":0})

    def test_multiple_h1_is_low_priority_review_only(self):
        report = site_report([{
            "url": "https://example.org/",
            "html": '<html lang="en"><head><title>Example</title><meta name="description" content="Example"><meta name="viewport" content="width=device-width"></head><body><h1>Title</h1><h1>Secondary</h1></body></html>',
        }])
        finding = report["remediation_plan"]["findings"][0]
        self.assertEqual(finding["code"], "multiple-h1")
        self.assertEqual(finding["priority"], "low")
        self.assertIn("not inherently invalid", finding["recommendation"])

    def test_missing_metadata_and_duplicate_titles_are_actionable_not_certified(self):
        report = site_report([
            {"url":"https://example.org/","html":"<title>Same</title><h1>Home</h1>"},
            {"url":"https://example.org/services","html":"<title>Same</title><h1>Services</h1>"},
        ])
        codes=[finding["code"] for finding in report["remediation_plan"]["findings"]]
        for expected in ("missing-description","missing-viewport","missing-language","duplicate-page-title"):
            self.assertIn(expected,codes)
        duplicates=[finding for finding in report["remediation_plan"]["findings"]
                    if finding["code"]=="duplicate-page-title"]
        self.assertEqual(len(duplicates),2)
        self.assertTrue(all("captured" in item["evidence"] for item in duplicates))
        self.assertTrue(all("verify" in item["verification"].lower() for item in duplicates))

    def test_rejects_invalid_report_shape(self):
        for value in (None, [], {}, {"pages": "wrong"}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                remediation_plan(value)
