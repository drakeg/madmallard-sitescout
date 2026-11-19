"""Vercel Python endpoint: analyzes pasted HTML, never fetches external URLs."""
from http.server import BaseHTTPRequestHandler
from app.http_api import respond, send_json

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        respond(self)

    def do_GET(self):
        send_json(self, 405, {"error": "POST required"})
