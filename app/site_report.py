"""Deterministic multi-page offline website inventory for authorized saved HTML.

No network access, JavaScript execution, form submission or outreach.
"""
import json
import re
from collections import deque
from urllib.parse import urldefrag, urlparse

from app.inventory import inventory
from app.requirements import functional_requirements

MAX_PAGES = 20
MAX_PAGE_BYTES = 512_000
MAX_TOTAL_BYTES = 2_000_000
JOURNEY_HINTS = re.compile(r"(^|[/_-])(contact|book|booking|quote|schedule|appointment|reserve|reservation)([/_.-]|$)", re.I)


def normalize_url(url):
    if not isinstance(url, str) or len(url) > 2048:
        raise ValueError("Page URL must be an absolute HTTP(S) URL")
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Page URL must be an absolute HTTP(S) URL without credentials")
    if parsed.port is not None and not 1 <= parsed.port <= 65535:
        raise ValueError("Invalid page URL port")
    return urldefrag(url)[0]


def site_report(pages):
    """Combine saved pages into a navigation and integration inventory.

    pages: list of {"url": absolute_http_url, "html": saved_markup}.
    Non-captured targets are explicitly unverified and not treated as broken.
    """
    if not isinstance(pages, list) or not 1 <= len(pages) <= MAX_PAGES:
        raise ValueError("Provide between 1 and 20 saved pages")
    records = {}
    origin = None
    total = 0
    for entry in pages:
        if not isinstance(entry, dict):
            raise ValueError("Every page must have a URL and saved HTML")
        url = normalize_url(entry.get("url"))
        html = entry.get("html")
        if not isinstance(html, str) or not html.strip():
            raise ValueError("Each page requires saved HTML")
        size = len(html.encode("utf-8"))
        total += size
        if size > MAX_PAGE_BYTES or total > MAX_TOTAL_BYTES:
            raise ValueError("Saved HTML exceeds offline report limits")
        host = urlparse(url).hostname
        if origin is None:
            origin = host
        if host != origin:
            raise ValueError("All pages must belong to one site hostname")
        if url in records:
            raise ValueError("Duplicate captured page URL")
        records[url] = inventory(html, url)

    known = set(records)
    edges = []
    unresolved = set()
    forms = []
    for url, item in records.items():
        for link in item["internal_links"]:
            target = normalize_url(link)
            if target in known:
                edges.append({"from": url, "to": target})
            else:
                unresolved.add(target)
        for form in item["forms"]:
            forms.append({
                "page": url, "method": form["method"],
                "action": form["action"], "fields": form["fields"],
                "verified_delivery": False,
            })

    adjacency = {url: set() for url in known}
    for edge in edges:
        adjacency[edge["from"]].add(edge["to"])

    destinations = sorted(url for url in known if JOURNEY_HINTS.search(urlparse(url).path))
    journeys = []
    for start in sorted(known):
        frontier = deque([(start, [start])])
        seen = {start}
        while frontier:
            node, path = frontier.popleft()
            if node in destinations:
                journeys.append({"from": start, "destination": node,
                                 "path": path, "verified_functional": False})
                break
            for target in sorted(adjacency[node]):
                if target not in seen:
                    seen.add(target)
                    frontier.append((target, path + [target]))
    result = {
        "site_hostname": origin,
        "pages": [records[url] for url in sorted(known)],
        "page_count": len(known),
        "navigation_links": sorted(edges, key=lambda edge: (edge["from"], edge["to"])),
        "uncaptured_internal_links": sorted(unresolved),
        "forms": forms,
        "candidate_contact_booking_pages": destinations,
        "sample_navigation_paths": journeys,
        "limitations": [
            "Uncaptured links are unverified, not necessarily broken",
            "Form delivery, booking integrations and JavaScript behavior were not tested",
            "Navigation paths describe HTML links only, not successful user journeys",
        ],
    }
    result["functional_requirements"] = functional_requirements(result)
    return result


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Report on authorized saved HTML pages; never fetch URLs")
    parser.add_argument("manifest", help="UTF-8 JSON containing pages with url and html fields")
    args = parser.parse_args()
    with open(args.manifest, encoding="utf-8") as stream:
        pages = json.load(stream)
    print(json.dumps(site_report(pages), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
