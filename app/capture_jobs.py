"""Durable, transaction-safe capture job metadata (no network requests here).

This module is intentionally not exposed as an HTTP endpoint. The current
capture route remains private, default-off and synchronous until actor
authentication, worker isolation and TLS requirements are implemented.
"""
import json
import sqlite3
import time
import uuid
from pathlib import Path

MAX_PENDING = 100
PER_ACTOR_WINDOW = 60
PER_ACTOR_LIMIT = 5
STATES = frozenset({"queued", "running", "succeeded", "failed"})


class QueueFullError(Exception):
    pass


class RateLimitedError(Exception):
    pass


class CaptureJobStore:
    def __init__(self, path):
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        conn = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout = 10000")
        return conn

    def _initialize(self):
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    actor TEXT NOT NULL,
                    url TEXT NOT NULL,
                    mode TEXT NOT NULL CHECK(mode IN ('inventory', 'directory')),
                    status TEXT NOT NULL CHECK(status IN ('queued', 'running', 'succeeded', 'failed')),
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    error TEXT
                );
                CREATE INDEX IF NOT EXISTS jobs_status_created
                    ON jobs(status, created_at);
                CREATE INDEX IF NOT EXISTS jobs_actor_created
                    ON jobs(actor, created_at);
                CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    event TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    FOREIGN KEY(job_id) REFERENCES jobs(id)
                );
            """)

    def enqueue(self, actor, url, mode="inventory", *, now=None,
                max_pending=MAX_PENDING, per_actor_limit=PER_ACTOR_LIMIT):
        if not isinstance(actor, str) or not actor.strip() or len(actor) > 128:
            raise ValueError("An authenticated actor identifier is required")
        if not isinstance(url, str) or not url.startswith("https://") or len(url) > 2048:
            raise ValueError("A public HTTPS URL is required")
        if mode not in ("inventory", "directory"):
            raise ValueError("Unsupported capture mode")
        stamp = time.time() if now is None else now
        identifier = uuid.uuid4().hex
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            pending = conn.execute(
                "SELECT COUNT(*) FROM jobs WHERE status IN ('queued','running')"
            ).fetchone()[0]
            if pending >= max_pending:
                raise QueueFullError("Capture queue is full")
            recent = conn.execute(
                "SELECT COUNT(*) FROM jobs WHERE actor=? AND created_at>?",
                (actor, stamp - PER_ACTOR_WINDOW),
            ).fetchone()[0]
            if recent >= per_actor_limit:
                raise RateLimitedError("Capture actor rate limit reached")
            conn.execute(
                "INSERT INTO jobs VALUES (?,?,?,?,?,?,?,?)",
                (identifier, actor, url, mode, "queued", stamp, stamp, None),
            )
            conn.execute(
                "INSERT INTO audit_events(job_id,actor,event,created_at) VALUES(?,?,?,?)",
                (identifier, actor, "queued", stamp),
            )
        return identifier

    def claim(self, *, now=None):
        stamp = time.time() if now is None else now
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT * FROM jobs WHERE status='queued' ORDER BY created_at,id LIMIT 1"
            ).fetchone()
            if row is None:
                return None
            conn.execute(
                "UPDATE jobs SET status='running',updated_at=? WHERE id=?",
                (stamp, row["id"]),
            )
            conn.execute(
                "INSERT INTO audit_events(job_id,actor,event,created_at) VALUES(?,?,?,?)",
                (row["id"], row["actor"], "running", stamp),
            )
            return dict(row) | {"status": "running", "updated_at": stamp}

    def complete(self, job_id, success, *, now=None, error=None):
        stamp = time.time() if now is None else now
        state = "succeeded" if success else "failed"
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT actor,status FROM jobs WHERE id=?", (job_id,)
            ).fetchone()
            if row is None or row["status"] != "running":
                raise ValueError("Only running jobs may be completed")
            # Never persist raw target HTML, credentials or untrusted errors.
            safe_error = "Capture failed" if not success else None
            conn.execute(
                "UPDATE jobs SET status=?,updated_at=?,error=? WHERE id=?",
                (state, stamp, safe_error, job_id),
            )
            conn.execute(
                "INSERT INTO audit_events(job_id,actor,event,created_at) VALUES(?,?,?,?)",
                (job_id, row["actor"], state, stamp),
            )

    def get(self, job_id, actor):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM jobs WHERE id=? AND actor=?", (job_id, actor)
            ).fetchone()
        return dict(row) if row is not None else None

    def audit(self, job_id, actor):
        if self.get(job_id, actor) is None:
            return []
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT event,created_at FROM audit_events WHERE job_id=? AND actor=? ORDER BY id",
                (job_id, actor),
            ).fetchall()
        return [dict(row) for row in rows]

    def prune(self, *, older_than):
        """Remove completed jobs older than a timestamp; retain active jobs."""
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            ids = [r[0] for r in conn.execute(
                "SELECT id FROM jobs WHERE status IN ('succeeded','failed') AND updated_at<?",
                (older_than,),
            ).fetchall()]
            for job_id in ids:
                conn.execute("DELETE FROM audit_events WHERE job_id=?", (job_id,))
                conn.execute("DELETE FROM jobs WHERE id=?", (job_id,))
            return len(ids)
