"""Vercel serverless endpoint for offline saved-page site reports."""
from http.server import BaseHTTPRequestHandler
from app.http_api import send_json
from app.site_report_api import respond_site_report


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        respond_site_report(self)

    def do_GET(self):
        send_json(self, 405, {"error": "POST required"})
