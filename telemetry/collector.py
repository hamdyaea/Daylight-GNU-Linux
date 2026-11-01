#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: contact@daylightlinux.ch
# Copyright (C) 2026 Hamdy Abou El Anein
# SPDX-License-Identifier: GPL-3.0-only
"""Reference local collector: aggregate counts only; deploy behind audited HTTPS."""
import argparse
from collections import deque
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import sqlite3
import threading
import time

VERSION = re.compile(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}(?:-[A-Za-z0-9.]{1,16})?\Z")

def initialize(database: Path) -> None:
    database.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE IF NOT EXISTS counts(day TEXT NOT NULL, version TEXT NOT NULL, mode TEXT NOT NULL, boots INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(day, version, mode))")

def handler(database: Path):
    lock = threading.Lock()
    arrivals = deque()
    class Counter(BaseHTTPRequestHandler):
        server_version = "DaylightCounter"
        sys_version = ""
        protocol_version = "HTTP/1.0"
        def log_message(self, *_):
            # Never persist requester IP, headers, URL parameters or request bodies.
            pass
        def reply(self, code):
            self.send_response(code)
            self.send_header("Content-Length", "0")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
        def do_GET(self):
            self.reply(405)
        def do_POST(self):
            self.connection.settimeout(3)
            if self.path != "/v1/boot":
                self.reply(404); return
            if self.headers.get("Transfer-Encoding") or self.headers.get_content_type() != "application/json":
                self.reply(400); return
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self.reply(400); return
            if not 1 <= length <= 256:
                self.reply(413); return
            # Global, identifier-free safety limit. This cannot provide anti-fraud uniqueness.
            with lock:
                now = time.monotonic()
                while arrivals and arrivals[0] < now - 60:
                    arrivals.popleft()
                if len(arrivals) >= 300:
                    self.reply(429); return
                arrivals.append(now)
            try:
                raw = self.rfile.read(length)
                if len(raw) != length:
                    self.reply(400); return
                event = json.loads(raw)
                if not isinstance(event, dict) or set(event) != {"event", "version", "mode"}:
                    self.reply(400); return
                if event["event"] != "boot" or event["mode"] not in ("live", "installed") or not isinstance(event["version"], str) or not VERSION.fullmatch(event["version"]):
                    self.reply(400); return
                day = datetime.now(timezone.utc).date().isoformat()
                with sqlite3.connect(database, timeout=2) as connection:
                    connection.execute("INSERT INTO counts(day,version,mode,boots) VALUES(?,?,?,1) ON CONFLICT(day,version,mode) DO UPDATE SET boots=boots+1", (day, event["version"], event["mode"]))
                self.reply(204)
            except (ValueError, UnicodeError, TimeoutError, sqlite3.Error, OSError, TypeError):
                self.reply(400)
    return Counter

class Server(ThreadingHTTPServer):
    daemon_threads = True
    request_queue_size = 16
    def handle_error(self, request, client_address):
        # The default implementation logs client_address in exception reports.
        pass

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=Path("/var/lib/daylight-counter/counts.sqlite3"))
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--export", action="store_true")
    args = parser.parse_args()
    initialize(args.database)
    if args.export:
        with sqlite3.connect(args.database) as connection:
            records = [dict(zip(("day", "version", "mode", "boots"), row)) for row in connection.execute("SELECT day,version,mode,boots FROM counts ORDER BY day,version,mode")]
        print(json.dumps(records, indent=2))
        return
    if not 1 <= args.port <= 65535:
        parser.error("Port must be 1..65535")
    # Loopback only. TLS and all proxy/provider logging require a separate deployment audit.
    server = Server(("127.0.0.1", args.port), handler(args.database))
    try:
        server.serve_forever(poll_interval=1)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
