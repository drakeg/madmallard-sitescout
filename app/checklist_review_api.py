"""Size-limited HTTP wrapper for offline human checklist review."""
import json

from app.checklist_review import MAX_CSV_BYTES, review_checklist
from app.http_api import send_json

MAX_REQUEST_BYTES = MAX_CSV_BYTES + 4096


def respond_checklist_review(handler):
    try:
        size = int(handler.headers.get("Content-Length", "0"))
        if not 0 < size <= MAX_REQUEST_BYTES:
            send_json(handler, 413, {"error": "Checklist request exceeds size limit"})
            return
        payload = json.loads(handler.rfile.read(size))
        if not isinstance(payload, dict) or not isinstance(payload.get("csv"), str):
            raise ValueError("Expected a checklist CSV string")
        review = review_checklist(payload["csv"])
        send_json(handler, 200, {"review": review})
    except (ValueError, UnicodeError, TypeError, json.JSONDecodeError):
        send_json(handler, 400, {"error": "Invalid checklist CSV or missing verification evidence"})
