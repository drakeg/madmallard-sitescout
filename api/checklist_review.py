"""Vercel endpoint for offline human verification checklist review."""
from http.server import BaseHTTPRequestHandler

from app.http_api import send_json
from app.checklist_review_api import respond_checklist_review


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        respond_checklist_review(self)

    def do_GET(self):
        send_json(self, 405, {"error": "POST required"})
