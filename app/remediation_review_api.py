"""Size-limited HTTP adapter for manual remediation action-plan review."""
import json

from app.http_api import send_json
from app.remediation_review import review_remediation_csv, MAX_BYTES

MAX_REQUEST_BYTES = MAX_BYTES + 4096


def respond_remediation_review(handler):
    try:
        size = int(handler.headers.get("Content-Length", "0"))
        if not 0 < size <= MAX_REQUEST_BYTES:
            send_json(handler, 413, {"error": "Action-plan review exceeds size limit"})
            return
        payload = json.loads(handler.rfile.read(size))
        if not isinstance(payload, dict) or not isinstance(payload.get("csv"), str):
            raise ValueError("Expected CSV content")
        send_json(handler, 200, {"review": review_remediation_csv(payload["csv"])})
    except (ValueError, UnicodeError, TypeError, json.JSONDecodeError):
        send_json(handler, 400, {"error": "Invalid remediation CSV or missing review evidence"})
