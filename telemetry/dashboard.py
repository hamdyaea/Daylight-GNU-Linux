#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Loopback-only HTTP dashboard for aggregate Daylight boot telemetry."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path

MIME = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
}

def make_handler(data_file: Path, static_dir: Path):
    class Dashboard(BaseHTTPRequestHandler):
        server_version = "DaylightTelemetry"
        sys_version = ""
        def log_message(self, *_):
            # Do not write visitor addresses, identity headers, paths or user agents.
            pass
        def reply(self, status, body=b"", content_type="application/json; charset=utf-8"):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'")
            self.end_headers()
            if body and self.command != "HEAD":
                self.wfile.write(body)
        def do_GET(self):
            if self.path == "/healthz":
                self.reply(204)
                return
            if self.path == "/api/metrics":
                try:
                    data = json.loads(data_file.read_text(encoding="utf-8"))
                    if not isinstance(data, dict) or not isinstance(data.get("records"), list):
                        raise ValueError("invalid snapshot")
                    body = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode()
                except (OSError, ValueError, UnicodeError):
                    self.reply(503, b'{"error":"snapshot unavailable"}')
                    return
                self.reply(200, body)
                return
            asset = MIME.get(self.path)
            if asset is None:
                self.reply(404, b"Not found", "text/plain; charset=utf-8")
                return
            name, content_type = asset
            try:
                body = (static_dir / name).read_bytes()
            except OSError:
                self.reply(503, b"Dashboard asset unavailable", "text/plain; charset=utf-8")
                return
            self.reply(200, body, content_type)
        def do_HEAD(self):
            self.do_GET()
    return Dashboard

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("/var/backups/daylight-telemetry/counts.json"))
    parser.add_argument("--static-dir", type=Path, default=Path("/usr/local/share/daylight-telemetry-dashboard"))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8788)
    args = parser.parse_args()
    if args.host not in ("127.0.0.1", "::1") or not 1 <= args.port <= 65535:
        parser.error("The dashboard must use a loopback address and a valid port")
    server = ThreadingHTTPServer((args.host, args.port), make_handler(args.data, args.static_dir))
    try:
        server.serve_forever(poll_interval=1)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    main()