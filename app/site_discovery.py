"""Small, authorization-scoped public HTTPS site discovery.

Only a caller-supplied public HTTPS page and up to two ordinary same-host
HTML links are requested. Every network request uses capture(), which performs
fresh public-IP DNS validation and pinning, TLS certificate verification,
nonredirecting GET, strict HTML size/type checks, and a timeout. No JavaScript,
authentication, form submission, or external-host crawling takes place.
"""
from urllib.parse import urlsplit, urldefrag

from app.capture import capture
from app.inventory import inventory
from app.site_report import JOURNEY_HINTS, site_report

MAX_DISCOVERY_PAGES = 3
MAX_DISCOVERY_ATTEMPTS = 5
SKIP_PATH_WORDS = (
    "logout", "signout", "delete", "remove", "unsubscribe", "checkout",
    "cart", "account", "login", "signin", "register", "reset-password",
    "admin", "wp-admin", "api",
)
SKIP_SUFFIXES = (
    ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg",
    ".ico", ".zip", ".doc", ".docx", ".xls", ".xlsx", ".mp4",
    ".js", ".css", ".json", ".xml", ".rss",
)


def eligible_link(raw, hostname):
    """Accept only same-host HTTPS/443 document paths without query or credentials."""
    if not isinstance(raw, str) or len(raw) > 2048:
        return None
    try:
        url = urldefrag(raw)[0]
        parsed = urlsplit(url)
        if (parsed.scheme != "https" or parsed.hostname != hostname
                or parsed.username or parsed.password
                or parsed.port not in (None, 443)
                or parsed.query or parsed.fragment):
            return None
    except ValueError:
        return None
    path = parsed.path.lower()
    segments = {part for part in path.split("/") if part}
    if segments.intersection(SKIP_PATH_WORDS) or path.endswith(SKIP_SUFFIXES):
        return None
    return url


def discover_report(start_url, fetch=capture, max_pages=MAX_DISCOVERY_PAGES):
    if not isinstance(max_pages, int) or not 1 <= max_pages <= MAX_DISCOVERY_PAGES:
        raise ValueError("Discovery page count must be between one and three")
    if not isinstance(start_url, str) or len(start_url) > 2048:
        raise ValueError("A public HTTPS URL is required")
    try:
        parsed = urlsplit(start_url)
        if (parsed.scheme != "https" or not parsed.hostname
                or parsed.username or parsed.password
                or parsed.port not in (None, 443)):
            raise ValueError("Only public HTTPS website URLs are allowed")
    except ValueError as exc:
        raise ValueError("Only public HTTPS website URLs are allowed") from exc

    hostname = parsed.hostname
    first_url = urldefrag(start_url)[0]
    pending = [first_url]
    scheduled = {first_url}
    pages = []
    failures = []
    attempts = 0
    while pending and len(pages) < max_pages and attempts < MAX_DISCOVERY_ATTEMPTS:
        attempts += 1
        url = pending.pop(0)
        try:
            html = fetch(url)
        except (ValueError, OSError, TimeoutError):
            if url == first_url:
                raise
            failures.append({"url": url, "status": "Not captured; page availability is unverified"})
            continue
        pages.append({"url": url, "html": html})
        if len(pages) >= max_pages:
            break

        item = inventory(html, url)
        choices = []
        for link in item["internal_links"]:
            candidate = eligible_link(link, hostname)
            if candidate is not None and candidate not in scheduled:
                choices.append(candidate)
                scheduled.add(candidate)
        # Give the pilot's most valuable contact/booking/quote journeys priority.
        choices.sort(key=lambda target: (
            0 if JOURNEY_HINTS.search(urlsplit(target).path) else 1,
            target,
        ))
        pending.extend(choices)
        # Avoid an attacker creating unbounded in-memory worklists from huge HTML.
        pending = pending[:20]

    report = site_report(pages)
    report["capture_discovery"] = {
        "pages_captured": len(pages),
        "max_pages": max_pages,
        "fetch_attempts": attempts,
        "additional_page_failures": failures,
        "method": "Bounded, same-host authorized HTTPS links in saved source; no JavaScript or form submission",
        "limitations": [
            "Only selected linked HTML pages were fetched; this is not a comprehensive crawl",
            "Uncaptured URLs are unverified and are not necessarily broken",
            "A captured form does not establish delivery to an inbox or CRM",
        ],
    }
    return report
