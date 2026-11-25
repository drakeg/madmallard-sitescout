"""Read-only HTML site inventory. No network access or JavaScript execution."""
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
import json

class SiteParser(HTMLParser):
    def __init__(self, base_url):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.links = []
        self.forms = []
        self.images = []
        self.headings = []
        self.title = ""
        self.meta_description = ""
        self.viewport = ""
        self.html_language = ""
        self._capture = None
        self._form = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.html_language = attrs.get("lang", "") or ""
        if tag == "meta":
            name = (attrs.get("name") or "").strip().lower()
            if name == "description":
                self.meta_description = attrs.get("content", "") or ""
            if name == "viewport":
                self.viewport = attrs.get("content", "") or ""
        if tag == "title" or tag in ("h1", "h2", "h3"):
            self._capture = [tag, ""]
        if tag == "a" and attrs.get("href"):
            target = urljoin(self.base_url, attrs["href"])
            if urlparse(target).scheme in ("http", "https"):
                self.links.append(target)
        if tag == "img":
            self.images.append({"src": urljoin(self.base_url, attrs.get("src", "")), "alt": attrs.get("alt", "")})
        if tag == "form":
            self._form = {"method": attrs.get("method", "get").upper(), "action": urljoin(self.base_url, attrs.get("action", "")), "fields": []}
        if tag in ("input", "select", "textarea") and self._form is not None:
            self._form["fields"].append({"name": attrs.get("name", ""), "type": attrs.get("type", tag), "required": "required" in attrs})
    def handle_data(self, data):
        if self._capture:
            self._capture[1] += data
    def handle_endtag(self, tag):
        if self._capture and self._capture[0] == tag:
            kind, value = self._capture
            if kind == "title": self.title = value.strip()
            else: self.headings.append({"level": kind, "text": value.strip()})
            self._capture = None
        if tag == "form" and self._form is not None:
            self.forms.append(self._form)
            self._form = None

def inventory(html, url):
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("An absolute http(s) URL is required")
    parser = SiteParser(url)
    parser.feed(html)
    domain = parsed.hostname
    return {
        "url": url, "title": parser.title, "meta_description": parser.meta_description,
        "viewport": parser.viewport, "html_language": parser.html_language,
        "headings": parser.headings,
        "internal_links": sorted(set(link for link in parser.links if urlparse(link).hostname == domain)),
        "external_links": sorted(set(link for link in parser.links if urlparse(link).hostname != domain)),
        "forms": parser.forms, "images": parser.images,
        "unknowns": ["JavaScript-driven behaviors require browser testing", "Form delivery and external integrations are unverified"],
    }

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Inventory an authorized saved HTML page; never fetches external URLs")
    p.add_argument("html_file")
    p.add_argument("--url", required=True)
    args = p.parse_args()
    with open(args.html_file, encoding="utf-8") as f:
        print(json.dumps(inventory(f.read(), args.url), indent=2))
