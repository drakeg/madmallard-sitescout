"""Local Docker dashboard and health endpoint."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from app.http_api import respond, send_json

DASHBOARD = Path(__file__).resolve().parent.parent / "index.html"


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if urlsplit(self.path).path == "/api/analyze":
            respond(self)
        else:
            send_json(self, 404, {"error": "Not found"})

    def do_GET(self):
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
