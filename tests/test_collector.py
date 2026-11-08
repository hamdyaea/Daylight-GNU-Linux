#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
import http.client
import importlib.util
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest
spec = importlib.util.spec_from_file_location("collector", Path(__file__).resolve().parent.parent/"telemetry/collector.py")
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)
class Collector(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name)/"counts.sqlite3"
        collector.initialize(self.db)
        self.server = collector.Server(("127.0.0.1", 0), collector.handler(self.db))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
    def tearDown(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join(); self.temp.cleanup()
    def post(self, obj, path="/v1/boot"):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        connection.request("POST", path, body=json.dumps(obj), headers={"Content-Type": "application/json"})
        status = connection.getresponse().status; connection.close(); return status
    def get(self, path):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        connection.request("GET", path)
        status = connection.getresponse().status; connection.close(); return status
    def test_healthcheck(self):
        self.assertEqual(self.get("/healthz"),204)
        self.assertEqual(self.get("/"),404)
    def test_aggregate_only(self):
        event={"event":"boot", "version":"5.0.0-rc.1", "mode":"installed"}
        self.assertEqual(self.post(event),204); self.assertEqual(self.post(event),204)
        with sqlite3.connect(self.db) as db:
            self.assertEqual(db.execute("SELECT version,mode,boots FROM counts").fetchall(),[("5.0.0-rc.1","installed",2)])
            self.assertEqual([r[1] for r in db.execute("PRAGMA table_info(counts)")],["day","version","mode","boots"])
    def test_reject_identifiers(self):
        self.assertEqual(self.post({"event":"boot","version":"5.0.0","mode":"installed","id":"abc"}),400)
    def test_invalid(self):
        for event in [[],None,{"event":"boot","version":"5.0.0","mode":"unknown"},{"event":"boot","version":"bad","mode":"live"}]:
            self.assertEqual(self.post(event),400)
    def test_wrong_endpoint(self):
        self.assertEqual(self.post({},"/anything"),404)
if __name__ == "__main__": unittest.main(verbosity=2)
