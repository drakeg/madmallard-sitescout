"""Authenticated, explicitly authorized single-page URL report for trusted Docker hosts.

The public Vercel deployment has no live-fetch route. This path reuses the
pinned HTTPS resolver, TLS validation, nonredirecting bounded capture, shared
admission throttling, and deterministic offline report parser.
"""
import json
import os

from app.capture import capture
from app.capture_guard import url_report_capture_access
from app.http_api import send_json
from app.site_discovery import discover_report

MAX_BODY_BYTES = 4096


def respond_url_report(handler, capture_fn=capture):
    if os.environ.get("SITESCOUT_CAPTURE_ENABLED") != "true":
        send_json(handler, 403, {
            "error": "URL analysis is disabled. Enable authorized HTTPS capture on a trusted Docker host."
        })
        return
    try:
        size = int(handler.headers.get("Content-Length", "0"))
        if not 0 < size <= MAX_BODY_BYTES:
            send_json(handler, 413, {"error": "Invalid URL analysis request size"})
            return
        payload = json.loads(handler.rfile.read(size))
        if not isinstance(payload, dict):
            raise ValueError("Expected a JSON object")
        if payload.get("authorized") is not True:
            send_json(handler, 403, {"error": "Explicit website inspection authorization is required"})
            return
        url = payload.get("url")
        if not isinstance(url, str) or not url.startswith("https://") or len(url) > 2048:
            raise ValueError("Enter an authorized public HTTPS URL")
        status, error = url_report_capture_access(handler.headers)
        if error:
            send_json(handler, status, {"error": error})
            return
        report = discover_report(url, fetch=capture_fn)
        send_json(handler, 200, {
            "report": report,
            "capture_scope": "Up to three authorized, same-host public HTTPS pages; no JavaScript or form submissions",
        })
    except (ValueError, TypeError, UnicodeError, json.JSONDecodeError):
        send_json(handler, 400, {"error": "Invalid URL, inaccessible page, or invalid captured HTML"})
    except (OSError, TimeoutError):
        send_json(handler, 502, {"error": "Remote HTTPS page could not be retrieved"})
