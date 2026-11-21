#!/usr/bin/env python3
"""Check every deployed Daylight Web Live payload against the pinned manifest."""
import hashlib
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = "https://daylightlinux.ch/live/"
ROOT = Path(__file__).resolve().parent
expected = json.loads((ROOT / "published-runtime.json").read_text())
failures = []
def download(name, max_bytes):
    req = Request(BASE + name, headers={"User-Agent": "Daylight-Web-Live-Asset-Check/1"})
    with urlopen(req, timeout=35) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}")
        data = response.read(max_bytes + 1)
        if len(data) > max_bytes:
            raise RuntimeError("oversized response")
        return data

try:
    public = json.loads(download("manifest.json", 65536))
    if public != expected:
        failures.append("Public manifest differs from pinned source manifest")
except (HTTPError, URLError, ValueError, RuntimeError) as exc:
    failures.append(f"manifest.json: {exc}")
for name, record in expected["files"].items():
    filename = record.get("file", name)
    try:
        data = download(filename, record["bytes"])
        if len(data) != record["bytes"]:
            raise RuntimeError(f"size mismatch: {len(data)} != {record['bytes']}")
        digest = hashlib.sha256(data).hexdigest()
        if digest != record["sha256"]:
            raise RuntimeError("SHA256 mismatch")
        print(f"PASS {name} => {filename} ({len(data)} bytes)")
    except (HTTPError, URLError, RuntimeError) as exc:
        failures.append(f"{name} => {filename}: {exc}")
for issue in failures:
    print("FAIL " + issue)
if failures:
    raise SystemExit(1)
print("PASS: all six public runtime assets match the pinned manifest")
