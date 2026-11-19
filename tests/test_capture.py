import unittest
from unittest.mock import patch
from app.capture import validate_target

def dns_for(ip):
    return lambda *args, **kwargs: [(2, 1, 6, "", (ip, 443))]

class CaptureSafetyTests(unittest.TestCase):
    def test_public_https_is_accepted(self):
        parsed, ip = validate_target("https://example.org/path", dns_for("93.184.215.14"))
        self.assertEqual(ip, "93.184.215.14")
        self.assertEqual(parsed.path, "/path")

    def test_private_dns_is_rejected(self):
        for ip in ("127.0.0.1", "10.0.0.1", "192.168.1.1", "169.254.169.254", "::1"):
            with self.subTest(ip=ip), self.assertRaises(ValueError):
                validate_target("https://example.org/", dns_for(ip))

    def test_rejects_unsafe_urls(self):
        for url in ("http://example.org", "https://127.0.0.1", "https://example.org:8443", "https://u:p@example.org", "https://localhost"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate_target(url, dns_for("93.184.215.14"))

    def test_mixed_dns_is_rejected(self):
        def resolver(*args, **kwargs):
            return [(2,1,6,"",("93.184.215.14",443)),(2,1,6,"",("10.0.0.1",443))]
        with self.assertRaises(ValueError):
            validate_target("https://example.org", resolver)
