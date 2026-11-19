"""Reusable, size-limited JSON HTTP endpoint without outbound fetching."""
import json
from app.analyze import MAX_HTML_BYTES, analyze

def respond(handler):
    try:
        size = int(handler.headers.get("Content-Length", "0"))
        if size < 1 or size > MAX_HTML_BYTES + 4096:
            return send_json(handler, 413, {"error": "Request size must be below 500 KiB"})
        payload = json.loads(handler.rfile.read(size))
        return send_json(handler, 200, {"result": analyze(payload)})
    except (ValueError, UnicodeError, json.JSONDecodeError) as exc:
        return send_json(handler, 400, {"error": str(exc)})

def send_json(handler, status, payload):
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)
