import unittest
from app.analyze import analyze

class FindingsTests(unittest.TestCase):
    def test_missing_title_h1_and_alt_are_explained(self):
        result = analyze({"url":"https://example.org/","html":'<img src="/photo.jpg">'})
        titles = [item["title"] for item in result["summary"]["findings"]]
        self.assertIn("Missing page title", titles)
        self.assertIn("No H1 heading found", titles)
        self.assertIn("1 image(s) without alt text", titles)

    def test_good_title_and_heading_not_flagged(self):
        result = analyze({"url":"https://example.org/","html":"<title>Good</title><h1>Hi</h1>"})
        self.assertEqual(result["summary"]["headline"], "Good")
        self.assertNotIn("Missing page title", [f["title"] for f in result["summary"]["findings"]])

    def test_directory_candidates_are_unverified(self):
        result = analyze({"mode":"directory","url":"https://example.org/","html":'<a href="https://vendor.example/">Vendor</a>'})
        self.assertEqual(result["summary"]["metrics"][0]["value"], 1)
        self.assertIn("Human verification", result["summary"]["findings"][0]["title"])
