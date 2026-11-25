"""In-memory admission control for opt-in capture on a single Docker worker."""
import hmac
import os
import threading
import time
from collections import deque

class CaptureGuard:
    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.attempts = deque()
        self.lock = threading.Lock()

    def authorize(self, provided, expected):
        return bool(expected and provided and hmac.compare_digest(provided, expected))

    def admit(self, now=None, limit=5, window=60):
        current = self.clock() if now is None else now
        with self.lock:
            while self.attempts and self.attempts[0] <= current - window:
                self.attempts.popleft()
            if len(self.attempts) >= limit:
                return False
            self.attempts.append(current)
            return True

guard = CaptureGuard()

def capture_access(headers):
    secret = os.environ.get("SITESCOUT_CAPTURE_TOKEN", "")
    if len(secret) < 24:
        return 503, "Capture token is not configured securely"
    auth = headers.get("Authorization", "")
    if not auth.startswith("Bearer ") or not guard.authorize(auth[7:], secret):
        return 401, "Valid capture bearer token required"
    if not guard.admit():
        return 429, "Capture rate limit reached; retry later"
    return 200, None


def url_report_capture_access(headers):
    """Allow URL reports without a token only in explicitly trusted local origins.

    The trusted-origin path is opt-in and restricted to configured exact HTTP
    origins on the operator's LAN. Matching Host + Origin and JSON content
    rejects ordinary cross-origin browser requests and DNS-rebinding origins.
    This is a trusted-network convenience mode, not authentication: clients
    able to forge HTTP headers on the LAN can still use the bounded fetcher.
    The legacy bearer-token path remains available in both modes.
    """
    from urllib.parse import urlsplit

    if headers.get("Authorization", ""):
        return capture_access(headers)
    if os.environ.get("SITESCOUT_TRUSTED_LAN_NO_TOKEN") != "true":
        return 401, "Valid capture bearer token required"

    configured = os.environ.get("SITESCOUT_TRUSTED_CAPTURE_ORIGINS", "")
    if not configured or len(configured) > 512:
        return 503, "Trusted capture origins are not configured"
    allowed = {origin.strip() for origin in configured.split(",") if origin.strip()}
    origin = headers.get("Origin", "")
    host = headers.get("Host", "")
    if not origin or origin not in allowed:
        return 403, "Browser origin is not trusted for tokenless capture"
    try:
        parsed = urlsplit(origin)
        valid_origin = (
            parsed.scheme in ("http", "https")
            and parsed.netloc
            and not parsed.username and not parsed.password
            and not parsed.path and not parsed.query and not parsed.fragment
            and parsed.netloc.lower() == host.lower()
        )
    except ValueError:
        valid_origin = False
    if not valid_origin:
        return 403, "Browser origin and host must match"
    if headers.get("Sec-Fetch-Site", "same-origin") != "same-origin":
        return 403, "Cross-site capture requests are prohibited"
    if headers.get("Content-Type", "").split(";", 1)[0].strip().lower() != "application/json":
        return 415, "JSON content type required"
    if not guard.admit():
        return 429, "Capture rate limit reached; retry later"
    return 200, None
