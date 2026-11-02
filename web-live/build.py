#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Build the Alpine browser preview on an unprivileged x86_64 Linux workstation.

No package is installed into the host. Reuse of an existing disposable root must
be explicit. Signed Alpine package checks remain enabled. Mirrors may eventually
remove pinned package versions; retain the source/artifact archives with releases.
"""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess

ROOT=Path(__file__).resolve().parent.parent
WORK=ROOT/'dist/web-live-build'
OUT=ROOT/'dist/web-live'


def obtain(url,path,expected,algorithm='sha256',encoded=False):
    def digest():
        raw=hashlib.new(algorithm,path.read_bytes()).digest()
        return base64.b64encode(raw).decode() if encoded else raw.hex()
    if not path.is_file() or digest()!=expected:
        temporary=path.with_name(path.name+'.download')
        subprocess.run(['curl','--disable','--fail','--silent','--show-error','--location','--proto','=https','--proto-redir','=https','--connect-timeout','10','--max-time','120',url,'-o',str(temporary)],check=True)
        temporary.replace(path)
    if digest()!=expected:raise ValueError('Input checksum mismatch: '+path.name)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reuse',action='store_true',help='Reuse only this project’s existing disposable guest tree')
    args=parser.parse_args()
    if os.geteuid()==0 or platform.machine()!='x86_64':parser.error('Build as an unprivileged user on an x86_64 workstation, not on the production Pi')
    for tool in ('bwrap','curl','bsdtar','cpio','gzip','bash'):
        if not shutil.which(tool):parser.error('Missing host build tool: '+tool)
    lock=json.loads((ROOT/'web-live/inputs.lock.json').read_text())
    packages=json.loads((ROOT/'web-live/alpine-packages.lock.json').read_text())
    WORK.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    root=WORK/'root'
    if root.exists() and not args.reuse:parser.error('Disposable root exists; use --reuse or archive it before a fresh build')
    base=WORK/'alpine-minirootfs.tar.gz'
    obtain('https://dl-cdn.alpinelinux.org/alpine/'+lock['alpine_branch']+'/releases/x86/alpine-minirootfs-'+lock['alpine_version']+'-x86.tar.gz',base,lock['minirootfs_sha256'])
    if not root.exists():
        root.mkdir()
        subprocess.run(['bsdtar','-xpf',str(base),'-C',str(root),'--no-same-owner'],check=True)
        pins=[p['P']+'='+p['V'] for p in packages]
        subprocess.run(['bwrap','--unshare-user','--unshare-pid','--unshare-ipc','--unshare-uts','--uid','0','--gid','0','--bind',str(root),'/','--proc','/proc','--dev','/dev','--ro-bind','/etc/resolv.conf','/etc/resolv.conf','--die-with-parent','/sbin/apk','add','--no-cache',*pins],check=True)
    found={}
    for block in (root/'lib/apk/db/installed').read_text().split('\n\n'):
        values=dict(line.split(':',1) for line in block.splitlines() if ':' in line)
        if 'P' in values:found[values['P']]=values['V']
    expected={p['P']:p['V'] for p in packages}
    if found!=expected:raise ValueError('Installed guest package versions differ from the reviewed lock')
    archive=WORK/'v86.tgz'
    obtain('https://registry.npmjs.org/v86/-/v86-'+lock['v86_version']+'.tgz',archive,lock['v86_npm_sha512'],'sha512',True)
    emulator=WORK/'emulator';emulator.mkdir(exist_ok=True)
    subprocess.run(['bsdtar','-xf',str(archive),'-C',str(emulator)],check=True)
    for name in ('libv86.js','v86.wasm'):shutil.copyfile(emulator/'package/build'/name,OUT/name)
    shutil.copyfile(emulator/'package/LICENSE',OUT/'V86-LICENSE.txt')
    for name,digest in lock['firmware'].items():
        obtain('https://raw.githubusercontent.com/copy/v86/'+lock['v86_source_ref']+'/bios/'+name,OUT/name,digest)
    subprocess.run(['python3',str(ROOT/'web-live/prepare-root.py'),'--root',str(root),'--output',str(OUT)],check=True)
    with (OUT/'initrd.bin').open('wb') as stream:
        subprocess.run(['bash','--noprofile','--norc','-o','pipefail','-c','find . -print0 | LC_ALL=C sort -z | cpio --null -o --format=newc --owner=0:0 2>/dev/null | gzip -n -6'],cwd=root,stdout=stream,check=True)
    for name in ('index.html','demo.css','demo.js'):shutil.copyfile(ROOT/'web-live'/name,OUT/name)
    shutil.copyfile(ROOT/'assets/branding/daylight.svg',OUT/'daylight.svg')
    page=(OUT/'index.html').read_text()
    for filename in ('demo.css','demo.js'):
        token=hashlib.sha256((OUT/filename).read_bytes()).hexdigest()[:12]
        page=page.replace('"'+filename+'"','"'+filename+'?v='+token+'"')
    (OUT/'index.html').write_text(page)
    manifest={'schema':1,'name':'Daylight Web Preview','base':'Alpine Linux '+lock['alpine_version']+' x86','emulator':'v86 '+lock['v86_version'],'memory_mib':256,'network_relay':False,'persistence':False,'files':{}}
    for name in ('libv86.js','v86.wasm','seabios.bin','vgabios.bin','vmlinuz.bin','initrd.bin'):
        p=OUT/name;manifest['files'][name]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Runtime bytes:',sum(p['bytes'] for p in manifest['files'].values()))
    print('Built',OUT,'Run node web-live/test-boot.mjs and the real-browser test before publication.')


if __name__=='__main__':main()
