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
