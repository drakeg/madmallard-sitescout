import tempfile
import threading
import unittest
from pathlib import Path

from app.worker_lock import WorkerBusyError, exclusive_worker_lock


class ExclusiveWorkerLockTests(unittest.TestCase):
    def test_rejects_second_worker_until_first_releases(self):
        with tempfile.TemporaryDirectory() as tmp:
            database = Path(tmp) / "capture.sqlite3"
            with exclusive_worker_lock(database):
                with self.assertRaises(WorkerBusyError):
                    with exclusive_worker_lock(database):
                        pass
            with exclusive_worker_lock(database):
                self.assertTrue((Path(str(database) + ".worker.lock")).exists())

    def test_second_thread_cannot_acquire_while_worker_active(self):
        with tempfile.TemporaryDirectory() as tmp:
            database = Path(tmp) / "capture.sqlite3"
            outcomes = []
            with exclusive_worker_lock(database):
                def contend():
                    try:
                        with exclusive_worker_lock(database):
                            outcomes.append("entered")
                    except WorkerBusyError:
                        outcomes.append("busy")
                worker = threading.Thread(target=contend)
                worker.start()
                worker.join()
            self.assertEqual(outcomes, ["busy"])
