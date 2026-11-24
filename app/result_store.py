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


def prune_analysis_results(directory, *, older_than):
    """Delete only expired, regular result JSON files with trusted job ID names.

    This intentionally does not touch files from other applications, symlinks,
    or active recent exports. Requires an owner-private local results directory.
    """
    root = Path(directory)
    if not root.exists():
        return 0
    if root.is_symlink() or not root.is_dir() or root.stat().st_mode & 0o077:
        raise ValueError("Result directory must be owner-private (0700)")
    removed = 0
    with os.scandir(root) as entries:
        for entry in entries:
            name = entry.name
            if not name.endswith(".json") or JOB_ID.fullmatch(name[:-5]) is None:
                continue
            if not entry.is_file(follow_symlinks=False):
                continue
            if entry.stat(follow_symlinks=False).st_mtime >= older_than:
                continue
            os.unlink(entry.path)
            removed += 1
    return removed


def load_analysis_result(directory, job_id):
    """Read only a small private regular result file; never follow symlinks.

    Returns None when absent. Caller MUST authenticate and authorize the job
    owner before invoking this function.
    """
    import stat
    if not isinstance(job_id, str) or JOB_ID.fullmatch(job_id) is None:
        raise ValueError("Invalid job identifier")
    root = Path(directory)
    if not root.exists():
        return None
    if root.is_symlink() or not root.is_dir() or root.stat().st_mode & 0o077:
        raise ValueError("Result directory must be owner-private (0700)")
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(root / (job_id + ".json"), flags)
    except FileNotFoundError:
        return None
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_mode & 0o077:
            raise ValueError("Unsafe result file")
        if info.st_size > MAX_RESULT_BYTES:
            raise ValueError("Result exceeds configured size limit")
        with os.fdopen(fd, "rb", closefd=False) as handle:
            raw = handle.read(MAX_RESULT_BYTES + 1)
        if len(raw) > MAX_RESULT_BYTES:
            raise ValueError("Result exceeds configured size limit")
        return json.loads(raw)
    finally:
        os.close(fd)
