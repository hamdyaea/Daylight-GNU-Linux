#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Validate opt-in mirror registry; publish only stable, current HTTPS mirrors."""
import argparse
import datetime as dt
import json
from pathlib import Path
import urllib.request
from urllib.parse import urlparse

UTC = dt.timezone.utc

def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "curl/8.0 DaylightMirrorHealth/1"})
    with urllib.request.urlopen(request, timeout=12) as response:
        return response.read(2_000_000)

def run(source, state_path, public_path, now):
    source_release = fetch(source.rstrip("/") + "/dists/daylight/InRelease")
    entries = json.loads(state_path.read_text()) if state_path.exists() else []
    updated, public = [], []
    for entry in entries:
        url = entry["url"].rstrip("/")
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.port:
            continue
        healthy = False
        try:
            healthy = fetch(url + "/dists/daylight/InRelease") == source_release
        except (OSError, ValueError):
            pass
        if healthy:
            entry["last_seen"] = now.isoformat()
            entry["healthy_since"] = entry.get("healthy_since") or now.isoformat()
            entry["failures"] = 0
        else:
            entry["healthy_since"] = None
            entry["failures"] = entry.get("failures", 0) + 1
        if healthy and (now - dt.datetime.fromisoformat(entry["healthy_since"])).total_seconds() >= 86400:
            public.append({"url": url, "country": entry.get("country", ""), "name": entry.get("name", url), "last_seen": entry["last_seen"]})
        updated.append(entry)
    for path, value in ((state_path, updated), (public_path, public)):
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(value, indent=2) + "\n")
        tmp.replace(path)

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", default="https://daylightlinux.ch/apt")
    p.add_argument("--registry", type=Path, required=True)
    p.add_argument("--public", type=Path, required=True)
    args = p.parse_args()
    run(args.source, args.registry, args.public, dt.datetime.now(UTC))