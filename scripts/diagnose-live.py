#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: contact@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Inspect an already-built disposable live guest, with no network or host disks."""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('iso', type=Path)
    args = parser.parse_args()
    iso = args.iso.resolve()
    out = Path('dist/live-diagnostic').resolve()
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='daylight-live-diagnostic-') as temporary:
        root = Path(temporary)
        subprocess.run(['xorriso', '-osirrox', 'on', '-indev', str(iso), '-extract', '/live', str(root/'live')], check=True)
        kernel = sorted((root/'live').glob('vmlinuz*'))[0]
        initrd = sorted((root/'live').glob('initrd*'))[0]
        serial, qmp = root/'serial.sock', root/'qmp.sock'
        kvm = os.access('/dev/kvm', os.R_OK | os.W_OK)
        command = ['qemu-system-x86_64', '-accel', 'kvm' if kvm else 'tcg', '-cpu', 'host' if kvm else 'max',
                   '-m', '2048', '-smp', '2', '-display', 'none', '-vga', 'std', '-nic', 'none', '-no-reboot',
                   '-cdrom', str(iso), '-kernel', str(kernel), '-initrd', str(initrd),
                   '-append', 'boot=live components username=daylight hostname=daylight-live locales=en_US.UTF-8 timezone=UTC noswap console=tty0 console=ttyS0,115200 daylight.smoke=1 systemd.journald.forward_to_console=1',
                   '-serial', f'unix:{serial},server=on,wait=off', '-qmp', f'unix:{qmp},server=on,wait=off',
                   '-object', 'rng-random,filename=/dev/urandom,id=rng0', '-device', 'virtio-rng-pci,rng=rng0']
        (out/'environment.txt').write_text('Acceleration: '+('KVM' if kvm else 'TCG')+'\nInput ISO: '+iso.name+'\n')
        with (out/'qemu.log').open('w') as qlog, (out/'serial.log').open('wb') as log:
            process = subprocess.Popen(command, stdout=qlog, stderr=subprocess.STDOUT)
            try:
                for _ in range(100):
                    if serial.exists(): break
                    if process.poll() is not None: raise RuntimeError('QEMU stopped before console opened')
                    time.sleep(0.1)
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as console:
                    console.connect(str(serial)); console.settimeout(1)
                    deadline = time.monotonic()+240
                    phase, tail = 0, ''
                    while time.monotonic() < deadline:
                        try: data = console.recv(65536)
                        except socket.timeout: data = b''
                        if data:
                            log.write(data); log.flush(); tail = (tail+data.decode(errors='replace'))[-12000:]
                        if phase == 0 and ' login:' in tail:
                            console.sendall(b'daylight\n'); phase=1; tail=''
                        elif phase == 1 and 'Password:' in tail:
                            # The default disposable Debian Live account; no host credentials are read.
                            console.sendall(b'live\n'); phase=2; tail=''
                        elif phase in (1,2) and ('daylight@' in tail or '$ ' in tail):
                            cmd="printf 'DAYLIGHT_DIAGNOSTIC_START\\n'; id; ps -ef; systemctl --no-pager status lightdm daylight-live-smoke; sudo -n journalctl -b -u lightdm -u daylight-live-smoke --no-pager; sudo -n cat /var/log/lightdm/lightdm.log /var/log/lightdm/x-0.log; cat ~/.xsession-errors; ls -l /usr/lib/daylight/live-smoke.sh /usr/bin/daylight-session; printf '\\nDAYLIGHT_DIAGNOSTIC_DONE\\n'\n"
                            console.sendall(cmd.encode()); phase=3; tail=''
                        elif phase == 3 and '\r\nDAYLIGHT_DIAGNOSTIC_DONE\r\n' in tail:
                            break
                        if process.poll() is not None: break
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
                    connection.settimeout(10); connection.connect(str(qmp))
                    stream=connection.makefile('rwb'); stream.readline()
                    for request in [{'execute':'qmp_capabilities'}, {'execute':'screendump','arguments':{'filename':str(out/'desktop.ppm')}}]:
                        stream.write((json.dumps(request)+'\n').encode()); stream.flush()
                        while True:
                            response=json.loads(stream.readline())
                            if 'error' in response: raise RuntimeError(str(response['error']))
                            if 'return' in response: break
                print('Diagnostic console and screenshot retained; this is not a validation pass.')
            finally:
                process.terminate()
                try: process.wait(timeout=10)
                except subprocess.TimeoutExpired: process.kill(); process.wait()


if __name__ == '__main__':
    main()
