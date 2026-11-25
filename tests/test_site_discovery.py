import unittest

from app.site_discovery import (
    MAX_DISCOVERY_ATTEMPTS, MAX_DISCOVERY_PAGES, discover_report, eligible_link,
)


class BoundedWebsiteDiscoveryTests(unittest.TestCase):
    def test_contact_page_is_discovered_before_generic_link(self):
        home = (
            '<title>Home</title><h1>Home</h1>'
            '<a href="/about">About</a><a href="/contact">Contact</a>'
            '<a href="/services">Services</a><a href="https://elsewhere.org/x">External</a>'
            '<a href="http://example.org/unsafe">HTTP</a><a href="/logout">Logout</a>'
        )
        pages = {
            "https://example.org/":home,
            "https://example.org/contact":'<title>Contact</title><h1>Contact</h1>'
                '<form method="post" action="/inquiry"><input name="email" required></form>',
            "https://example.org/about":'<title>About</title><h1>About</h1>',
        }
        requests = []

        def fetch(url):
            requests.append(url)
            return pages[url]

        result = discover_report("https://example.org/", fetch=fetch)
        self.assertEqual(requests, [
            "https://example.org/", "https://example.org/contact",
            "https://example.org/about",
        ])
        self.assertEqual(result["page_count"], 3)
        self.assertEqual(result["capture_discovery"]["fetch_attempts"], 3)
        self.assertEqual(result["capture_discovery"]["pages_captured"], 3)
        self.assertEqual(result["candidate_contact_booking_pages"], ["https://example.org/contact"])
        self.assertEqual(len(result["forms"]),1)
        self.assertFalse(result["forms"][0]["verified_delivery"])
        self.assertIn("https://example.org/services",result["uncaptured_internal_links"])

    def test_block_cross_host_http_query_unsafe_and_asset_urls(self):
        for link in (
            "http://example.org/", "https://other.org/contact",
            "https://example.org/logout", "https://example.org/admin/settings",
            "https://example.org/delete", "https://example.org/api/search",
            "https://example.org/file.pdf", "https://example.org/contact?next=x",
            "https://user:pass@example.org/contact",
            "https://example.org:8080/contact",
            "file:///etc/passwd",
        ):
            with self.subTest(link=link):
                self.assertIsNone(eligible_link(link,"example.org"))
        self.assertEqual(eligible_link("https://example.org/contact#main","example.org"),
                         "https://example.org/contact")

    def test_failed_secondary_pages_are_not_claimed_broken(self):
        urls=[]
        def fetch(url):
            urls.append(url)
            if url.endswith("/contact"):
                raise TimeoutError("Private environment error")
            if url.endswith("/"):
                return '<h1>Root</h1><a href="/contact">Contact</a><a href="/services">Services</a>'
            return '<title>Services</title><h1>Services</h1>'
        result=discover_report("https://example.org/",fetch=fetch)
        self.assertEqual(result["page_count"],2)
        self.assertEqual(result["capture_discovery"]["additional_page_failures"][0]["url"],
                         "https://example.org/contact")
        self.assertIn("unverified", result["capture_discovery"]["additional_page_failures"][0]["status"])
        self.assertEqual(urls, ["https://example.org/","https://example.org/contact",
                                "https://example.org/services"])

    def test_bounded_outbound_attempts_when_many_pages_fail(self):
        calls=[]
        html='<h1>Home</h1>'+''.join(
            '<a href="/%03d">Link</a>' % number for number in range(120)
        )
        def fetch(url):
            calls.append(url)
            if url.endswith("/"):
                return html
            raise ValueError("404, no redirect follow")
        result=discover_report("https://example.org/",fetch=fetch)
        self.assertEqual(result["page_count"],1)
        self.assertEqual(len(calls),MAX_DISCOVERY_ATTEMPTS)
        self.assertEqual(len(result["capture_discovery"]["additional_page_failures"]),4)

    def test_rejects_invalid_root_and_unbounded_counts(self):
        for url in (None,"","http://example.org/","https://user:secret@example.org/",
                    "https://example.org:8443/"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                discover_report(url,fetch=lambda _: "<h1>test</h1>")
        for limit in (0, MAX_DISCOVERY_PAGES+1, "3"):
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                discover_report("https://example.org/",fetch=lambda _: "<h1>test</h1>",
                                max_pages=limit)
