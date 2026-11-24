"""Operator-only command-line interface for durable capture jobs.

Not an HTTP API. Execute inside a trusted, single-worker Docker host. This CLI
requires explicit capture enablement and never accepts credentials as args.
"""
import argparse
import json
import os
import sys
import time

from app.capture_jobs import CaptureJobStore, QueueFullError, RateLimitedError
from app.capture_worker import CaptureWorker
from app.capture import validate_target
from app.worker_lock import WorkerBusyError, exclusive_worker_lock

DEFAULT_DB = "/data/capture_jobs.sqlite3"
RETENTION_SECONDS = 7 * 24 * 60 * 60


def run(argv=None, *, store_factory=CaptureJobStore, worker_factory=CaptureWorker):
    parser = argparse.ArgumentParser(description="Private SiteScout capture worker")
    parser.add_argument("--database", default=os.environ.get("SITESCOUT_JOBS_DB", DEFAULT_DB))
    commands = parser.add_subparsers(dest="operation", required=True)
    submit = commands.add_parser("submit", help="Queue an authorized public HTTPS URL")
    submit.add_argument("--actor", required=True)
    submit.add_argument("--url", required=True)
    submit.add_argument("--mode", choices=("inventory", "directory"), default="inventory")
    submit.add_argument("--authorized", action="store_true", help="Operator confirms authorization")
    commands.add_parser("work-once", help="Execute one queued job, if present")
    recover = commands.add_parser("recover", help="Requeue stale jobs with exclusive worker lock")
    recover.add_argument("--older-than-seconds", type=int, default=120)
    listing = commands.add_parser("list", help="List operator-owned capture job metadata")
    listing.add_argument("--actor", required=True)
    listing.add_argument("--limit", type=int, default=25)
    status = commands.add_parser("status", help="Read a job as its authorized operator")
    status.add_argument("--actor", required=True)
    status.add_argument("--job-id", required=True)
    audit = commands.add_parser("audit", help="Read sanitized events for owned job")
    audit.add_argument("--actor", required=True)
    audit.add_argument("--job-id", required=True)
    prune = commands.add_parser("prune", help="Remove completed jobs past retention")
    prune.add_argument("--older-than-days", type=int, default=7)
    args = parser.parse_args(argv)

    if os.environ.get("SITESCOUT_CAPTURE_ENABLED") != "true":
        print("Capture is disabled; set SITESCOUT_CAPTURE_ENABLED=true on a trusted host", file=sys.stderr)
        return 3
    if args.operation == "submit":
        if not args.authorized:
            print("Explicit authorization confirmation required", file=sys.stderr)
            return 2
        # Prevent invalid targets from entering the durable queue.
        try:
            validate_target(args.url)
        except ValueError:
            print("Target must be an allowed public HTTPS URL", file=sys.stderr)
            return 2

    store = store_factory(args.database)
    try:
        if args.operation == "submit":
            identifier = store.enqueue(args.actor, args.url, args.mode)
            output = {"job_id": identifier, "status": "queued"}
        elif args.operation == "work-once":
            with exclusive_worker_lock(args.database):
                result = worker_factory(store).process_one()
            # Results can contain untrusted page data; never echo them in logs.
            output = {"job_id": result["id"], "status": result["status"]} if result else {"status": "empty"}
        elif args.operation == "recover":
            if args.older_than_seconds < 60:
                print("Recovery threshold must be at least 60 seconds", file=sys.stderr)
                return 2
            with exclusive_worker_lock(args.database):
                recovered = store.recover_stale(before=time.time() - args.older_than_seconds)
            output = {"requeued": recovered}
        elif args.operation == "list":
            output = {"jobs": store.list_for_actor(args.actor, limit=args.limit)}
        elif args.operation == "status":
            job = store.get(args.job_id, args.actor)
            if job is None:
                print("Job not found", file=sys.stderr)
                return 4
            output = {key: job[key] for key in ("id", "status", "mode", "created_at", "updated_at", "error")}
        elif args.operation == "audit":
            if store.get(args.job_id, args.actor) is None:
                print("Job not found", file=sys.stderr)
                return 4
            output = {"events": store.audit(args.job_id, args.actor)}
        else:
            if args.older_than_days < 1:
                print("Retention must be at least one day", file=sys.stderr)
                return 2
            removed = store.prune(older_than=time.time() - args.older_than_days * 86400)
            output = {"removed": removed}
    except WorkerBusyError:
        print("Another capture worker is active", file=sys.stderr)
        return 7
    except RateLimitedError:
        print("Actor rate limit exceeded", file=sys.stderr)
        return 5
    except QueueFullError:
        print("Queue capacity reached", file=sys.stderr)
        return 6
    except ValueError:
        print("Invalid capture job parameters", file=sys.stderr)
        return 2

    print(json.dumps(output, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
