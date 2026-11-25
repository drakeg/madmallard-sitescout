"""Offline review of a human-updated SiteScout remediation action CSV.

Statuses are operator attestations, not proof of live deployment, technical
verification, accessibility compliance, or resolved customer impact.
"""
import csv
import io

MAX_BYTES = 512_000
MAX_ROWS = 1000
MAX_CELL = 4096
HEADERS = ("Priority", "Finding", "Page URL", "Observed evidence", "Recommended fix",
           "Manual verification", "Review status", "Assigned to", "Evidence link", "Notes")
STATES = ("Needs review", "In progress", "Implemented", "Deferred")


def review_remediation_csv(contents):
    if not isinstance(contents, str) or not contents.strip():
        raise ValueError("An action-plan CSV is required")
    if len(contents.encode("utf-8")) > MAX_BYTES:
        raise ValueError("Action plan exceeds 500 KiB")
    reader = csv.DictReader(io.StringIO(contents, newline=""), strict=True)
    if tuple(reader.fieldnames or ()) != HEADERS:
        raise ValueError("Unexpected action plan columns")
    counts = {state: 0 for state in STATES}
    follow_up = []
    total = 0
    try:
        for number, row in enumerate(reader, start=2):
            total += 1
            if total > MAX_ROWS:
                raise ValueError("Too many action-plan rows")
            if None in row or any(value is None or len(value) > MAX_CELL for value in row.values()):
                raise ValueError("Invalid action-plan row shape or size")
            state = row["Review status"].strip()
            if state not in counts:
                raise ValueError("Unsupported review status")
            if not row["Page URL"].strip() or not row["Finding"].strip() or not row["Recommended fix"].strip():
                raise ValueError("Action row is missing its finding details")
            if state != "Needs review" and not row["Assigned to"].strip():
                raise ValueError("Assigned owner is required after triage")
            if state == "Implemented" and (not row["Evidence link"].strip() or not row["Notes"].strip()):
                raise ValueError("Implementation requires evidence reference and review notes")
            if state == "Deferred" and not row["Notes"].strip():
                raise ValueError("Deferral requires documented rationale")
            counts[state] += 1
            if state in ("Needs review", "In progress", "Deferred"):
                follow_up.append({
                    "row": number, "priority": row["Priority"],
                    "finding": row["Finding"], "page": row["Page URL"],
                    "status": state, "assigned_to": row["Assigned to"],
                    "notes": row["Notes"],
                })
    except csv.Error as exc:
        raise ValueError("Malformed action-plan CSV") from exc
    if total == 0:
        raise ValueError("Action plan contains no review rows")
    return {
        "total": total,
        "counts": {
            "needs_review": counts["Needs review"],
            "in_progress": counts["In progress"],
            "implemented": counts["Implemented"],
            "deferred": counts["Deferred"],
        },
        "follow_up": follow_up,
        "evidence_label": "Self-reported progress; implementation and live effectiveness not independently verified",
    }
