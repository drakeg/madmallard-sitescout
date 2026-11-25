"""Smoke the default-off Docker HTTP routes against a live local container."""
import json
import time
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8087"


def request(path, data=None):
    payload = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(
        BASE + path, data=payload,
        headers={"Content-Type": "application/json"} if payload else {},
    )
    try:
        with urllib.request.urlopen(req, timeout=3) as response:
            return response.status, response.read().decode()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode()


def main():
    for attempt in range(30):
        try:
            code, body = request("/health")
            if code == 200 and json.loads(body)["status"] == "ok":
                break
        except (OSError, ValueError):
            pass
        time.sleep(0.25)
    else:
        raise SystemExit("Container health route never became ready")

    code, body = request("/")
    assert code == 200 and "Mad Mallard SiteScout" in body, "Dashboard missing"
    for path, payload in (
        ("/api/jobs", None),
        ("/api/capture", {"url": "https://example.org"}),
    ):
        code, body = request(path, payload)
        assert code == 403, f"{path} should be default-off, received {code}"
        assert "disabled" in json.loads(body)["error"].lower()
    pages = [
        {"url": "https://example.org/", "html": '<h1>Home</h1><a href="/contact">Contact</a>'},
        {"url": "https://example.org/contact", "html":
         '<h1>Contact</h1><form method="post" action="/submit"><input name="email" required></form>'},
    ]
    code, body = request("/api/site_report", pages)
    assert code == 200, f"Offline site report returned {code}"
    report = json.loads(body)["report"]
    assert report["page_count"] == 2
    assert report["candidate_contact_booking_pages"] == ["https://example.org/contact"]
    assert report["functional_requirements"]["forms_to_test"][0]["verified_functional"] is False
    code, body = request("/api/site_report", {"not": "a page list"})
    assert code == 400 and "error" in json.loads(body)
    # Exercise the public CSV contract without importing app through script-relative sys.path.
    headers=["Page URL", "Form action", "Method", "Required fields",
             "Verification test", "Observed result", "Status", "Reviewer", "Notes"]
    import csv
    import io
    csv_stream=io.StringIO(newline="")
    writer=csv.writer(csv_stream)
    writer.writerow(headers)
    writer.writerow(["https://example.org/contact", "/send", "POST", "email",
                     "Submit synthetic inquiry", "", "Not tested", "", ""])
    code, body = request("/api/checklist_review", {"csv": csv_stream.getvalue()})
    assert code == 200, f"Offline checklist review returned {code}"
    review=json.loads(body)["review"]
    assert review["counts"]["not_tested"] == 1
    assert "not independently verified" in review["evidence_label"]

    remediation_headers=["Priority","Finding","Page URL","Observed evidence",
        "Recommended fix","Manual verification","Review status","Assigned to","Evidence link","Notes"]
    review_csv=io.StringIO(newline="")
    remediation_writer=csv.writer(review_csv)
    remediation_writer.writerow(remediation_headers)
    remediation_writer.writerow(["high","missing-title","https://example.org/","No HTML title",
        "Add title","Inspect browser title","Needs review","","",""])
    code, body = request("/api/remediation_review", {"csv": review_csv.getvalue()})
    assert code == 200, f"Remediation review returned {code}"
    remediation=json.loads(body)["review"]
    assert remediation["counts"]["needs_review"] == 1
    assert "not independently verified" in remediation["evidence_label"]

    print("Docker HTTP smoke passed: homepage, health, offline site report and capture default-off")


if __name__ == "__main__":
    main()
