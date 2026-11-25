"""Scope-aware next steps for a static SiteScout website inspection.

No invented verification, score, rank, compliance or customer-conversion claims.
A priority here is a recommended HUMAN activity based on observed source only.
"""
from urllib.parse import urlsplit

MAX_NEXT_STEPS = 8


def review_guidance(report):
    if not isinstance(report, dict) or not isinstance(report.get("pages"), list):
        raise ValueError("Expected a structured site report")
    pages = report["pages"]
    forms = report.get("forms") or []
    findings = (report.get("remediation_plan") or {}).get("findings") or []
    uncaptured = report.get("uncaptured_internal_links") or []
    discovery = report.get("capture_discovery") or {}
    followups = []

    def add(priority, title, why, action, evidence):
        followups.append({
            "priority": priority,
            "title": title,
            "why": why,
            "next_action": action,
            "evidence": evidence,
            "status": "Not verified",
        })

    high = [item for item in findings if item.get("priority") == "high"]
    medium = [item for item in findings if item.get("priority") == "medium"]
    if high:
        add("high", "Review high-priority source findings",
            f"{len(high)} high-priority issue(s) were flagged in captured source HTML.",
            "Compare each finding with the rendered page, then assign and verify fixes.",
            [item.get("page", "") for item in high[:3]])

    if forms:
        add("high", "Verify inquiry delivery with a synthetic test",
            f"{len(forms)} form(s) were detected, but delivery to the destination was not tested.",
            "With site-owner permission, submit clearly labeled synthetic inquiries and confirm mailbox/CRM receipt.",
            [item.get("page", "") for item in forms[:3]])
    else:
        add("medium", "Check for client-side or embedded lead forms",
            "No form markup was detected in the captured HTML; JavaScript or external embeds may provide forms.",
            "Open the site in a browser and inspect contact, quote and booking interactions.",
            [item.get("url", "") for item in pages[:2]])

    if uncaptured:
        add("medium", "Inspect additional site destinations",
            f"{len(uncaptured)} internal link destination(s) were not included in this report; they may be functional.",
            "Expand authorized page coverage, including contact, services, pricing and booking pages.",
            list(uncaptured[:3]))

    failures = discovery.get("additional_page_failures") or []
    if failures:
        add("medium", "Retry uninspected pages with permission",
            f"{len(failures)} additional page capture attempt(s) did not complete; this is not evidence of broken pages.",
            "Open affected pages manually and diagnose redirects, content type or availability.",
            [item.get("url", "") for item in failures[:3]])

    if medium:
        add("medium", "Review page structure and metadata",
            f"{len(medium)} medium-priority static review item(s) were flagged.",
            "Check findings against browser output and update metadata, headings, alt text or form markup where appropriate.",
            [item.get("page", "") for item in medium[:3]])

    add("medium", "Test the actual mobile and desktop experience",
        "The static HTML parser does not render CSS, run JavaScript or measure mobile layout.",
        "Use a real browser at desktop and narrow viewport widths; test navigation and the contact journey.",
        [item.get("url", "") for item in pages[:2]])

    add("low", "Consider deeper performance and accessibility checks",
        "No performance measurements, accessibility conformance tests or security audit were performed.",
        "Run independently verified browser-based checks and manually review their findings.",
        [])

    return {
        "headline": (
            "Static inspection completed; live functionality remains unverified"
            if pages else "No captured pages available"
        ),
        "pages_reviewed": len(pages),
        "forms_identified": len(forms),
        "high_priority_findings": len(high),
        "medium_priority_findings": len(medium),
        "uncaptured_internal_destinations": len(uncaptured),
        "recommended_next_steps": followups[:MAX_NEXT_STEPS],
        "evidence_type": "Captured or supplied source HTML; no live browser execution or form delivery verification",
        "not_tested": [
            "Rendered visual design and responsive usability",
            "JavaScript-driven navigation or dynamic content",
            "Actual form, booking, payment or CRM delivery",
            "Performance metrics, accessibility compliance and SEO outcomes",
        ],
    }
