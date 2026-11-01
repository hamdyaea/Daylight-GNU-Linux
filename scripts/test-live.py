#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: contact@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Boot a live filesystem in offline QEMU without attaching any host disk."""
import argparse
import json
from pathlib import Path
import socket
import subprocess
import tempfile
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("iso", type=Path)
    parser.add_argument("--output", type=Path, default=Path("dist/live-test"))
    parser.add_argument("--timeout", type=int, default=360)
    args = parser.parse_args()
    iso, out = args.iso.resolve(), args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="daylight-qemu-") as temporary:
        root = Path(temporary)
        subprocess.run(["xorriso", "-osirrox", "on", "-indev", str(iso), "-extract", "/live", str(root / "live")], check=True)
        kernels = sorted((root / "live").glob("vmlinuz*"))
        initrds = sorted((root / "live").glob("initrd*"))
        if not kernels or not initrds:
            raise SystemExit("The ISO has no live kernel or initramfs")
        qmp, serial = root / "qmp.sock", out / "serial.log"
        command = ["qemu-system-x86_64", "-accel", "tcg", "-m", "1536", "-smp", "2", "-display", "none", "-vga", "std", "-nic", "none", "-no-reboot",
                   "-cdrom", str(iso), "-kernel", str(kernels[0]), "-initrd", str(initrds[0]),
                   "-append", "boot=live components username=daylight hostname=daylight-live locales=en_US.UTF-8 timezone=UTC noswap console=ttyS0,115200 daylight.smoke=1",
                   "-serial", "file:" + str(serial), "-qmp", f"unix:{qmp},server=on,wait=off",
                   "-object", "rng-random,filename=/dev/urandom,id=rng0", "-device", "virtio-rng-pci,rng=rng0"]
        with (out / "qemu.log").open("w") as log:
            process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
            try:
                deadline = time.monotonic() + args.timeout
                while time.monotonic() < deadline:
                    text = serial.read_text(errors="replace") if serial.exists() else ""
                    if "DAYLIGHT_LIVE_READY" in text:
                        break
                    if "DAYLIGHT_LIVE_FAILED" in text or process.poll() is not None:
                        raise RuntimeError("Live smoke test failed; inspect the retained logs")
                    time.sleep(2)
                else:
                    raise RuntimeError("Live boot timed out; inspect serial.log")
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
                    connection.settimeout(10)
                    connection.connect(str(qmp))
                    stream = connection.makefile("rwb")
                    stream.readline()
                    requests = [{"execute": "qmp_capabilities"}, {"execute": "screendump", "arguments": {"filename": str(out / "desktop.ppm")}}]
                    for request in requests:
                        stream.write((json.dumps(request) + "\n").encode())
                        stream.flush()
                        while True:
                            response = json.loads(stream.readline())
                            if "error" in response:
                                raise RuntimeError(str(response["error"]))
                            if "return" in response:
                                break
                (out / "result.txt").write_text("PASS: offline live-filesystem boot with Fluxbox and Conky.\nDirect-kernel testing does not certify ISO bootloaders, physical hardware or Secure Boot.\n")
                print("DAYLIGHT_LIVE_SMOKE_OK")
            finally:
                process.terminate()
                try:
                    process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()


if __name__ == "__main__":
    main()
