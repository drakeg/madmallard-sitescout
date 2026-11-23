"""Durable capture job store tests: no external requests."""
import tempfile
import threading
import unittest
from pathlib import Path

from app.capture_jobs import CaptureJobStore, QueueFullError, RateLimitedError


class CaptureJobStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "captures.sqlite3"
        self.store = CaptureJobStore(self.path)

    def test_persists_job_audit_and_owner_checks_across_reopen(self):
        job_id = self.store.enqueue("alice", "https://example.org/", now=100)
        reopened = CaptureJobStore(self.path)
        self.assertEqual(reopened.get(job_id, "alice")["status"], "queued")
        self.assertIsNone(reopened.get(job_id, "bob"))
        self.assertEqual(reopened.audit(job_id, "bob"), [])
        claimed = reopened.claim(now=101)
        self.assertEqual(claimed["id"], job_id)
        reopened.complete(job_id, True, now=102)
        self.assertEqual(self.store.get(job_id, "alice")["status"], "succeeded")
        self.assertEqual(
            [r["event"] for r in self.store.audit(job_id, "alice")],
            ["queued", "running", "succeeded"],
        )

    def test_actor_rate_limit_is_shared_across_instances(self):
        other = CaptureJobStore(self.path)
        for i in range(5):
            (self.store if i % 2 else other).enqueue(
                "alice", "https://example.org", now=100 + i
            )
        with self.assertRaises(RateLimitedError):
            other.enqueue("alice", "https://example.org", now=105)
        # Independent actor is not rate-limited.
        self.assertTrue(other.enqueue("bob", "https://example.org", now=105))
        self.assertTrue(self.store.enqueue("alice", "https://example.org", now=161))

    def test_queue_bounds_and_no_duplicate_claims(self):
        first = self.store.enqueue("alice", "https://example.org", max_pending=1, now=100)
        with self.assertRaises(QueueFullError):
            self.store.enqueue("bob", "https://example.org", max_pending=1, now=101)
        self.assertEqual(self.store.claim()["id"], first)
        self.assertIsNone(self.store.claim())
        self.store.complete(first, False, error="secret token should not be logged")
        self.assertEqual(self.store.get(first, "alice")["error"], "Capture failed")
        self.assertTrue(self.store.enqueue("bob", "https://example.org", max_pending=1))

    def test_prunes_only_completed_jobs(self):
        finished = self.store.enqueue("alice", "https://example.org", now=100)
        queued = self.store.enqueue("alice", "https://example.org", now=200)
        self.store.claim(now=101)
        self.store.complete(finished, True, now=102)
        self.assertEqual(self.store.prune(older_than=150), 1)
        self.assertIsNone(self.store.get(finished, "alice"))
        self.assertIsNotNone(self.store.get(queued, "alice"))

    def test_invalid_actor_and_mode(self):
        for actor in ("", " ", None, "a" * 129):
            with self.subTest(actor=actor), self.assertRaises(ValueError):
                self.store.enqueue(actor, "https://example.org")
        with self.assertRaises(ValueError):
            self.store.enqueue("alice", "https://example.org", mode="not-a-mode")

    def test_concurrent_enqueue_enforces_queue_bound(self):
        results = []
        lock = threading.Lock()
        def submit(i):
            try:
                self.store.enqueue(f"actor-{i}", "https://example.org", max_pending=3)
                value = "ok"
            except QueueFullError:
                value = "full"
            with lock:
                results.append(value)
        threads = [threading.Thread(target=submit, args=(i,)) for i in range(12)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(results.count("ok"), 3)
        self.assertEqual(results.count("full"), 9)


if __name__ == "__main__":
    unittest.main()
