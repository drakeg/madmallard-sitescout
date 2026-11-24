"""Default-off, Docker-only authenticated capture-job metadata API.

Bearer-token digests map to actor identities. No session cookies, CORS,
public exposure, captured HTML or result access are provided here.
"""
import json
import os
import re
import sqlite3
from urllib.parse import urlsplit

from app.capture import validate_target
from app.capture_jobs import CaptureJobStore, QueueFullError, RateLimitedError
from app.http_api import send_json
from app.operator_auth import authenticate_operator

JOB_ID = re.compile(r"^[0-9a-f]{32}$")
MAX_BODY = 4096


def dispatch(handler, method):
    """Handle /api/jobs routes. Return True when route was recognized."""
    path = urlsplit(handler.path).path
    if path != "/api/jobs" and not path.startswith("/api/jobs/"):
        return False
    if method not in ("GET", "POST"):
        send_json(handler, 405, {"error": "Method not allowed"})
        return True
    if (os.environ.get("SITESCOUT_JOBS_ENABLED") != "true"
            or os.environ.get("SITESCOUT_CAPTURE_ENABLED") != "true"):
        send_json(handler, 403, {"error": "Capture jobs are disabled"})
        return True
    status, actor = authenticate_operator(handler.headers)
    if status != 200:
        send_json(handler, status, {"error": "Operator authentication required"})
        return True
    try:
        store = CaptureJobStore(os.environ.get(
            "SITESCOUT_JOBS_DB", "/data/capture_jobs.sqlite3"))
        if path == "/api/jobs":
            if method == "POST":
                size = int(handler.headers.get("Content-Length", "0"))
                if not 0 < size <= MAX_BODY:
                    send_json(handler, 413, {"error": "Invalid job request size"})
                    return True
                payload = json.loads(handler.rfile.read(size))
                if not isinstance(payload, dict):
                    raise ValueError("Request must be a JSON object")
                url = payload.get("url")
                mode = payload.get("mode", "inventory")
                if not isinstance(url, str) or not url or len(url) > 2048:
                    raise ValueError("Valid public HTTPS URL required")
                if not isinstance(mode, str) or mode not in ("inventory", "directory"):
                    raise ValueError("Invalid analysis mode")
                validate_target(url)
                job_id = store.enqueue(actor, url, mode)
                send_json(handler, 202, {"job_id": job_id, "status": "queued"})
                return True
            send_json(handler, 200, {"jobs": store.list_for_actor(actor)})
            return True
        if method != "GET":
            send_json(handler, 405, {"error": "Method not allowed"})
            return True
        parts = path.removeprefix("/api/jobs/").split("/")
        if len(parts) not in (1, 2) or not JOB_ID.fullmatch(parts[0]):
            send_json(handler, 404, {"error": "Job not found"})
            return True
        job_id = parts[0]
        job = store.get(job_id, actor)
        if job is None:
            send_json(handler, 404, {"error": "Job not found"})
            return True
        if len(parts) == 2:
            if parts[1] != "audit":
                send_json(handler, 404, {"error": "Job not found"})
                return True
            send_json(handler, 200, {"events": store.audit(job_id, actor)})
            return True
        visible = {key: job[key] for key in
                   ("id", "mode", "status", "created_at", "updated_at", "error")}
        send_json(handler, 200, {"job": visible})
        return True
    except (ValueError, TypeError, json.JSONDecodeError):
        send_json(handler, 400, {"error": "Invalid job request"})
    except RateLimitedError:
        send_json(handler, 429, {"error": "Capture admission limit exceeded"})
    except QueueFullError:
        send_json(handler, 503, {"error": "Capture queue capacity reached"})
    except sqlite3.Error:
        send_json(handler, 503, {"error": "Capture job store unavailable"})
    return True
