#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Mirror the signed Daylight APT repository; publish metadata only after verified objects."""
import argparse
import datetime as dt
import gzip
import hashlib
import os
from pathlib import Path
import re
import subprocess
import tempfile
import urllib.request

def fetch(base, name):
    if not re.fullmatch(r"[A-Za-z0-9_./+~-]+", name) or ".." in Path(name).parts:
        raise ValueError("Invalid repository path")
    with urllib.request.urlopen(urllib.request.Request(base + "/" + name, headers={"User-Agent":"curl/8.0"}), timeout=60) as r:
        return r.read()

def verified_write(path, data, sha):
    if hashlib.sha256(data).hexdigest() != sha:
        raise ValueError("SHA256 mismatch: " + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(data)
    tmp.replace(path)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", default="https://daylightlinux.ch/apt")
    p.add_argument("--dest", type=Path, default=Path("/srv/daylight-mirror"))
    p.add_argument("--trusted-keyring", type=Path, required=True,
                   help="Pinned official Daylight signing key; obtain independently")
    a = p.parse_args()
    if not a.source.startswith("https://"):
        p.error("HTTPS source required")
    base = a.source.rstrip("/")
    dest = a.dest.resolve()
    if str(dest) == "/": p.error("Destination cannot be /")
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        for name in ("InRelease", "Release", "Release.gpg"):
            (t / name).write_bytes(fetch(base, "dists/daylight/" + name))
        subprocess.run(["gpgv", "--keyring", str(a.trusted_keyring), str(t/"Release.gpg"), str(t/"Release")], check=True)
        result = subprocess.run(["gpgv", "--keyring", str(a.trusted_keyring), "--output", str(t/"plain"), str(t/"InRelease")], check=True, capture_output=True)
        if (t/"plain").read_bytes() != (t/"Release").read_bytes():
            raise ValueError("InRelease differs from Release")
        release = (t/"Release").read_text()
        valid_until = re.search(r"^Valid-Until: (.+)$", release, re.M)
        if not valid_until: raise ValueError("Missing expiry")
        from email.utils import parsedate_to_datetime
        if parsedate_to_datetime(valid_until.group(1)) <= dt.datetime.now(dt.timezone.utc):
            raise ValueError("Expired APT metadata")
        checks = {}
        for line in release.split("SHA256:",1)[1].splitlines()[1:]:
            match = re.match(r"^ ([0-9a-f]{64})\s+\d+\s+(\S+)$", line)
            if match: checks[match.group(2)] = match.group(1)
        for arch in ("amd64", "arm64"):
            rel = f"main/binary-{arch}/Packages.gz"
            payload = fetch(base, "dists/daylight/" + rel)
            if rel not in checks: raise ValueError("Missing signed package index")
            verified_write(dest/"dists/daylight"/rel, payload, checks[rel])
            for block in gzip.decompress(payload).decode().split("\n\n"):
                if not block.strip(): continue
                fields = dict(line.split(": ", 1) for line in block.splitlines() if ": " in line and not line.startswith(" "))
                name, sha = fields["Filename"], fields["SHA256"]
                if not name.startswith("pool/") or ".." in Path(name).parts: raise ValueError("Unsafe filename")
                target = dest/name
                if target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest() == sha: continue
                verified_write(target, fetch(base, name), sha)
            for variant in ("Packages",):
                path = f"main/binary-{arch}/{variant}"
                if path in checks:
                    verified_write(dest/"dists/daylight"/path, fetch(base, "dists/daylight/"+path), checks[path])
        for name in ("Release.gpg", "Release", "InRelease"):
            path = dest/"dists/daylight"/name
            path.parent.mkdir(parents=True, exist_ok=True)
            temp = path.with_name(name+".tmp")
            temp.write_bytes((t/name).read_bytes())
            temp.replace(path)
        print("Mirror synchronized and verified:", dest)

if __name__ == "__main__": main()