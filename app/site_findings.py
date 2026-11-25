"""Explainable static website improvement recommendations.

These findings are limited to authorized saved HTML, never claims about live
rendering, customer conversions, accessibility compliance, or broken links.
"""
from urllib.parse import urlparse

MAX_FINDINGS = 200
SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def remediation_plan(report):
    if not isinstance(report, dict) or not isinstance(report.get("pages"), list):
        raise ValueError("A structured site inventory is required")
    findings = []

    def add(code, severity, page, evidence, recommendation, verification):
        if len(findings) >= MAX_FINDINGS:
            return
        findings.append({
            "code": code,
            "priority": severity,
            "page": page,
            "evidence": evidence,
            "recommendation": recommendation,
            "verification": verification,
            "status": "Needs review",
        })

    for page in report["pages"]:
        url = page["url"]
        if not page.get("title", "").strip():
            add("missing-title", "high", url,
                "No nonempty HTML <title> element in saved source.",
                "Write a descriptive, unique page title.",
                "Inspect the rendered page title and search preview manually.")
        headings = page.get("headings", [])
        h1s = [item for item in headings if item.get("level") == "h1" and item.get("text", "").strip()]
        if not h1s:
            add("missing-h1", "medium", url,
                "No nonempty H1 was detected in saved HTML.",
                "Add a clear H1 describing the purpose of the page.",
                "Check the rendered heading structure and reading order.")
        elif len(h1s) > 1:
            add("multiple-h1", "low", url,
                f"{len(h1s)} nonempty H1 headings appear in saved HTML.",
                "Review heading hierarchy for clarity; multiple H1s are not inherently invalid.",
                "Confirm headings form a useful navigable outline.")
        images = page.get("images", [])
        missing_alt = sum(1 for image in images if not image.get("alt", "").strip())
        if missing_alt:
            add("image-alt-review", "medium", url,
                f"{missing_alt} of {len(images)} image elements have empty or missing alt text.",
                "Review image purpose; use meaningful alt text for informative images and empty alt for decorative ones.",
                "Check informative images with assistive technology; decorative images may correctly have empty alt.")

        for form in page.get("forms", []):
            method = str(form.get("method", "GET")).upper()
            action = str(form.get("action", ""))
            scheme = urlparse(action).scheme.lower()
            if scheme == "http":
                add("insecure-form-action", "high", url,
                    "A form action explicitly uses unencrypted HTTP.",
                    "Review whether the form transmits sensitive information and use a secure HTTPS destination.",
                    "Inspect actual rendered form action, transport, and destination authorization.")
            if method == "GET" and any(
                field.get("type") in ("password", "email", "tel")
                for field in form.get("fields", [])
            ):
                add("get-sensitive-form", "high", url,
                    "A GET form includes a password, email, or telephone field in saved markup.",
                    "Check whether form values may appear in URLs; use a suitable secure submission method.",
                    "Confirm actual form behavior without submitting real personal data.")

    unknown = report.get("uncaptured_internal_links", [])
    if unknown:
        add("unreviewed-internal-destinations", "medium",
            report.get("site_hostname", ""),
            f"{len(unknown)} internal link destinations have not been included in this saved-page report.",
            "Include important internal destinations in the authorized review scope.",
            "Manually verify links; uncaptured does not mean broken.")

    findings.sort(key=lambda finding: (
        SEVERITY_ORDER[finding["priority"]], finding["page"], finding["code"]
    ))
    counts = {priority: sum(item["priority"] == priority for item in findings)
              for priority in ("high", "medium", "low")}
    return {
        "findings": findings,
        "counts": counts,
        "total": len(findings),
        "capped": len(findings) >= MAX_FINDINGS,
        "scope": "Static saved-HTML observations; live behavior and compliance are unverified",
    }
