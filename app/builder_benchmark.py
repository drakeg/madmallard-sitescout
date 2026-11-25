"""Offline, deterministic preflight for generated website artifacts.

This tool does not execute generated HTML/JavaScript, load external assets,
contact a website, or verify form delivery, mobile accessibility or licenses.
"""
import argparse
import json
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath

from app.inventory import inventory

MAX_PAGES = 50
MAX_PAGE_BYTES = 512_000
MANUAL_GATES = [
    "Desktop and mobile browser navigation verified against generated routes",
    "Synthetic inquiry form submitted to and received at an authorized test endpoint",
    "Keyboard and screen-reader review plus automated accessibility check",
    "Performance and responsive screenshot comparisons on identical devices",
    "Third-party fonts, media, generated assets, model and dependency license audit",
    "Real model/provider consumption and hosting costs measured and recorded",
]


class _PageMeta(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.viewport = False

    def handle_starttag(self, tag, attrs):
        if tag != "meta":
            return
        attrs = dict(attrs)
        if (str(attrs.get("name", "")).lower() == "viewport"
                and "width=device-width" in str(attrs.get("content", "")).lower()):
            self.viewport = True


def load_briefs(path="fixtures/builder_benchmark_briefs.json"):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    briefs = data.get("briefs")
    if not isinstance(briefs, list) or {b.get("id") for b in briefs} != {
        "contractor", "cafe", "rv-repair"
    } or len(briefs) != 3:
        raise ValueError("Benchmark requires three distinct fixed SMB briefs")
    for brief in briefs:
        required = brief.get("required_pages")
        if not isinstance(required, list) or not required or len(set(required)) != len(required):
            raise ValueError("Each brief needs unique required pages")
        for item in required:
            safe_artifact_path(item)
        if brief.get("form_page") not in required:
            raise ValueError("Form page must be among required pages")
        if not isinstance(brief.get("form_fields"), list) or not brief["form_fields"]:
            raise ValueError("Expected form-field names are required")
    return {brief["id"]: brief for brief in briefs}


def safe_artifact_path(value):
    if not isinstance(value, str):
        raise ValueError("Unsafe benchmark artifact path")
    path = PurePosixPath(value)
    if (path.is_absolute() or not value.endswith(".html")
            or not path.parts or any(part in (".", "..") for part in value.split("/"))
            or "\\" in value):
        raise ValueError("Unsafe benchmark artifact path")
    return path


def evaluate_export(root, brief):
    if not isinstance(brief, dict) or not isinstance(brief.get("required_pages"), list):
        raise ValueError("A benchmark brief is required")
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError("Generated export directory not found")
    html_files = list(root.rglob("*.html"))
    if len(html_files) > MAX_PAGES:
        raise ValueError("Generated export exceeds 50 HTML pages")
    if any(page.is_symlink() for page in html_files):
        raise ValueError("Generated export contains an HTML symlink")
    checks = []

    def check(page, code, passed, evidence):
        checks.append({"page": page, "check": code,
                       "status": "pass" if passed else "fail", "evidence": evidence})

    for relative in brief["required_pages"]:
        safe = safe_artifact_path(relative)
        path = root.joinpath(*safe.parts)
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError("Generated page escapes allowed export root")
        if not path.is_file():
            check(relative, "page-present", False, "Required page is missing")
            continue
        if path.stat().st_size > MAX_PAGE_BYTES:
            raise ValueError("Generated HTML exceeds per-page byte limit")
        html = path.read_text(encoding="utf-8")
        check(relative, "page-present", True, "Required page file exists")
        site = inventory(html, "https://example.invalid/" + relative)
        check(relative, "title", bool(site["title"].strip()),
              "Nonempty source HTML title detected" if site["title"].strip() else "Source HTML title missing")
        headings = [h for h in site["headings"] if h["level"] == "h1" and h["text"].strip()]
        check(relative, "h1", bool(headings),
              "Nonempty source H1 detected" if headings else "Nonempty source H1 missing")
        meta = _PageMeta()
        meta.feed(html)
        check(relative, "mobile-viewport", meta.viewport,
              "Device-width viewport declared" if meta.viewport else "Device-width viewport absent")
        if relative == brief["form_page"]:
            expected = set(brief["form_fields"])
            forms = site["forms"]
            found = any(f["method"] == "POST" and
                        expected.issubset({field["name"] for field in f["fields"]}) for f in forms)
            check(relative, "form-markup", found,
                  "POST form with named expected fields detected" if found else
                  "Expected named POST form fields not detected in source")
    totals = {
        "pass": sum(c["status"] == "pass" for c in checks),
        "fail": sum(c["status"] == "fail" for c in checks),
    }
    return {
        "brief_id": brief["id"],
        "required_pages": brief["required_pages"],
        "observed_html_file_count": len(html_files),
        "static_checks": checks,
        "totals": totals,
        "manual_gates": MANUAL_GATES,
        "provider_cost": "unmeasured",
        "browser_functionality": "unverified",
        "form_delivery": "unverified",
        "license_clearance": "unverified",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Offline builder output benchmark preflight")
    parser.add_argument("--brief", required=True, choices=("contractor", "cafe", "rv-repair"))
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--fail-on-static", action="store_true",
                        help="Exit nonzero if required static checks fail")
    args = parser.parse_args(argv)
    report = evaluate_export(args.output_dir, load_briefs()[args.brief])
    print(json.dumps(report, indent=2))
    return 1 if args.fail_on_static and report["totals"]["fail"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
