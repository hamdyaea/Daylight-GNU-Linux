#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Run the verified AMD64 live ISO privately with noVNC and a bounded lifetime."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import socket
import subprocess
import tempfile
import time
import urllib.request


def digest(path):
    value=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4*1024*1024), b''):
            value.update(block)
    return value.hexdigest()


def obtain(manifest, cache):
    release=json.loads(manifest.read_text())
    if not re.fullmatch(r'v5\.0\.0(?:-rc\.[0-9]+)?', release['tag']):
        raise ValueError('Unexpected demo release tag')
    if not re.fullmatch(r'daylight-live_5\.0\.0(?:-rc\.[0-9]+)?_amd64\.iso',release['iso']):
        raise ValueError('Unexpected ISO name')
    if not re.fullmatch('[a-f0-9]{64}',release['iso_sha256']):
        raise ValueError('A pinned ISO SHA256 is required')
    cache.mkdir(parents=True,exist_ok=True)
    path=cache/release['iso']
    if path.is_file() and digest(path)==release['iso_sha256']:
        return path
    url='https://github.com/hamdyaea/Daylight-GNU-Linux/releases/download/'+release['tag']+'/'+release['iso']
    temporary=path.with_suffix('.partial')
    request=urllib.request.Request(url,headers={'User-Agent':'Daylight-Browser-Demo/5'})
    try:
        with urllib.request.urlopen(request,timeout=60) as response, temporary.open('wb') as stream:
            total=0
            while True:
                block=response.read(4*1024*1024)
                if not block: break
                total+=len(block)
                if total>3*1024**3: raise ValueError('ISO exceeded the 3 GiB download limit')
                stream.write(block)
        if total!=release['iso_bytes'] or digest(temporary)!=release['iso_sha256']:
            raise ValueError('Published ISO size or digest does not match the pinned manifest')
        temporary.replace(path)
    finally:
        if temporary.exists(): temporary.unlink()
    return path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    default_manifest=Path(__file__).with_name('release.json')
    if not default_manifest.exists(): default_manifest=Path(__file__).resolve().parent.parent/'release/current.json'
    parser.add_argument('--manifest',type=Path,default=default_manifest)
    parser.add_argument('--cache',type=Path,default=Path.home()/'.cache/daylight-demo')
    parser.add_argument('--download-only',action='store_true')
    parser.add_argument('--iso',type=Path)
    parser.add_argument('--sha256')
    parser.add_argument('--listen',choices=['127.0.0.1','0.0.0.0'],default='127.0.0.1')
    parser.add_argument('--port',type=int,default=6080)
    parser.add_argument('--duration',type=int,default=1200)
    args=parser.parse_args()
    if not 1024<=args.port<=65535 or not 30<=args.duration<=3600:
        parser.error('Port must be unprivileged; session lifetime must be 30..3600 seconds')
    if args.iso:
        iso=args.iso.resolve()
        if not args.sha256 or not re.fullmatch('[a-f0-9]{64}',args.sha256) or digest(iso)!=args.sha256:
            parser.error('An explicit ISO requires its matching --sha256')
    else:
        iso=obtain(args.manifest,args.cache).resolve()
    if args.download_only:
        print('Verified ISO cached:',iso)
        return
    if os.geteuid()==0:
        raise SystemExit('Never run the interactive guest or its VNC frontend as root')
    if args.listen=='0.0.0.0' and not Path('/.dockerenv').exists() and not os.environ.get('CODESPACES'):
        raise SystemExit('Wildcard listening is permitted only inside the intended container')
    with socket.socket() as check:
        check.bind((args.listen,args.port))
    with tempfile.TemporaryDirectory(prefix='daylight-demo-') as temporary:
        work=Path(temporary)
        vnc=work/'vnc.sock'
        readiness=work/'guest-readiness.log'
        qemu=['qemu-system-x86_64','-accel','tcg','-cpu','max','-m','1536','-smp','1','-display','none','-vga','std','-nic','none','-no-reboot','-boot','d','-cdrom',str(iso),'-monitor','none','-serial','file:'+str(work/'serial.log'),'-vnc','unix:'+str(vnc),'-usb','-device','usb-tablet','-sandbox','on,obsolete=deny,elevateprivileges=deny,spawn=deny,resourcecontrol=deny',
              '-device','virtio-serial-pci','-chardev','file,id=daylight-ready,path='+str(readiness),'-device','virtserialport,chardev=daylight-ready,name=org.daylightlinux.test']
        # Only a tiny readiness report crosses this dedicated observation channel.
        # No host disk, shared directory, repository credential or SSH agent is exposed.
        child_env={'PATH':'/usr/local/bin:/usr/bin:/bin','HOME':str(work),'LANG':'C.UTF-8','TMPDIR':str(work)}
        children=[]
        def stop(signum=None,frame=None):
            for child in reversed(children):
                if child.poll() is None: child.terminate()
            if signum is not None: raise KeyboardInterrupt
        signal.signal(signal.SIGTERM,stop)
        signal.signal(signal.SIGINT,stop)
        with (work/'qemu.log').open('w') as log:
            try:
                guest=subprocess.Popen(qemu,env=child_env,stdout=log,stderr=subprocess.STDOUT)
                children.append(guest)
                for _ in range(100):
                    if vnc.exists(): break
                    if guest.poll() is not None: raise RuntimeError((work/'qemu.log').read_text())
                    time.sleep(.1)
                else: raise RuntimeError('The private VNC socket did not start')
                web=Path('/opt/daylight-demo/www')
                if not web.is_dir(): web=Path('/usr/share/novnc')
                proxy=subprocess.Popen(['websockify','--web',str(web),'--unix-target',str(vnc),'--heartbeat','30',f'{args.listen}:{args.port}'],env=child_env)
                children.append(proxy)
                print(f'Daylight browser demo: http://127.0.0.1:{args.port}/vnc.html?autoconnect=true&resize=scale',flush=True)
                print('The VM is booting; an established VNC connection does not yet mean the desktop is ready.',flush=True)
                print('No guest network, no host disks, no persistence. Session terminates automatically after '+str(args.duration)+' seconds.',flush=True)
                deadline=time.monotonic()+args.duration
                announced=False
                while time.monotonic()<deadline:
                    if guest.poll() is not None or proxy.poll() is not None:
                        raise RuntimeError('The demo guest or frontend exited unexpectedly')
                    if not announced and readiness.exists():
                        with readiness.open('rb') as stream: report=stream.read(65536)
                        if b'DAYLIGHT_LIVE_FAILED' in report:
                            raise RuntimeError('The live guest reported a desktop startup failure')
                        if b'DAYLIGHT_LIVE_READY' in report:
                            print('DAYLIGHT_DESKTOP_READY: live user, Fluxbox and Conky are running.',flush=True)
                            announced=True
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            finally:
                stop()
                for child in reversed(children):
                    try: child.wait(timeout=10)
                    except subprocess.TimeoutExpired: child.kill();child.wait()


if __name__=='__main__':
    main()
