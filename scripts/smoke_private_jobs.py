"""Real Docker integration check for operator identity and SQLite volume sharing.

Uses synthetic local CI tokens and an offline fixture job; never fetches a URL.
"""
import json
import os
import time
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8087"
TOKEN = "sitescout-smoke-only-operator-token-1234567890"
OTHER_TOKEN = "sitescout-smoke-only-outsider-token-1234567890"


def call(path, token=None):
    headers = {"Authorization": "Bearer " + token} if token else {}
    request = urllib.request.Request(BASE + path, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=3) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as response:
        return response.code, json.loads(response.read())


def main():
    for _ in range(30):
        try:
            code, body = call("/health")
            if code == 200 and body["status"] == "ok":
                break
        except (OSError, ValueError):
            pass
        time.sleep(0.25)
    else:
        raise SystemExit("Authenticated smoke API never became ready")

    assert call("/api/jobs")[0] == 401
    assert call("/api/jobs", "invalid" * 8)[0] == 401
    status, payload = call("/api/jobs", TOKEN)
    assert status == 200
    jobs = payload["jobs"]
    assert len(jobs) == 1, "Shared worker-created fixture job is not visible"
    assert "url" not in jobs[0] and "actor" not in jobs[0]
    identifier = jobs[0]["id"]
    status, detail = call("/api/jobs/" + identifier, TOKEN)
    assert status == 200 and detail["job"]["id"] == identifier
    assert "url" not in detail["job"]
    assert call("/api/jobs/" + identifier + "/audit", TOKEN)[0] == 200
    assert call("/api/jobs", OTHER_TOKEN) == (200, {"jobs": []})
    assert call("/api/jobs/" + identifier, OTHER_TOKEN)[0] == 404
    assert call("/api/jobs/" + identifier + "/audit", OTHER_TOKEN)[0] == 404
    print("Private jobs Docker smoke passed: hashed operator identity, shared volume and owner isolation")


if __name__ == "__main__":
    main()
