"""Extract linked business candidates from an authorized saved directory page.

No network requests, AI calls, or outreach. These are unverified candidates.
"""
import json
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

EXCLUDED_HOSTS = {"facebook.com", "instagram.com", "x.com", "twitter.com", "youtube.com", "tiktok.com", "google.com"}

class DirectoryParser(HTMLParser):
    def __init__(self, base_url):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.host = urlparse(base_url).hostname
        self.links = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        attrs = dict(attrs)
        href = attrs.get("href", "")
        url = urljoin(self.base_url, href)
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            return
        if parsed.hostname == self.host or parsed.hostname in EXCLUDED_HOSTS:
            return
        self.current = {"url": url, "label": "", "source": self.base_url}

    def handle_data(self, data):
        if self.current:
            self.current["label"] += data

    def handle_endtag(self, tag):
        if tag == "a" and self.current:
            self.current["label"] = " ".join(self.current["label"].split())
            self.links.append(self.current)
            self.current = None

def directory_candidates(html, base_url):
    parsed = urlparse(base_url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("An absolute http(s) URL is required")
    parser = DirectoryParser(base_url)
    parser.feed(html)
    seen = set()
    candidates = []
    for item in parser.links:
        if item["url"] in seen:
            continue
        seen.add(item["url"])
        item["classification"] = "unverified_external_link"
        item["review_required"] = True
        candidates.append(item)
    return {"source": base_url, "candidates": candidates, "count": len(candidates)}

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Extract unverified external links from a saved HTML directory")
    p.add_argument("html_file")
    p.add_argument("--url", required=True)
    args = p.parse_args()
    with open(args.html_file, encoding="utf-8") as f:
        print(json.dumps(directory_candidates(f.read(), args.url), indent=2))
