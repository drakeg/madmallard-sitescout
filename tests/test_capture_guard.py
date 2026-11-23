import os
import unittest
from unittest.mock import patch
from app.capture_guard import CaptureGuard, capture_access, guard

class GuardTests(unittest.TestCase):
    def test_authentication(self):
        guard_instance = CaptureGuard()
        self.assertTrue(guard_instance.authorize("a"*32, "a"*32))
        self.assertFalse(guard_instance.authorize("wrong", "a"*32))
        self.assertFalse(guard_instance.authorize("", ""))

    def test_rate_limit_and_window(self):
        guard_instance = CaptureGuard()
        self.assertTrue(guard_instance.admit(now=100, limit=2))
        self.assertTrue(guard_instance.admit(now=100, limit=2))
        self.assertFalse(guard_instance.admit(now=101, limit=2))
        self.assertTrue(guard_instance.admit(now=161, limit=2))

    def test_missing_secret_fails_closed(self):
        with patch.dict(os.environ, {"SITESCOUT_CAPTURE_TOKEN": ""}):
            self.assertEqual(capture_access({"Authorization": "Bearer abc"})[0], 503)

    def test_invalid_token_is_rejected(self):
        with patch.dict(os.environ, {"SITESCOUT_CAPTURE_TOKEN": "a"*32}):
            self.assertEqual(capture_access({"Authorization": "Bearer wrong"})[0], 401)

    def test_valid_token_admitted(self):
        with patch.dict(os.environ, {"SITESCOUT_CAPTURE_TOKEN": "a"*32}):
            with patch.object(guard, "admit", return_value=True):
                self.assertEqual(capture_access({"Authorization": "Bearer " + "a"*32})[0], 200)
