"""Opt-in single-host capture queue runner.

Only starts when capture is explicitly enabled by the operator. Uses the
existing exclusive file lock for each job and never performs automatic
stale-job recovery.
"""
import time

from app.capture_worker import CaptureWorker
from app.worker_lock import WorkerBusyError, exclusive_worker_lock


def run_worker_loop(store, database, *, stop=None, sleep=time.sleep,
                    interval=3.0, worker_factory=CaptureWorker,
                    max_cycles=None):
    """Drain queued work one job per lock, sleeping when idle or lock busy.

    max_cycles is for deterministic tests and operator diagnostics. No retries
    are scheduled automatically for failed jobs.
    """
    if not 1 <= interval <= 60:
        raise ValueError("Poll interval must be between 1 and 60 seconds")
    if max_cycles is not None and (not isinstance(max_cycles, int) or max_cycles < 1):
        raise ValueError("Max cycles must be a positive integer")
    cycles = 0
    while max_cycles is None or cycles < max_cycles:
        if stop is not None and stop():
            return cycles
        try:
            with exclusive_worker_lock(database):
                worker_factory(store).process_one()
        except WorkerBusyError:
            # Another single-host worker owns the shared lock.
            pass
        cycles += 1
        if max_cycles is None or cycles < max_cycles:
            sleep(interval)
    return cycles
