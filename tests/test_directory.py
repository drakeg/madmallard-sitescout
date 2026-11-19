import unittest
from app.directory import directory_candidates

class DirectoryTests(unittest.TestCase):
    def test_external_links_are_review_only(self):
        html = '<a href="/tenants">Tenants</a><a href="https://example-food.com">ORDER ONLINE</a><a href="https://example-food.com">Again</a><a href="https://instagram.com/example">Social</a>'
        result = directory_candidates(html, "https://www.optimisthall.com/tenants")
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["candidates"][0]["label"], "ORDER ONLINE")
        self.assertTrue(result["candidates"][0]["review_required"])
    def test_rejects_non_web_urls(self):
        with self.assertRaises(ValueError):
            directory_candidates("", "file:///tmp/site.html")

if __name__ == "__main__":
    unittest.main()
