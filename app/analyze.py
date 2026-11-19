"""Pure offline HTML analysis shared by Vercel and Docker."""
from app.directory import directory_candidates
from app.inventory import inventory
from app.findings import summarize

MAX_HTML_BYTES = 512_000

def analyze(payload):
    if not isinstance(payload, dict):
        raise ValueError("Expected a JSON object")
    html = payload.get("html")
    url = payload.get("url")
    mode = payload.get("mode", "inventory")
    if not isinstance(html, str) or not html.strip():
        raise ValueError("Paste saved HTML to analyze")
    if len(html.encode("utf-8")) > MAX_HTML_BYTES:
        raise ValueError("HTML exceeds 500 KiB limit")
    if not isinstance(url, str) or len(url) > 2048:
        raise ValueError("A valid source URL is required")
    if mode == "inventory":
        result = inventory(html, url)
        result["summary"] = summarize(result, mode)
        return result
    if mode == "directory":
        result = directory_candidates(html, url)
        result["summary"] = summarize(result, mode)
        return result
    raise ValueError("Unknown analysis mode")
