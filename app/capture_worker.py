"""One-job-at-a-time, dependency-injected execution for a private capture worker.

Not connected to HTTP and not a scheduler. Callers must supply an authorized
worker environment and retain a single active worker for stale-job recovery.
"""
from app.analyze import analyze
from app.capture import capture


class CaptureWorker:
    def __init__(self, store, fetch=capture, evaluate=analyze, save=None):
        self.store = store
        self.fetch = fetch
        self.evaluate = evaluate
        self.save = save

    def process_one(self):
        """Process one queued job; results are deliberately not persisted."""
        job = self.store.claim()
        if job is None:
            return None
        try:
            html = self.fetch(job["url"])
            result = self.evaluate({
                "url": job["url"],
                "mode": job["mode"],
                "html": html,
            })
        except (ValueError, OSError, TimeoutError, UnicodeError):
            self.store.complete(job["id"], False)
            return {"id": job["id"], "status": "failed"}
        except Exception:
            # A programming error still leaves an auditable failed record,
            # but must propagate for process-level alerting and inspection.
            self.store.complete(job["id"], False)
            raise
        if self.save is not None:
            try:
                self.save(job["id"], result)
            except (ValueError, OSError):
                self.store.complete(job["id"], False)
                return {"id": job["id"], "status": "failed"}
        self.store.complete(job["id"], True)
        return {"id": job["id"], "status": "succeeded", "result": result}
