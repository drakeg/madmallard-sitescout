import tempfile
import unittest
from pathlib import Path

from app.builder_benchmark import evaluate_export, load_briefs, safe_artifact_path


class BuilderBenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.briefs = load_briefs()

    def write_site(self, brief, *, missing=None, include_form=True):
        for page in brief["required_pages"]:
            if page == missing:
                continue
            target = self.root / page
            target.parent.mkdir(parents=True, exist_ok=True)
            form = ('<form method="post" action="/api/test-inquiry">'
                    '<input name="name"><input name="email"><textarea name="message"></textarea></form>'
                    if page == brief["form_page"] and include_form else "")
            target.write_text(
                '<!doctype html><html><head><title>Fictional example</title>'
                '<meta name="viewport" content="width=device-width,initial-scale=1">'
                '</head><body><h1>Fictional site</h1>' + form + '</body></html>',
                encoding="utf-8",
            )

    def test_all_three_briefs_are_identical_in_structure(self):
        self.assertEqual(set(self.briefs), {"contractor", "cafe", "rv-repair"})
        for item in self.briefs.values():
            self.assertEqual(len(item["required_pages"]), 3)
            self.assertIn(item["form_page"], item["required_pages"])
            self.assertEqual(set(item["form_fields"]), {"name", "email", "message"})

    def test_static_success_is_not_functional_or_license_verification(self):
        brief = self.briefs["contractor"]
        self.write_site(brief)
        report = evaluate_export(self.root, brief)
        self.assertEqual(report["totals"]["fail"], 0)
        self.assertGreater(report["totals"]["pass"], 0)
        self.assertEqual(report["form_delivery"], "unverified")
        self.assertEqual(report["browser_functionality"], "unverified")
        self.assertEqual(report["license_clearance"], "unverified")
        self.assertEqual(report["provider_cost"], "unmeasured")
        self.assertTrue(any("Synthetic inquiry" in gate for gate in report["manual_gates"]))

    def test_missing_page_and_form_are_reported_as_static_failures(self):
        brief = self.briefs["rv-repair"]
        self.write_site(brief, missing="services/index.html", include_form=False)
        report = evaluate_export(self.root, brief)
        bad = {(c["page"], c["check"]) for c in report["static_checks"] if c["status"] == "fail"}
        self.assertIn(("services/index.html", "page-present"), bad)
        self.assertIn(("request-service/index.html", "form-markup"), bad)
        self.assertNotEqual(report["totals"]["fail"], 0)

    def test_rejects_path_escape_and_html_symlink(self):
        for path in ("../outside.html", "/root.html", "a/../../b.html", "test\\evil.html"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                safe_artifact_path(path)
        brief = self.briefs["cafe"]
        self.write_site(brief)
        extra = self.root / "outside.html"
        extra.symlink_to(self.root / "index.html")
        with self.assertRaises(ValueError):
            evaluate_export(self.root, brief)

    def test_rejects_oversized_html_page(self):
        brief = self.briefs["contractor"]
        self.write_site(brief)
        (self.root / "index.html").write_text("x" * 512001)
        with self.assertRaises(ValueError):
            evaluate_export(self.root, brief)
