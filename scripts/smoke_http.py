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
    print("Docker HTTP smoke passed: homepage, health, jobs and capture default-off")


if __name__ == "__main__":
    main()
