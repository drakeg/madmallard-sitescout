import unittest

from app.requirements import functional_requirements
from app.site_report import site_report


class FunctionalRequirementsTests(unittest.TestCase):
    def test_form_delivery_never_claimed_verified(self):
        report = site_report([
            {"url": "https://example.org/", "html": '<a href="/contact">Contact</a>'},
            {"url": "https://example.org/contact", "html":
             '<h1>Contact</h1><form method="post" action="https://forms.vendor.example/lead">'
             '<input name="email" type="email" required><textarea name="message"></textarea></form>'},
        ])
        requirements = report["functional_requirements"]
        self.assertTrue(requirements["requires_human_verification"])
        self.assertEqual(len(requirements["forms_to_test"]), 1)
        form = requirements["forms_to_test"][0]
        self.assertFalse(form["verified_functional"])
        self.assertEqual(form["required_fields"], ["email"])
        self.assertEqual(requirements["potential_external_form_hosts"], ["forms.vendor.example"])
        self.assertTrue(any("different hostname" in message for message in form["static_warnings"]))
        self.assertTrue(any("valid synthetic inquiry" in case for case in form["test_cases"]))

    def test_get_and_http_action_are_flagged_as_unverified(self):
        report = site_report([{
            "url": "https://example.org/",
            "html": '<form action="http://example.org/submit"><input name="query"></form>',
        }])
        warnings = report["functional_requirements"]["forms_to_test"][0]["static_warnings"]
        self.assertTrue(any("HTTP" in message for message in warnings))
        self.assertTrue(any("GET" in message for message in warnings))
        self.assertEqual(report["functional_requirements"]["potential_external_form_hosts"], [])

    def test_formless_site_still_requires_review(self):
        report = site_report([{"url": "https://example.org/", "html": "<h1>Hello</h1>"}])
        self.assertEqual(report["functional_requirements"]["forms_to_test"], [])
        self.assertTrue(report["functional_requirements"]["requires_human_verification"])

    def test_invalid_report_is_rejected(self):
        for invalid in (None, [], {}, {"forms": []}, {"forms": "not-a-list", "site_hostname": "x"}):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                functional_requirements(invalid)
