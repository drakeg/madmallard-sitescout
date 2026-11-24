"""Local Docker dashboard and health endpoint."""
import json
import os
from app.capture import capture
from app.capture_guard import capture_access
from app.analyze import analyze
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from app.http_api import respond, send_json
from app.jobs_api import dispatch as dispatch_jobs
from app.site_report_api import respond_site_report

DASHBOARD = Path(__file__).resolve().parent.parent / "index.html"

def validate_capture_payload(payload):
    """Reject invalid capture parameters before outbound network requests."""
    if not isinstance(payload, dict):
        raise ValueError("Capture request must be a JSON object")
    url = payload.get("url")
    if not isinstance(url, str) or not url.strip() or len(url) > 2048:
        raise ValueError("A valid HTTPS URL is required")
    mode = payload.get("mode", "inventory")
    if not isinstance(mode, str) or mode not in ("inventory", "directory"):
        raise ValueError("Mode must be inventory or directory")
    return url, mode


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if dispatch_jobs(self, "POST"):
            return
        if urlsplit(self.path).path == "/api/analyze":
            respond(self)
        elif urlsplit(self.path).path == "/api/site_report":
            respond_site_report(self)
        elif urlsplit(self.path).path == "/api/capture":
            if os.environ.get("SITESCOUT_CAPTURE_ENABLED") != "true":
                send_json(self, 403, {"error": "Live capture is disabled. Enable explicitly on a trusted Docker host."})
                return
            status, error = capture_access(self.headers)
            if error:
                send_json(self, status, {"error": error})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 4096:
                    raise ValueError("Invalid request size")
                payload = json.loads(self.rfile.read(length))
                url, mode = validate_capture_payload(payload)
                html = capture(url)
                send_json(self, 200, {"result": analyze({"url": url, "mode": mode, "html": html})})
            except (ValueError, OSError, TimeoutError) as exc:
                send_json(self, 400, {"error": str(exc)})
        else:
            send_json(self, 404, {"error": "Not found"})

    def do_GET(self):
        if dispatch_jobs(self, "GET"):
            return
        path = urlsplit(self.path).path
        if path == "/":
            body = DASHBOARD.read_bytes()
            content_type = "text/html; charset=utf-8"
        elif path in ("/health", "/api/health"):
            body = json.dumps({"status": "ok", "service": "sitescout"}).encode()
            content_type = "application/json; charset=utf-8"
        else:
            self.send_error(404, "Not Found")
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
