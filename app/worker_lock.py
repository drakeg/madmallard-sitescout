"""Exclusive flock for single-host trusted capture workers.

This only coordinates processes sharing the SAME filesystem. It does not
replace distributed leases or fencing across networked storage/hosts.
"""
import fcntl
from contextlib import contextmanager
from pathlib import Path


class WorkerBusyError(Exception):
    pass


@contextmanager
def exclusive_worker_lock(database):
    path = Path(str(database) + ".worker.lock")
    path.parent.mkdir(parents=True, exist_ok=True)
    # Lock file must remain on the persistent SQLite filesystem.
    with path.open("a+b") as handle:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise WorkerBusyError("Another capture worker is already active") from exc
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
