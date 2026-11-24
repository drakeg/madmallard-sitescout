"""Evidence-based functional requirements inferred from saved HTML only.

These are verification tasks, never claims that submissions or integrations work.
"""
from urllib.parse import urlparse

FORM_TESTS = (
    "Submit a valid synthetic inquiry and verify the intended destination receives it",
    "Verify required fields reject missing input",
    "Verify confirmation and error handling in desktop and mobile browsers",
)


def functional_requirements(site):
    if not isinstance(site, dict) or not isinstance(site.get("forms"), list):
        raise ValueError("Expected a structured offline site report")
    host = site.get("site_hostname")
    if not isinstance(host, str) or not host:
        raise ValueError("Site hostname is required")
    checks = []
    external_destinations = set()
    for entry in site["forms"]:
        page = entry["page"]
        action = entry["action"]
        method = entry["method"]
        fields = entry["fields"]
        parsed = urlparse(action)
        external = bool(parsed.hostname and parsed.hostname != host)
        if external:
            external_destinations.add(parsed.hostname)
        findings = []
        if external:
            findings.append("Form action points to a different hostname; confirm authorized integration ownership")
        if parsed.scheme == "http":
            findings.append("Form action specifies HTTP; verify secure submission transport")
        if method == "GET":
            findings.append("Form uses GET; check whether submitted fields include sensitive data in URLs")
        if not fields:
            findings.append("No named input fields detected; inspect form behavior manually")
        checks.append({
            "page": page,
            "action": action,
            "method": method,
            "field_count": len(fields),
            "required_fields": [field["name"] for field in fields if field["required"]],
            "test_cases": list(FORM_TESTS),
            "static_warnings": findings,
            "verified_functional": False,
        })
    contact_paths = site.get("candidate_contact_booking_pages", [])
    return {
        "forms_to_test": checks,
        "potential_external_form_hosts": sorted(external_destinations),
        "contact_booking_pages_to_validate": list(contact_paths),
        "unverified_behaviors": [
            "Form delivery, notifications and CRM integrations require end-to-end tests",
            "Contact or booking page presence does not establish availability or successful checkout",
            "JavaScript controls and responsive/mobile workflows require browser testing",
        ],
        "requires_human_verification": True,
    }
