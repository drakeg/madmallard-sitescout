"""Opt-in Docker-only public HTTPS capture with DNS pinning and no redirects."""
import http.client
import ipaddress
import socket
import ssl
from urllib.parse import urlsplit

MAX_CAPTURE_BYTES = 512_000

def validate_target(url, resolver=socket.getaddrinfo):
    if not isinstance(url, str) or len(url) > 2048:
        raise ValueError("A valid HTTPS URL is required")
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.port not in (None, 443):
        raise ValueError("Only public HTTPS URLs on port 443 are allowed")
    host = parsed.hostname
    if host.endswith(".") or not host.isascii() or "." not in host:
        raise ValueError("A public DNS hostname is required")
    try:
        ipaddress.ip_address(host)
        raise ValueError("IP literal targets are not allowed")
    except ValueError as exc:
        if str(exc) == "IP literal targets are not allowed":
            raise
    try:
        addresses = resolver(host, 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError("DNS lookup failed") from exc
    ips = {item[4][0] for item in addresses}
    if not ips or any(not ipaddress.ip_address(ip).is_global for ip in ips):
        raise ValueError("Private, reserved, or non-public addresses are blocked")
    return parsed, sorted(ips)[0]

class PinnedHTTPSConnection(http.client.HTTPSConnection):
    def __init__(self, host, ip, timeout):
        super().__init__(host, port=443, timeout=timeout, context=ssl.create_default_context())
        self.pinned_ip = ip

    def connect(self):
        raw = socket.create_connection((self.pinned_ip, 443), self.timeout)
        try:
            self.sock = self._context.wrap_socket(raw, server_hostname=self.host)
        except Exception:
            raw.close()
            raise

def capture(url):
    parsed, ip = validate_target(url)
    connection = PinnedHTTPSConnection(parsed.hostname, ip, timeout=8)
    try:
        path = parsed.path or "/"
        if parsed.query:
            path += "?" + parsed.query
        connection.request("GET", path, headers={"User-Agent": "MadMallardSiteScout/0.1 (authorized inspection)", "Accept": "text/html", "Accept-Encoding": "identity", "Connection": "close"})
        response = connection.getresponse()
        if response.status != 200:
            raise ValueError(f"Target returned HTTP {response.status}; redirects are not followed")
        if "text/html" not in response.getheader("Content-Type", "").lower():
            raise ValueError("Target did not return HTML")
        size = response.getheader("Content-Length")
        if size and int(size) > MAX_CAPTURE_BYTES:
            raise ValueError("Target HTML exceeds 500 KiB")
        data = response.read(MAX_CAPTURE_BYTES + 1)
        if len(data) > MAX_CAPTURE_BYTES:
            raise ValueError("Target HTML exceeds 500 KiB")
        return data.decode("utf-8", errors="replace")
    finally:
        connection.close()
