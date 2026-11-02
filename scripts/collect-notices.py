#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Preserve the complete standard-library notices of the pinned Rust toolchain."""
from pathlib import Path
import subprocess
import urllib.request

root = Path(__file__).resolve().parent.parent
sysroot = Path(subprocess.check_output(["rustup", "run", "1.88.0", "rustc", "--print", "sysroot"], text=True).strip())
local = sysroot / "share/doc/rust/COPYRIGHT-library.html"
if local.is_file():
    content = local.read_bytes()
else:
    with urllib.request.urlopen("https://doc.rust-lang.org/1.88.0/COPYRIGHT-library.html", timeout=30) as response:
        content = response.read()
if b"Rust Standard Library" not in content or len(content) < 10000:
    raise SystemExit("Unexpected Rust notice document; refusing incomplete packaging")
(root / "licenses").mkdir(exist_ok=True)
(root / "licenses/RUST-STANDARD-LIBRARY.html").write_bytes(content)
print("Rust standard-library notices preserved.")
