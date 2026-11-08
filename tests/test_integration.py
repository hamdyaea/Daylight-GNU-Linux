#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
ROOT = Path(__file__).resolve().parent.parent
BINARY = Path(os.environ.get("DAYLIGHT_BINARY", ROOT / "target/x86_64-unknown-linux-musl/release/daylight"))

class CLI(unittest.TestCase):
    def run_cli(self, *args, ok=True, env=None):
        result = subprocess.run([str(BINARY), *args], capture_output=True, text=True, timeout=15, env=env)
        self.assertEqual(result.returncode == 0, ok, result.stderr)
        return result.stdout
    def test_version(self):
        self.assertIn("5.0.0-rc.3", self.run_cli("--version"))
    def test_status_is_valid_json(self):
        data = json.loads(self.run_cli("status", "--json"))
        self.assertGreater(data["memory_total_kib"], 0)
        for prohibited in ("hostname", "ip", "mac", "serial", "username", "installation_id"):
            self.assertNotIn(prohibited, data)
    def test_password_not_logged(self):
        out = self.run_cli("password", "32", "3").splitlines()
        self.assertEqual([len(p) for p in out], [32, 32, 32])
        self.assertEqual(len(set(out)), 3)
    def test_invalid_input(self):
        for args in [("password", "2"), ("password", "10000000"), ("temperature", "NaN", "C"), ("days", "2025-02-29"), ("games", "dice", "0"), ("connect", "--check", "a;touch /tmp/no"), ("remove", "--yes"), ("monitor", "--interval", "0"), ("unknown",)]:
            self.run_cli(*args, ok=False)
    def test_calendar(self):
        self.assertEqual(self.run_cli("days", "2000-01-01", "2001-01-01").strip(), "366")
    def test_converter(self):
        self.assertIn("212.00 F", self.run_cli("temperature", "100", "C"))
    def test_monitor_json(self):
        lines = self.run_cli("monitor", "--watch", "--json", "--interval", "0.2", "--count", "2").splitlines()
        self.assertEqual(len(lines), 2)
        self.assertIsNone(json.loads(lines[0])["cpu_percent"])
        self.assertIsInstance(json.loads(lines[1])["cpu_percent"], (int, float))
    def test_telemetry_default(self):
        self.assertIn("disabled", self.run_cli("telemetry", "status"))
        self.assertEqual(self.run_cli("telemetry", "send"), "")
    def test_settings_are_isolated(self):
        if os.geteuid() == 0:
            self.skipTest("Desktop writes deliberately reject root")
        with tempfile.TemporaryDirectory() as temporary:
            env = dict(os.environ, XDG_CONFIG_HOME=temporary)
            sentinel = Path(temporary)/"existing.conf"
            sentinel.write_text("unchanged")
            self.run_cli("settings", "set", "profile", "minimal", env=env)
            self.assertEqual(self.run_cli("settings", "get", "profile", env=env).strip(), "minimal")
            self.assertEqual(sentinel.read_text(), "unchanged")
            self.run_cli("settings", "set", "wallpaper", "../../etc/shadow", env=env, ok=False)
    def test_no_network_for_local_connect(self):
        self.assertIn("No external request", self.run_cli("connect"))
    def test_unknown_app_errors(self):
        self.run_cli("app", "does-not-exist", ok=False)

if __name__ == "__main__":
    unittest.main(verbosity=2)
