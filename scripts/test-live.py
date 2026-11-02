#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Boot only an isolated ISO live filesystem, retaining diagnostics on failure."""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import time


def screenshot(socket_path, destination):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(10)
        connection.connect(str(socket_path))
        stream = connection.makefile('rwb')
        stream.readline()
        for request in ({'execute': 'qmp_capabilities'},
                        {'execute': 'screendump', 'arguments': {'filename': str(destination)}}):
            stream.write((json.dumps(request)+'\n').encode())
            stream.flush()
            while True:
                reply = json.loads(stream.readline())
                if 'error' in reply:
                    raise RuntimeError(str(reply['error']))
                if 'return' in reply:
                    break


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('iso', type=Path)
    parser.add_argument('--timeout', type=int, default=600)
    args = parser.parse_args()
    iso = args.iso.resolve()
    if not iso.is_file() or args.timeout < 30:
        parser.error('An existing ISO and timeout of at least 30 seconds are required')
    output = Path('dist/live-test').resolve()
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='daylight-live-test-') as temporary:
        work = Path(temporary)
        subprocess.run(['xorriso', '-osirrox', 'on', '-indev', str(iso), '-extract', '/live', str(work/'live')], check=True)
        kernel = sorted((work/'live').glob('vmlinuz*'))[0]
        initrd = sorted((work/'live').glob('initrd*'))[0]
        serial, monitor = output/'serial.log', work/'qmp.sock'
        kvm = os.access('/dev/kvm', os.R_OK | os.W_OK)
        (output/'environment.txt').write_text('Acceleration: '+('KVM' if kvm else 'TCG')+'\nNo network or host disks attached.\n')
        command = ['qemu-system-x86_64', '-accel', 'kvm' if kvm else 'tcg', '-cpu', 'host' if kvm else 'max',
                   '-m', '2048', '-smp', '2', '-display', 'none', '-vga', 'std', '-nic', 'none', '-no-reboot',
                   '-cdrom', str(iso), '-kernel', str(kernel), '-initrd', str(initrd),
                   '-append', 'boot=live components username=daylight hostname=daylight-live locales=en_US.UTF-8 timezone=UTC noswap console=tty0 console=ttyS0,115200 daylight.smoke=1',
                   '-serial', 'file:'+str(serial), '-qmp', f'unix:{monitor},server=on,wait=off',
                   '-object', 'rng-random,filename=/dev/urandom,id=rng0', '-device', 'virtio-rng-pci,rng=rng0']
        failure = None
        with (output/'qemu.log').open('w') as log:
            process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
            try:
                deadline = time.monotonic()+args.timeout
                while time.monotonic() < deadline:
                    text = serial.read_text(errors='replace') if serial.exists() else ''
                    if 'DAYLIGHT_LIVE_READY' in text:
                        screenshot(monitor, output/'desktop.ppm')
                        (output/'result.txt').write_text('PASS: offline live filesystem boot, live user, Fluxbox and Conky. ISO BIOS/UEFI bootloaders and physical hardware not certified.\n')
                        print('DAYLIGHT_LIVE_READY confirmed; screenshot retained.')
                        break
                    if 'DAYLIGHT_LIVE_FAILED' in text:
                        raise RuntimeError('Guest reported failure; inspect serial.log and desktop.ppm')
                    if process.poll() is not None:
                        raise RuntimeError('QEMU exited before the graphical session became ready')
                    time.sleep(2)
                else:
                    raise TimeoutError('Live boot did not confirm the desktop within the deadline')
            except Exception as error:
                failure = error
                (output/'result.txt').write_text('FAIL: '+str(error)+'\n')
                if process.poll() is None and monitor.exists():
                    try:
                        screenshot(monitor, output/'desktop.ppm')
                    except Exception as capture_error:
                        (output/'screenshot-error.txt').write_text(str(capture_error)+'\n')
            finally:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill(); process.wait()
        if failure:
            raise failure


if __name__ == '__main__':
    main()
