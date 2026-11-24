"""Offline review of human-completed SiteScout form-verification CSV.

Statuses are self-reported evidence, NOT proof that a destination received a
test inquiry. No network calls, CRM access, persistence or outreach.
"""
import csv
import io

MAX_CSV_BYTES = 512_000
MAX_ROWS = 1000
MAX_CELL_CHARS = 4096
HEADERS = (
    "Page URL", "Form action", "Method", "Required fields", "Verification test",
    "Observed result", "Status", "Reviewer", "Notes",
)
STATUSES = {"Not tested", "Passed", "Failed", "Blocked"}


def review_checklist(text):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("A completed checklist CSV is required")
    if len(text.encode("utf-8")) > MAX_CSV_BYTES:
        raise ValueError("Checklist exceeds 500 KiB")
    reader = csv.DictReader(io.StringIO(text, newline=""), strict=True)
    if reader.fieldnames is None or tuple(reader.fieldnames) != HEADERS:
        raise ValueError("Unexpected CSV columns; use SiteScout's checklist template")
    counts = {status: 0 for status in STATUSES}
    follow_up = []
    total = 0
    try:
        for index, row in enumerate(reader, 2):
            total += 1
            if total > MAX_ROWS:
                raise ValueError("Checklist exceeds 1000 tests")
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"Checklist row {index} has missing or extra columns")
            if any(len(value) > MAX_CELL_CHARS for value in row.values()):
                raise ValueError(f"Checklist row {index} has an oversized cell")
            status = row["Status"].strip()
            if status not in STATUSES:
                raise ValueError(f"Checklist row {index} has an unsupported status")
            if not row["Page URL"].strip() or not row["Verification test"].strip():
                raise ValueError(f"Checklist row {index} lacks its page or test")
            if status != "Not tested" and (
                not row["Reviewer"].strip() or not row["Observed result"].strip()
            ):
                raise ValueError(f"Checklist row {index} requires reviewer and observed evidence")
            counts[status] += 1
            if status in ("Failed", "Blocked"):
                follow_up.append({
                    "row": index, "page": row["Page URL"], "test": row["Verification test"],
                    "status": status, "observed_result": row["Observed result"],
                    "notes": row["Notes"],
                })
    except csv.Error as exc:
        raise ValueError("Malformed checklist CSV") from exc
    if total == 0:
        raise ValueError("Checklist contains no test rows")
    return {
        "total_tests": total,
        "counts": {
            "not_tested": counts["Not tested"],
            "passed": counts["Passed"],
            "failed": counts["Failed"],
            "blocked": counts["Blocked"],
        },
        "follow_up": follow_up,
        "evidence_label": "Self-reported by the reviewer; not independently verified by SiteScout",
    }
