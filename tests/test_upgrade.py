#!/usr/bin/env python3
"""Prepare historical packages and run the update-only integration test.

This helper creates an isolated historical source checkout and compiles the RC3
Rust executable, or downloads the immutable, hash-verified public RC4 packages.
It does not alter the working tree, install packages, or use the
production signing key. The actual upgrade runs only inside a disposable Docker
container through scripts/test-upgrade.sh.

Developer: Hamdy Abou El Anein — GPL-3.0-only.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
RC3_SOURCE = "017360374eb60773be2c98ccff1c09b65557aac7"
RC4_SOURCE = "f7d1e02f8eb326cadeb8368ead5cc64d2d2c1050"
TRIPLES = {"amd64": "x86_64-unknown-linux-musl", "arm64": "aarch64-unknown-linux-musl"}


def run(*arguments, **kwargs):
    return subprocess.run(arguments, check=True, **kwargs)


def prepare_public_rc4(output, arch):
    """Exercise the bits existing users received, never rebuild or replace them."""
    manifest = json.loads((ROOT / "release/rc4-packages.json").read_text())
    if manifest["source_commit"] != RC4_SOURCE or manifest["package_version"] != "5.0.0~rc4":
        raise RuntimeError("The immutable public RC4 manifest changed")
    packages = {name: checksum for name, checksum in manifest["packages"].items()
                if name.endswith((f"_{arch}.deb", "_all.deb"))}
    if len(packages) != 7:
        raise RuntimeError("Expected one public RC4 core plus six data packages")
    for name, checksum in sorted(packages.items()):
        url = manifest["apt_url"].rstrip("/") + "/pool/main/d/daylight/" + name
        request = urllib.request.Request(url, headers={"User-Agent": "DaylightLinux-upgrade-integration/1.0"})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    data = response.read()
                break
            except (OSError, urllib.error.URLError):
                if attempt == 2:
                    raise
                time.sleep(2)
        if hashlib.sha256(data).hexdigest() != checksum:
            raise RuntimeError("Published RC4 checksum mismatch: " + name)
        (output / name).write_bytes(data)
        print("RC4_PUBLIC_PACKAGE_SHA256", checksum, name, flush=True)
    (output / "SOURCE.json").write_text(json.dumps({
        "purpose": "Unmodified public RC4 packages for disposable upgrade tests",
        "source_commit": RC4_SOURCE,
        "reconstructed_from_source": False,
        "files": packages,
    }, indent=2) + "\n")
    print("Hash-verified public RC4 upgrade fixture:", output)


def prepare_previous(output, arch, profile="rc3"):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    if any(output.glob("*.deb")):
        raise RuntimeError("Use a new empty directory for the historical test fixture")
    if profile == "rc4":
        prepare_public_rc4(output, arch)
        return
    # Reject a wrong source ref instead of silently testing the current code.
    revision = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", RC3_SOURCE + "^{commit}"], text=True).strip()
    if revision != RC3_SOURCE:
        raise RuntimeError("The historical RC3 source is unavailable")
    with tempfile.TemporaryDirectory(prefix="daylight-rc3-source-") as temporary:
        work = Path(temporary)
        archive = work / "source.tar"
        source = work / "source"
        source.mkdir()
        run("git", "-C", str(ROOT), "archive", "--output", str(archive), RC3_SOURCE,
            "Cargo.toml", "Cargo.lock", "rust-toolchain.toml", "src", "config", "packaging",
            "scripts", "licenses",
            "assets/wallpapers", "assets/branding", "docs/THIRD_PARTY.md")
        with tarfile.open(archive) as stream:
            stream.extractall(source, filter="data")
        required = ("scripts/daylight-session", "scripts/daylight-terminal", "scripts/interactive-shell",
                    "config/fluxbox/menu", "packaging/control-center.desktop")
        missing = [name for name in required if not (source / name).is_file()]
        if missing:
            raise RuntimeError("Historical fixture source is incomplete: " + ", ".join(missing))
        for path in (ROOT / "assets/wallpapers").glob("*"):
            if path.suffix in (".jpg", ".png"):
                shutil.copy2(path, source / "assets/wallpapers" / path.name)
        shutil.copy2(ROOT / "assets/branding/daylight.png", source / "assets/branding/daylight.png")
        # The archived directory has no .git; force the known historical epoch.
        epoch = subprocess.check_output(["git", "-C", str(ROOT), "show", "-s", "--format=%ct", RC3_SOURCE], text=True).strip()
        env = dict(os.environ, SOURCE_DATE_EPOCH=epoch)
        host_info = subprocess.check_output(["rustup", "run", "1.88.0", "rustc", "-vV"], text=True)
        host = next(line.split(": ", 1)[1] for line in host_info.splitlines() if line.startswith("host: "))
        sysroot = subprocess.check_output(["rustup", "run", "1.88.0", "rustc", "--print", "sysroot"], text=True).strip()
        triple = TRIPLES[arch]
        env["CARGO_TARGET_" + triple.upper().replace("-", "_") + "_LINKER"] = str(Path(sysroot) / "lib/rustlib" / host / "bin/rust-lld")
        notices = ROOT / "licenses/RUST-STANDARD-LIBRARY.html"
        if notices.is_file():
            shutil.copy2(notices, source / "licenses" / notices.name)
        else:
            run("python3", "scripts/collect-notices.py", cwd=source, env=env)
        run("cargo", "+1.88.0", "build", "--locked", "--release", "--target", triple, cwd=source, env=env)
        binary = source / "target" / triple / "release/daylight"
        if arch == "amd64":
            version = subprocess.check_output([str(binary), "--version"], text=True)
            if "5.0.0-rc.3" not in version:
                raise RuntimeError("Fixture is not the historical RC3 executable")
        run("python3", "scripts/build-debs.py", "--arch", arch, "--binary", str(binary), "--output", str(output), cwd=source, env=env)
    files = sorted(output.glob("*.deb"))
    if len(files) != 7:
        raise RuntimeError("Expected one historical core plus six data packages")
    (output / "SOURCE.json").write_text(json.dumps({
        "purpose": "Disposable upgrade-test fixture, not a new public RC3 release",
        "source_commit": RC3_SOURCE,
        "reconstructed_from_source": True,
        "files": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in files},
    }, indent=2) + "\n")
    print("Historical RC3-source upgrade fixture:", output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-fixture", type=Path)
    parser.add_argument("--arch", choices=TRIPLES, default="amd64")
    parser.add_argument("--run-container", choices=("bookworm", "trixie"))
    parser.add_argument("--previous-packages", type=Path)
    parser.add_argument("--previous-profile", choices=("rc3", "rc4"), default="rc3")
    parser.add_argument("--conky-case", choices=("stock", "custom"), default="stock")
    args = parser.parse_args()
    if args.prepare_fixture:
        prepare_previous(args.prepare_fixture, args.arch, args.previous_profile)
    if args.run_container:
        previous = (args.previous_packages or args.prepare_fixture)
        if previous is None or not previous.is_dir():
            parser.error("--previous-packages must identify a prepared historical fixture")
        run("docker", "run", "--rm", "--cpus=2", "--memory=1536m", "--memory-swap=1536m", "--pids-limit=512",
            "-e", "DAYLIGHT_DISPOSABLE_TEST=yes",
            "-e", "DAYLIGHT_PREVIOUS_PROFILE=" + args.previous_profile,
            "-e", "DAYLIGHT_CONKY_CASE=" + args.conky_case, "-v", str(ROOT) + ":/src:ro",
            "-v", str(previous.resolve()) + ":/previous:ro", "debian:" + args.run_container,
            "/bin/sh", "/src/scripts/test-upgrade.sh")
    if not args.prepare_fixture and not args.run_container:
        parser.error("Select --prepare-fixture or --run-container explicitly")


if __name__ == "__main__":
    main()
