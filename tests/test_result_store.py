import json
import os
import tempfile
import unittest
from pathlib import Path

from app.result_store import MAX_RESULT_BYTES, save_analysis_result, prune_analysis_results
from app.capture_jobs import CaptureJobStore
from app.capture_worker import CaptureWorker


class PrivateResultExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name) / "results"
        self.job_id = "a" * 32

    def test_stores_private_json_and_refuses_overwrite(self):
        filename = save_analysis_result(self.dir, self.job_id, {"summary": {"title": "Sample"}})
        path = Path(filename)
        self.assertEqual(json.loads(path.read_text())["summary"]["title"], "Sample")
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.dir.stat().st_mode & 0o777, 0o700)
        with self.assertRaises(FileExistsError):
            save_analysis_result(self.dir, self.job_id, {"summary": "different"})

    def test_rejects_oversized_output_and_invalid_id(self):
        with self.assertRaises(ValueError):
            save_analysis_result(self.dir, "not-a-job", {"x": "ok"})
        with self.assertRaises(ValueError):
            save_analysis_result(self.dir, self.job_id, {"body": "x" * MAX_RESULT_BYTES})
        self.assertFalse(self.dir.exists())

    def test_rejects_world_accessible_existing_directory(self):
        self.dir.mkdir(mode=0o755)
        self.dir.chmod(0o755)
        with self.assertRaises(ValueError):
            save_analysis_result(self.dir, self.job_id, {"ok": True})

    def test_expiry_only_deletes_old_regular_results(self):
        old = Path(save_analysis_result(self.dir, self.job_id, {"title": "old"}))
        new = Path(save_analysis_result(self.dir, "b" * 32, {"title": "new"}))
        unknown = self.dir / "operator-notes.json"
        unknown.write_text("retain")
        symlink = self.dir / ("c" * 32 + ".json")
        symlink.symlink_to(unknown)
        os.utime(old, (10, 10))
        self.assertEqual(prune_analysis_results(self.dir, older_than=100), 1)
        self.assertFalse(old.exists())
        self.assertTrue(new.exists())
        self.assertTrue(unknown.exists())
        self.assertTrue(symlink.is_symlink())
        self.assertEqual(prune_analysis_results(self.dir, older_than=100), 0)

    def test_expiry_refuses_world_readable_result_directory(self):
        self.dir.mkdir()
        self.dir.chmod(0o755)
        with self.assertRaises(ValueError):
            prune_analysis_results(self.dir, older_than=100)

    def test_worker_saves_before_success_and_fails_closed_on_export_error(self):
        store = CaptureJobStore(Path(self.temp.name) / "jobs.sqlite3")
        first = store.enqueue("alice", "https://example.org/one")
        good = CaptureWorker(
            store, fetch=lambda url: "<h1>Hello</h1>",
            evaluate=lambda req: {"heading": "Hello"},
            save=lambda ident, result: save_analysis_result(self.dir, ident, result),
        )
        self.assertEqual(good.process_one()["status"], "succeeded")
        self.assertTrue((self.dir / (first + ".json")).exists())

        second = store.enqueue("alice", "https://example.org/two")
        bad = CaptureWorker(
            store, fetch=lambda url: "<h1>Hello</h1>",
            evaluate=lambda req: {"heading": "Hello"},
            save=lambda ident, result: (_ for _ in ()).throw(OSError("disk unavailable")),
        )
        self.assertEqual(bad.process_one()["status"], "failed")
        self.assertEqual(store.get(second, "alice")["error"], "Capture failed")
