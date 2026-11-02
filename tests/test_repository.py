#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Validate the repository builder without using an existing key or changing APT."""
import gzip
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent


class SignedRepository(unittest.TestCase):
    def test_signed_indexes_and_tamper_detection(self):
        if any(shutil.which(c) is None for c in ("gpg", "gpgv", "gpgconf", "dpkg-scanpackages")):
            self.skipTest("GnuPG and dpkg-scanpackages are required")
        if len(list((ROOT / "dist").glob("daylight-*.deb"))) != 8:
            self.skipTest("Build the eight AMD64/ARM64/data packages first")
        with tempfile.TemporaryDirectory(prefix="daylight-signing-test-") as temporary:
            base = Path(temporary)
            home = base / "gnupg"
            home.mkdir(mode=0o700)
            env = dict(os.environ, GNUPGHOME=str(home), LC_ALL="C")

            def run(*args, check=True):
                return subprocess.run(args, env=env, text=True, capture_output=True,
                                      timeout=90, check=check)

            try:
                run("gpg", "--batch", "--pinentry-mode", "loopback", "--passphrase", "",
                    "--quick-generate-key", "Disposable Daylight CI key <ci@example.invalid>",
                    "ed25519", "sign", "1d")
                public = run("gpg", "--batch", "--with-colons", "--list-keys").stdout
                fingerprint = next(line.split(":")[9] for line in public.splitlines() if line.startswith("fpr:"))
                repository = base / "repository"
                run("python3", str(ROOT / "scripts/build-apt-repository.py"),
                    "--packages", str(ROOT / "dist"), "--output", str(repository),
                    "--signing-key", fingerprint)
                keyring = repository / "daylight-archive-keyring.gpg"
                release = repository / "dists/daylight/InRelease"
                self.assertEqual(run("gpgv", "--keyring", str(keyring), str(release)).returncode, 0)
                for arch in ("amd64", "arm64"):
                    index = repository / f"dists/daylight/main/binary-{arch}/Packages"
                    data = index.read_bytes()
                    self.assertEqual(gzip.decompress(index.with_name("Packages.gz").read_bytes()), data)
                    records = [dict(line.split(": ", 1) for line in block.splitlines()
                                    if ": " in line and not line.startswith(" "))
                               for block in data.decode().strip().split("\n\n")]
                    self.assertEqual(len(records), 7)
                    self.assertEqual({p["Architecture"] for p in records}, {arch, "all"})
                    for package in records:
                        payload = (repository / package["Filename"]).read_bytes()
                        self.assertEqual(hashlib.sha256(payload).hexdigest(), package["SHA256"])
                bad = base / "tampered.InRelease"
                bad.write_text(release.read_text().replace("Origin: Daylight GNU/Linux", "Origin: Tampered"))
                self.assertNotEqual(run("gpgv", "--keyring", str(keyring), str(bad), check=False).returncode, 0)
            finally:
                run("gpgconf", "--kill", "all", check=False)
        # TemporaryDirectory removes only the newly created disposable key and repository.


if __name__ == "__main__":
    unittest.main(verbosity=2)
