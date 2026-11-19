import io
import unittest
from pathlib import Path
from unittest.mock import patch

from app.server import Handler, DASHBOARD


class DashboardTests(unittest.TestCase):
    def test_dashboard_exists_and_has_accessible_status(self):
        html = DASHBOARD.read_text()
        self.assertIn("<h1>SiteScout</h1>", html)
        self.assertIn('role="status"', html)
        self.assertIn("/api/health", html)

    def test_docker_routes(self):
        for route, expected in (("/", b"SiteScout"), ("/health", b'"status": "ok"'), ("/api/health", b'"status": "ok"')):
            instance = Handler.__new__(Handler)
            instance.path = route
            instance.wfile = io.BytesIO()
            instance.send_response = lambda code: self.assertEqual(code, 200)
            instance.send_header = lambda *args: None
            instance.end_headers = lambda: None
            instance.do_GET()
            self.assertIn(expected, instance.wfile.getvalue())

    def test_vercel_config(self):
        import json
        config = json.loads(Path("vercel.json").read_text())
        self.assertEqual(config["rewrites"][0]["destination"], "/api/health")
