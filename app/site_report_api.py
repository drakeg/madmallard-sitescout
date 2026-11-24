"""Size-limited offline multi-page site report HTTP endpoint for Docker/Vercel."""
import json

from app.http_api import send_json
from app.site_report import site_report

MAX_REPORT_REQUEST_BYTES = 2_100_000


def respond_site_report(handler):
    try:
        size = int(handler.headers.get("Content-Length", "0"))
        if not 0 < size <= MAX_REPORT_REQUEST_BYTES:
            send_json(handler, 413, {"error": "Site report request exceeds 2.1 MB limit"})
            return
        payload = json.loads(handler.rfile.read(size))
        report = site_report(payload)
        send_json(handler, 200, {"report": report})
    except (ValueError, UnicodeError, TypeError, json.JSONDecodeError):
        send_json(handler, 400, {"error": "Invalid offline site report input"})
