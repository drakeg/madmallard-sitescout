"""Verify LAN dashboard binding and default-off sensitive controls in Compose.

This intentionally inspects generated Compose configuration rather than regex
matching YAML. Capture/worker profiles must never publish additional ports.
"""
import json
import os
import subprocess


def main():
    env = os.environ.copy()
    env["SITESCOUT_BIND"] = "0.0.0.0"
    env["SITESCOUT_CAPTURE_ENABLED"] = "false"
    env["SITESCOUT_JOBS_ENABLED"] = "false"
    command = ["docker", "compose", "--profile", "capture-worker",
               "--profile", "capture-runner", "config", "--format", "json"]
    config = json.loads(subprocess.check_output(command, env=env, text=True))
    services = config["services"]
    api = services["api"]
    ports = api["ports"]
    assert len(ports) == 1, "Only the dashboard API should publish a port"
    assert ports[0]["host_ip"] == "0.0.0.0", "Dashboard should be reachable on trusted LAN"
    assert str(ports[0]["target"]) == "8080"
    assert api["environment"]["SITESCOUT_CAPTURE_ENABLED"] == "false"
    assert api["environment"]["SITESCOUT_JOBS_ENABLED"] == "false"
    for name in ("capture-worker", "capture-runner"):
        assert not services[name].get("ports"), f"{name} must not publish ports"
        assert services[name]["environment"]["SITESCOUT_CAPTURE_ENABLED"] == "false"
    print("Compose network gate passed: LAN dashboard, no public worker ports, capture default-off")


if __name__ == "__main__":
    main()
