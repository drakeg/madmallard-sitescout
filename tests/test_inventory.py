import unittest
from app.inventory import inventory

class InventoryTests(unittest.TestCase):
    def test_extracts_functional_elements(self):
        html = '<title>Shop</title><h1>Welcome</h1><a href="/book">Book</a><form method="post" action="/send"><input name="email" required></form>'
        result = inventory(html, "https://example.com/")
        self.assertEqual(result["title"], "Shop")
        self.assertEqual(result["internal_links"], ["https://example.com/book"])
        self.assertEqual(result["forms"][0]["method"], "POST")
        self.assertTrue(result["forms"][0]["fields"][0]["required"])
    def test_rejects_invalid_base_url(self):
        with self.assertRaises(ValueError):
            inventory("<h1>Hello</h1>", "file:///tmp/demo.html")
    def test_does_not_include_javascript_links(self):
        result = inventory('<a href="javascript:alert(1)">Click</a>', "https://example.com")
        self.assertEqual(result["internal_links"], [])

if __name__ == "__main__":
    unittest.main()
