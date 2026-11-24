import unittest

from app.site_report import site_report, normalize_url


class OfflineSiteReportTests(unittest.TestCase):
    def test_navigation_forms_and_contact_path(self):
        pages = [
            {"url": "https://example.com/", "html": '<title>Home</title><a href="/services">Services</a><a href="/unseen">Unseen</a>'},
            {"url": "https://example.com/services", "html": '<h1>Services</h1><a href="/contact#form">Contact</a>'},
            {"url": "https://example.com/contact", "html": '<h1>Contact</h1><form method="post" action="/send"><input name="email" required></form>'},
        ]
        report = site_report(pages)
        self.assertEqual(report["page_count"], 3)
        self.assertEqual(report["site_hostname"], "example.com")
        self.assertEqual(report["uncaptured_internal_links"], ["https://example.com/unseen"])
        self.assertEqual(report["candidate_contact_booking_pages"], ["https://example.com/contact"])
        self.assertEqual(report["forms"][0]["method"], "POST")
        self.assertFalse(report["forms"][0]["verified_delivery"])
        home = next(item for item in report["sample_navigation_paths"]
                    if item["from"] == "https://example.com/")
        self.assertEqual(home["path"], ["https://example.com/", "https://example.com/services",
                                        "https://example.com/contact"])
        self.assertFalse(home["verified_functional"])

    def test_does_not_assume_uncaptured_destinations_work(self):
        result = site_report([{"url": "https://example.com/", "html": '<a href="/contact">Contact</a>'}])
        self.assertEqual(result["candidate_contact_booking_pages"], [])
        self.assertEqual(result["sample_navigation_paths"], [])
        self.assertEqual(result["uncaptured_internal_links"], ["https://example.com/contact"])

    def test_rejects_cross_site_and_duplicate_pages(self):
        first = {"url": "https://example.org/", "html": "<h1>Home</h1>"}
        with self.assertRaises(ValueError):
            site_report([first, {"url": "https://elsewhere.org/", "html": "<h1>Other</h1>"}])
        with self.assertRaises(ValueError):
            site_report([first, {"url": "https://example.org/#duplicate", "html": "<h1>Copy</h1>"}])

    def test_size_count_and_shape_bounds(self):
        with self.assertRaises(ValueError):
            site_report([])
        with self.assertRaises(ValueError):
            site_report([{"url": "https://example.org/", "html": "<h1>x</h1>"}] * 21)
        with self.assertRaises(ValueError):
            site_report([{"url": "https://example.org/", "html": "a" * 512001}])
        for invalid in (None, "text", [None], [{"url": "https://example.org/", "html": ""}]):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                site_report(invalid)

    def test_rejects_credentials_and_invalid_schemes(self):
        for url in ("file:///etc/passwd", "https://user:pass@example.org", "javascript:alert(1)"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                normalize_url(url)
        self.assertEqual(normalize_url("https://example.org/contact#details"),
                         "https://example.org/contact")
