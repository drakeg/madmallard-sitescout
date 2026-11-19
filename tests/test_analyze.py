import unittest
from app.analyze import analyze

class AnalyzeTests(unittest.TestCase):
    def test_inventory(self):
        result=analyze({"mode":"inventory","url":"https://example.org","html":"<title>Hello</title><h1>Welcome</h1>"})
        self.assertEqual(result["title"], "Hello")

    def test_directory(self):
        result=analyze({"mode":"directory","url":"https://example.org","html":'<a href="https://shop.example/">Shop</a>'})
        self.assertEqual(result["count"], 1)

    def test_rejects_empty_html(self):
        with self.assertRaises(ValueError):
            analyze({"url":"https://example.org","html":""})

    def test_rejects_invalid_mode(self):
        with self.assertRaises(ValueError):
            analyze({"url":"https://example.org","html":"<p>x</p>","mode":"fetch"})

    def test_rejects_oversized_html(self):
        with self.assertRaises(ValueError):
            analyze({"url":"https://example.org","html":"x"*512001})
