import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.capture_jobs import CaptureJobStore
from app.worker_cli import run


class WorkerCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.database = str(Path(self.temp.name) / "jobs.sqlite3")
        self.enable = patch.dict(os.environ, {"SITESCOUT_CAPTURE_ENABLED": "true"})
        self.enable.start()
        self.addCleanup(self.enable.stop)

    def call(self, *args, worker_factory=None):
        stdout, stderr = io.StringIO(), io.StringIO()
        kwargs = {"worker_factory": worker_factory} if worker_factory else {}
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = run(["--database", self.database, *args], **kwargs)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_disabled_is_fail_closed_and_creates_no_db(self):
        with patch.dict(os.environ, {"SITESCOUT_CAPTURE_ENABLED": "false"}):
            code, _, _ = self.call("work-once")
        self.assertEqual(code, 3)
        self.assertFalse(Path(self.database).exists())

    def test_submission_requires_operator_confirmation(self):
        code, _, _ = self.call("submit", "--actor", "alice", "--url", "https://example.org")
        self.assertEqual(code, 2)
        self.assertFalse(Path(self.database).exists())

    def test_workflow_and_actor_scope(self):
        with patch("app.worker_cli.validate_target", return_value=(None, "93.184.215.14")):
            code, stdout, _ = self.call("submit", "--actor", "alice",
                                        "--url", "https://example.org", "--authorized")
        self.assertEqual(code, 0)
        import json
        job_id = json.loads(stdout)["job_id"]
        self.assertTrue(job_id)
        self.assertEqual(self.call("status", "--actor", "bob", "--job-id", job_id)[0], 4)
        self.assertEqual(self.call("audit", "--actor", "bob", "--job-id", job_id)[0], 4)
        self.assertIn("queued", self.call("status", "--actor", "alice", "--job-id", job_id)[1])

        class StubWorker:
            def __init__(self, store):
                self.store = store
            def process_one(self):
                claimed = self.store.claim()
                self.store.complete(claimed["id"], True)
                return {"id": claimed["id"], "status": "succeeded",
                        "result": {"untrusted_page": "do-not-echo"}}
        code, output, _ = self.call("work-once", worker_factory=StubWorker)
        self.assertEqual(code, 0)
        self.assertNotIn("do-not-echo", output)
        self.assertIn("succeeded", output)
        self.assertIn("succeeded", self.call("audit", "--actor", "alice", "--job-id", job_id)[1])
        self.assertEqual(self.call("prune", "--older-than-days", "0")[0], 2)


    def test_recovery_rejects_too_short_threshold(self):
        code, _, stderr = self.call("recover", "--older-than-seconds", "0")
        self.assertEqual(code, 2)
        self.assertIn("at least 60", stderr)

    def test_worker_busy_fails_without_claiming_job(self):
        from app.worker_lock import exclusive_worker_lock
        store = CaptureJobStore(self.database)
        identifier = store.enqueue("alice", "https://example.org")
        with exclusive_worker_lock(self.database):
            code, _, stderr = self.call("work-once")
        self.assertEqual(code, 7)
        self.assertIn("worker is active", stderr)
        self.assertEqual(store.get(identifier, "alice")["status"], "queued")

    def test_private_result_pruning_respects_retention(self):
        from app.result_store import save_analysis_result
        import json
        import time
        directory = Path(self.temp.name) / "results"
        filename = save_analysis_result(directory, "a" * 32, {"summary": "sample"})
        os.utime(filename, (10, 10))
        with patch.dict(os.environ, {"SITESCOUT_RESULTS_DIR": str(directory)}):
            code, output, _ = self.call("prune-results", "--older-than-days", "1")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output)["result_files_removed"], 1)
        self.assertFalse(Path(filename).exists())

    def test_listing_is_owner_scoped_and_excludes_urls(self):
        store = CaptureJobStore(self.database)
        owned = store.enqueue("alice", "https://example.org/private-path")
        store.enqueue("bob", "https://example.org/other-private-path")
        code, output, _ = self.call("list", "--actor", "alice", "--limit", "1")
        self.assertEqual(code, 0)
        self.assertIn(owned, output)
        self.assertNotIn("private-path", output)
        self.assertNotIn("other-private-path", output)
        self.assertEqual(self.call("list", "--actor", "alice", "--limit", "0")[0], 2)

    def test_work_loop_passes_interval_and_save_configuration(self):
        with patch("app.worker_cli.run_worker_loop", return_value=2) as loop:
            code, output, _ = self.call("work-loop", "--interval-seconds", "2")
            self.assertEqual(code, 0)
            self.assertEqual(output, "")
            self.assertEqual(loop.call_args.kwargs["interval"], 2)
            self.assertTrue(callable(loop.call_args.kwargs["worker_factory"]))
        with patch("app.worker_cli.run_worker_loop", return_value=1) as loop:
            code, _, _ = self.call("work-loop", "--save-results")
            self.assertEqual(code, 0)
            self.assertTrue(callable(loop.call_args.kwargs["worker_factory"]))
        code, _, _ = self.call("work-loop", "--interval-seconds", "0")
        self.assertEqual(code, 2)

    def test_invalid_public_target_is_rejected(self):
        with patch("app.worker_cli.validate_target", side_effect=ValueError("private")):
            code, _, stderr = self.call("submit", "--actor", "alice",
                                         "--url", "https://internal.local", "--authorized")
        self.assertEqual(code, 2)
        self.assertIn("public HTTPS", stderr)
        self.assertFalse(Path(self.database).exists())
