#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Unit tests for the community mirror publication policy."""
import datetime as dt
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("mirror_health", Path(__file__).resolve().parents[1] / "scripts/daylight-mirror-health.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
UTC = dt.timezone.utc

class MirrorHealthTests(unittest.TestCase):
    def test_requires_full_day_and_hides_failures(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "registry.json"
            public = Path(directory) / "public.json"
            state.write_text(json.dumps([{"url": "https://mirror.example.org", "country": "CH", "name": "Example"}]))
            first = dt.datetime(2026, 11, 10, 10, tzinfo=UTC)
            with patch.object(module, "fetch", return_value=b"signed-release"):
                module.run("https://daylightlinux.ch/apt", state, public, first)
                self.assertEqual(json.loads(public.read_text()), [])
                module.run("https://daylightlinux.ch/apt", state, public, first + dt.timedelta(hours=24))
                self.assertEqual(len(json.loads(public.read_text())), 1)
            def failing(url):
                if "mirror.example.org" in url: raise OSError("offline")
                return b"signed-release"
            with patch.object(module, "fetch", side_effect=failing):
                module.run("https://daylightlinux.ch/apt", state, public, first + dt.timedelta(hours=24, minutes=15))
            self.assertEqual(json.loads(public.read_text()), [])
            self.assertEqual(json.loads(state.read_text())[0]["failures"], 1)

if __name__ == "__main__":
    unittest.main()
