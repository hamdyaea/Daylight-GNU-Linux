#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: contact@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Create a signed APT repository using an explicitly selected owner-controlled key."""
import argparse
from datetime import datetime, timedelta, timezone
import gzip
import hashlib
from pathlib import Path
import re
import shutil
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packages", type=Path, default=Path("dist"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--signing-key", required=True, help="Full fingerprint of an existing release-signing key")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Fa-f0-9]{40}|[A-Fa-f0-9]{64}", args.signing_key):
        parser.error("Use a complete key fingerprint")
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        parser.error("Output directory must be empty; existing repositories are never overwritten")
    output.mkdir(parents=True, exist_ok=True)
    pool = output / "pool/main/d/daylight"
    pool.mkdir(parents=True)
    packages = sorted(args.packages.glob("daylight-*.deb"))
    if not packages:
        parser.error("No Daylight packages found")
    for package in packages:
        shutil.copyfile(package, pool / package.name)
    suite = output / "dists/daylight"
    for arch in ("amd64", "arm64"):
        dest = suite / f"main/binary-{arch}"
        dest.mkdir(parents=True)
        records = subprocess.check_output(["dpkg-scanpackages", "--arch", arch, "pool"], cwd=output)
        (dest / "Packages").write_bytes(records)
        (dest / "Packages.gz").write_bytes(gzip.compress(records, mtime=0))
    now = datetime.now(timezone.utc)
    fmt = "%a, %d %b %Y %H:%M:%S +0000"
    release = "Origin: Daylight GNU/Linux\nLabel: Daylight GNU/Linux\nSuite: daylight\nCodename: daylight\nArchitectures: amd64 arm64\nComponents: main\n"
    release += f"Date: {now.strftime(fmt)}\nValid-Until: {(now + timedelta(days=30)).strftime(fmt)}\nDescription: Daylight GNU/Linux packages\nSHA256:\n"
    for item in sorted(suite.rglob("Packages*")):
        data = item.read_bytes()
        release += f" {hashlib.sha256(data).hexdigest()} {len(data)} {item.relative_to(suite)}\n"
    (suite / "Release").write_text(release)
    key = args.signing_key.upper()
    subprocess.run(["gpg", "--batch", "--local-user", key, "--digest-algo", "SHA256", "--clearsign", "--output", str(suite / "InRelease"), str(suite / "Release")], check=True)
    subprocess.run(["gpg", "--batch", "--local-user", key, "--digest-algo", "SHA256", "--armor", "--detach-sign", "--output", str(suite / "Release.gpg"), str(suite / "Release")], check=True)
    with (output / "daylight-archive-keyring.gpg").open("wb") as keyfile:
        subprocess.run(["gpg", "--export", key], stdout=keyfile, check=True)
    subprocess.run(["gpgv", "--keyring", str(output / "daylight-archive-keyring.gpg"), str(suite / "InRelease")], check=True)
    print("Signed repository created locally:", output)
    print("Publish atomically over HTTPS after reviewing the key fingerprint. No server was modified.")


if __name__ == "__main__":
    main()
