"""Vercel endpoint for offline remediation CSV review."""
from http.server import BaseHTTPRequestHandler

from app.http_api import send_json
from app.remediation_review_api import respond_remediation_review


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        respond_remediation_review(self)

    def do_GET(self):
        send_json(self, 405, {"error": "POST required"})
