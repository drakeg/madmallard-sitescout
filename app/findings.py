"""Explain inventory findings without inventing scores or asserting runtime behavior."""
def summarize(result, mode):
    if mode == "directory":
        count = result["count"]
        return {
            "headline": f"{count} external link candidate(s) found",
            "metrics": [{"label": "Candidates", "value": count}],
            "findings": [
                {"severity": "info", "title": "Human verification required",
                 "detail": "Links are unverified candidates, not confirmed businesses. Review ownership and suitability before contacting anyone."}
            ],
        }

    forms = result["forms"]
    images = result["images"]
    missing_alt = sum(not image["alt"].strip() for image in images)
    headings = result["headings"]
    findings = []
    if not result["title"]:
        findings.append({"severity": "warning", "title": "Missing page title",
                         "detail": "Add a descriptive HTML title for browser tabs and search results."})
    if not any(heading["level"] == "h1" for heading in headings):
        findings.append({"severity": "warning", "title": "No H1 heading found",
                         "detail": "Consider a clear main heading that describes the page."})
    if missing_alt:
        findings.append({"severity": "warning", "title": f"{missing_alt} image(s) without alt text",
                         "detail": "Review each image: give informative images meaningful alternatives; decorative images may use empty alt text."})
    if forms:
        findings.append({"severity": "info", "title": f"{len(forms)} form(s) need functional testing",
                         "detail": "HTML inspection cannot establish that form submissions or integrations work."})
    findings.append({"severity": "info", "title": "JavaScript behavior not verified",
                     "detail": "A browser test is needed to evaluate interactive elements, loading, and real-world accessibility."})
    return {
        "headline": result["title"] or "Untitled page",
        "metrics": [
            {"label": "Internal links", "value": len(result["internal_links"])},
            {"label": "External links", "value": len(result["external_links"])},
            {"label": "Forms", "value": len(forms)},
            {"label": "Images", "value": len(images)},
        ],
        "findings": findings,
    }
