import tempfile
import unittest
from pathlib import Path

from app.capture_jobs import CaptureJobStore
from app.capture_worker import CaptureWorker


class CaptureWorkerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = CaptureJobStore(Path(self.temp.name) / "jobs.sqlite")

    def test_one_job_per_call_and_no_job(self):
        first = self.store.enqueue("alice", "https://example.org/one")
        second = self.store.enqueue("alice", "https://example.org/two")
        calls = []
        def fetch(url):
            calls.append(url)
            return "<title>OK</title>"
        worker = CaptureWorker(self.store, fetch=fetch, evaluate=lambda p: {"mode": p["mode"]})
        self.assertEqual(worker.process_one()["id"], first)
        self.assertEqual(self.store.get(first, "alice")["status"], "succeeded")
        self.assertEqual(self.store.get(second, "alice")["status"], "queued")
        self.assertEqual(worker.process_one()["id"], second)
        self.assertIsNone(worker.process_one())
        self.assertEqual(len(calls), 2)

    def test_failure_is_sanitized_and_audited(self):
        identifier = self.store.enqueue("alice", "https://example.org")
        def broken(url):
            raise ValueError("Sensitive upstream response: secret=not-for-storage")
        result = CaptureWorker(self.store, fetch=broken).process_one()
        self.assertEqual(result, {"id": identifier, "status": "failed"})
        self.assertEqual(self.store.get(identifier, "alice")["error"], "Capture failed")
        self.assertEqual([e["event"] for e in self.store.audit(identifier, "alice")],
                         ["queued", "running", "failed"])

    def test_programming_error_is_audited_and_raised(self):
        identifier = self.store.enqueue("alice", "https://example.org")
        def broken(url):
            raise RuntimeError("unexpected worker bug")
        with self.assertRaises(RuntimeError):
            CaptureWorker(self.store, fetch=broken).process_one()
        self.assertEqual(self.store.get(identifier, "alice")["status"], "failed")

    def test_stale_recovery_only_requeues_old_running_jobs(self):
        first = self.store.enqueue("alice", "https://example.org/one", now=100)
        second = self.store.enqueue("alice", "https://example.org/two", now=200)
        self.store.claim(now=101)
        self.assertEqual(self.store.recover_stale(before=101, now=250), 0)
        self.assertEqual(self.store.recover_stale(before=200, now=251), 1)
        self.assertEqual(self.store.get(first, "alice")["status"], "queued")
        self.assertEqual(self.store.get(second, "alice")["status"], "queued")
        self.assertEqual([e["event"] for e in self.store.audit(first, "alice")],
                         ["queued", "running", "requeued"])
        self.assertEqual(self.store.recover_stale(before=300, now=301), 0)
