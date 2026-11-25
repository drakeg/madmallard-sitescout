import os
import unittest
from unittest.mock import patch
from app.capture_guard import CaptureGuard, capture_access, url_report_capture_access, guard

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


class TrustedLanCaptureTests(unittest.TestCase):
    def setUp(self):
        self.headers = {
            "Host": "192.168.0.155:8087",
            "Origin": "http://192.168.0.155:8087",
            "Content-Type": "application/json",
            "Sec-Fetch-Site": "same-origin",
        }
        self.env = {
            "SITESCOUT_TRUSTED_LAN_NO_TOKEN": "true",
            "SITESCOUT_TRUSTED_CAPTURE_ORIGINS":
                "http://192.168.0.155:8087,http://localhost:8087",
        }

    def test_opt_in_same_origin_is_rate_limited_without_token(self):
        with patch.dict(os.environ, self.env):
            with patch.object(guard,"admit",return_value=True) as rate:
                self.assertEqual(url_report_capture_access(self.headers),(200,None))
                rate.assert_called_once()

    def test_disabled_requires_token(self):
        with patch.dict(os.environ,{**self.env,"SITESCOUT_TRUSTED_LAN_NO_TOKEN":"false"}):
            self.assertEqual(url_report_capture_access(self.headers)[0],401)

    def test_no_configured_origin_fails_closed(self):
        with patch.dict(os.environ,{**self.env,"SITESCOUT_TRUSTED_CAPTURE_ORIGINS":""}):
            self.assertEqual(url_report_capture_access(self.headers)[0],503)

    def test_rejects_cross_site_or_spoofed_origin_and_invalid_content_type(self):
        cases=[
            ("Origin","https://attacker.test",403),
            ("Origin","null",403),
            ("Origin","http://localhost:8087",403),
            ("Host","evil.test:8087",403),
            ("Sec-Fetch-Site","cross-site",403),
            ("Content-Type","text/plain",415),
        ]
        with patch.dict(os.environ,self.env):
            for key,value,status in cases:
                with self.subTest(key=key,value=value):
                    headers={**self.headers,key:value}
                    with patch.object(guard,"admit") as rate:
                        self.assertEqual(url_report_capture_access(headers)[0],status)
                        rate.assert_not_called()

    def test_rate_limit_still_applies(self):
        with patch.dict(os.environ,self.env):
            with patch.object(guard,"admit",return_value=False):
                self.assertEqual(url_report_capture_access(self.headers)[0],429)

    def test_trusted_mode_does_not_disable_explicit_bearer_auth(self):
        with patch.dict(os.environ,{**self.env,"SITESCOUT_CAPTURE_TOKEN":"a"*32}):
            with patch.object(guard,"admit",return_value=True):
                self.assertEqual(url_report_capture_access({
                    "Authorization":"Bearer "+"a"*32
                })[0],200)
