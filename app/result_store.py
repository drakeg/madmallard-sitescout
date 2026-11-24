"""Explicit opt-in, local-only storage of bounded sanitized analysis JSON.

Captured raw HTML is never written here. Results may contain sensitive text
from authorized pages: use only on a trusted host with protected volume access.
"""
import json
import os
import re
from pathlib import Path

MAX_RESULT_BYTES = 256 * 1024
JOB_ID = re.compile(r"^[0-9a-f]{32}$")


def save_analysis_result(directory, job_id, result):
    if not isinstance(job_id, str) or JOB_ID.fullmatch(job_id) is None:
        raise ValueError("Invalid job identifier")
    serialized = json.dumps(result, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if len(serialized) > MAX_RESULT_BYTES:
        raise ValueError("Analysis result exceeds private export limit")
    root = Path(directory)
    root.mkdir(parents=True, mode=0o700, exist_ok=True)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Unsafe result directory")
    if root.stat().st_mode & 0o077:
        raise ValueError("Result directory must be owner-private (0700)")
    target = root / (job_id + ".json")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(target, flags, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(serialized)
    except BaseException:
        target.unlink(missing_ok=True)
        raise
    return str(target)
