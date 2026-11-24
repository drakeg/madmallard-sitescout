import tempfile
import unittest
from pathlib import Path

from app.capture_jobs import CaptureJobStore
from app.worker_loop import run_worker_loop
from app.worker_lock import exclusive_worker_lock


class WorkerRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.database = str(Path(self.temp.name) / "jobs.sqlite3")
        self.store = CaptureJobStore(self.database)

    def test_processes_bounded_cycles_without_network(self):
        first = self.store.enqueue("operator", "https://example.org/one")
        second = self.store.enqueue("operator", "https://example.org/two")
        class FakeWorker:
            def __init__(self, store):
                self.store = store
            def process_one(self):
                job = self.store.claim()
                if job:
                    self.store.complete(job["id"], True)
        sleeps = []
        cycles = run_worker_loop(self.store, self.database, worker_factory=FakeWorker,
                                 interval=2, max_cycles=3, sleep=sleeps.append)
        self.assertEqual(cycles, 3)
        self.assertEqual(sleeps, [2, 2])
        self.assertEqual(self.store.get(first, "operator")["status"], "succeeded")
        self.assertEqual(self.store.get(second, "operator")["status"], "succeeded")

    def test_does_not_claim_while_lock_is_held(self):
        job_id = self.store.enqueue("operator", "https://example.org")
        with exclusive_worker_lock(self.database):
            self.assertEqual(run_worker_loop(self.store, self.database,
                                             interval=1, max_cycles=1, sleep=lambda _: None), 1)
        self.assertEqual(self.store.get(job_id, "operator")["status"], "queued")

    def test_stop_and_invalid_config(self):
        self.assertEqual(run_worker_loop(self.store, self.database,
                                         stop=lambda: True,
                                         sleep=lambda _: None, max_cycles=2), 0)
        for interval in (0, -1, 61):
            with self.assertRaises(ValueError):
                run_worker_loop(self.store, self.database, interval=interval)
        for cycles in (0, -1, "2"):
            with self.assertRaises(ValueError):
                run_worker_loop(self.store, self.database, max_cycles=cycles)
