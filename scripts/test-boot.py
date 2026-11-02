#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: contact@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Boot the unmodified ISO through BIOS or UEFI, without bypassing its bootloader."""
import argparse
import importlib.util
import os
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import time


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('iso',type=Path)
    parser.add_argument('--firmware',choices=['bios','uefi'],required=True)
    parser.add_argument('--timeout',type=int,default=600)
    args=parser.parse_args()
    iso=args.iso.resolve()
    if not iso.is_file(): parser.error('ISO is missing')
    out=Path('dist/boot-'+args.firmware).resolve();out.mkdir(parents=True,exist_ok=True)
    spec=importlib.util.spec_from_file_location('live_test',Path(__file__).with_name('test-live.py'))
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    with tempfile.TemporaryDirectory(prefix='daylight-boot-') as temporary:
        work=Path(temporary)
        monitor=work/'qmp.sock';channel=work/'guest.sock'
        kvm=os.access('/dev/kvm',os.R_OK|os.W_OK)
        command=['qemu-system-x86_64','-accel','kvm' if kvm else 'tcg','-cpu','host' if kvm else 'max','-m','2048','-smp','2','-display','none','-vga','std','-nic','none','-no-reboot','-boot','d','-cdrom',str(iso),'-serial','file:'+str(out/'serial.log'),'-qmp',f'unix:{monitor},server=on,wait=off','-device','virtio-serial-pci','-chardev',f'socket,id=daylighttest,path={channel},server=on,wait=off','-device','virtserialport,chardev=daylighttest,name=org.daylightlinux.test','-object','rng-random,filename=/dev/urandom,id=rng0','-device','virtio-rng-pci,rng=rng0']
        if args.firmware=='uefi':
            code=Path('/usr/share/OVMF/OVMF_CODE_4M.fd');variables=Path('/usr/share/OVMF/OVMF_VARS_4M.fd')
            if not code.exists() or not variables.exists(): raise RuntimeError('Install OVMF with the 4M non-Secure-Boot firmware files')
            shutil.copyfile(variables,work/'vars.fd')
            command+=['-drive',f'if=pflash,format=raw,readonly=on,file={code}','-drive',f'if=pflash,format=raw,file={work/"vars.fd"}']
        failure=None
        with (out/'qemu.log').open('w') as log:
            process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
            stream=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
            try:
                deadline=time.monotonic()+args.timeout
                while not channel.exists():
                    if process.poll() is not None or time.monotonic()>deadline: raise RuntimeError('QEMU did not expose its private validation channel')
                    time.sleep(.1)
                stream.connect(str(channel));stream.settimeout(2)
                data=b''
                while time.monotonic()<deadline:
                    try:
                        chunk=stream.recv(65536)
                        if chunk: data+=chunk
                    except socket.timeout: pass
                    (out/'guest.log').write_bytes(data)
                    if b'DAYLIGHT_LIVE_READY' in data:
                        time.sleep(2)
                        helper.screenshot(monitor,out/'desktop.ppm')
                        (out/'result.txt').write_text('PASS: real '+args.firmware.upper()+' ISO bootloader reached the Daylight live user, Fluxbox and Conky. No network or host disks. UEFI Secure Boot disabled.\n')
                        print('DAYLIGHT_'+args.firmware.upper()+'_BOOT_OK')
                        break
                    if b'DAYLIGHT_LIVE_FAILED' in data or process.poll() is not None: raise RuntimeError('Guest boot failed; inspect retained diagnostics')
                else: raise TimeoutError('Bootloader test timed out before desktop readiness')
            except Exception as error:
                failure=error
                (out/'result.txt').write_text('FAIL: '+str(error)+'\n')
                if process.poll() is None and monitor.exists():
                    try: helper.screenshot(monitor,out/'desktop.ppm')
                    except Exception: pass
            finally:
                stream.close()
                process.terminate()
                try: process.wait(timeout=10)
                except subprocess.TimeoutExpired: process.kill();process.wait()
        if failure: raise failure


if __name__=='__main__':
    main()
