import unittest
from app.server import Handler, validate_capture_payload


class HealthContractTest(unittest.TestCase):
    def test_handler_has_get(self):
        self.assertTrue(callable(Handler.do_GET))


if __name__ == "__main__":
    unittest.main()


class CapturePreflightTests(unittest.TestCase):
    def test_valid_capture_modes(self):
        self.assertEqual(validate_capture_payload({"url": "https://example.org"}), ("https://example.org", "inventory"))
        self.assertEqual(validate_capture_payload({"url": "https://example.org", "mode": "directory"}), ("https://example.org", "directory"))

    def test_invalid_payloads_are_rejected(self):
        for payload in (None, [], "text", 5, {}, {"url": None}, {"url": ""},
                        {"url": "https://example.org", "mode": "unexpected"},
                        {"url": "https://example.org", "mode": []}):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                validate_capture_payload(payload)

    def test_oversized_url_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_capture_payload({"url": "https://example.org/" + "a" * 2048})
