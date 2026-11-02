#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Publish only verified static browser-demo files; never start Docker, QEMU or a service."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil

WEB=Path('/var/www/daylightlinux/live')


def sha(path):
    value=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):value.update(block)
    return value.hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--evidence',type=Path,required=True)
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args();source=args.source.resolve()
    if source==WEB or WEB in source.parents or source in WEB.parents:parser.error('Staging and web directories must be separate')
    manifest=json.loads((source/'deployment-manifest.json').read_text())
    evidence=json.loads(args.evidence.read_text())
    if evidence.get('result')!='PASS' or evidence.get('realKeyboard') is not True or evidence.get('manifestSha256')!=sha(source/'manifest.json'):
        raise SystemExit('Exact-runtime browser and keyboard validation is required')
    if evidence.get('terminalOnlyStartup') is not True or evidence.get('startupFocused') is not True or evidence.get('startupTitle') != 'Daylight Start':
        raise SystemExit('Verified terminal-first Daylight Start startup is required')
    if evidence.get('simpleToolbar') is not True or evidence.get('restartCleanGuest') is not True or evidence.get('automaticVisibilityResume') is not True:
        raise SystemExit('Validated three-control interface, clean restart and automatic resume are required')
    for name in ('index.html','demo.js','demo.css'):
        if evidence.get('interfaceSha256',{}).get(name)!=sha(source/name):
            raise SystemExit('Exact graphical-interface browser validation is required: '+name)
    entries=manifest['files']
    if not {'index.html','demo.js','demo.css','manifest.json','SOURCES.txt','daylight-web-sources.zip'}<=set(entries):raise SystemExit('Incomplete browser demo')
    for name,record in entries.items():
        if not re.fullmatch(r'[A-Za-z0-9_.-]+',name) or name.startswith('.'):
            raise SystemExit('Unsafe publication filename')
        path=source/name
        if path.is_symlink() or not path.is_file() or path.stat().st_size!=record['bytes'] or sha(path)!=record['sha256']:
            raise SystemExit('Unverified static file: '+name)
    print('Verified static files:',len(entries),'total bytes:',sum(r['bytes'] for r in entries.values()))
    if not args.apply:
        print('Plan only; no changes. No runtime service is needed.')
        return
    if os.geteuid()!=0:raise SystemExit('Explicit production publication requires root')
    if not WEB.parent.is_dir() or WEB.is_symlink():raise SystemExit('Unexpected web-root layout')
    if WEB.exists() and not (WEB/'deployment-manifest.json').is_file():
        # The main static-site generator may have created only the reviewed interface.
        allowed={'index.html','demo.js','demo.css','daylight.svg'}
        if any(p.name not in allowed or p.is_symlink() for p in WEB.iterdir()):raise SystemExit('Unmanaged existing live directory; refusing to replace it')
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup=Path('/var/backups/daylight-web-live')/stamp
    if WEB.exists():
        backup.mkdir(parents=True)
        for path in WEB.iterdir():
            if path.is_file() and path.name in ('index.html','demo.js','demo.css','manifest.json','deployment-manifest.json','SOURCES.txt'):
                shutil.copyfile(path,backup/path.name)
    WEB.mkdir(mode=0o755,exist_ok=True)
    # Payloads are content-addressed; older versions remain readable during updates.
    for name in sorted(entries,key=lambda n:(n in ('manifest.json','index.html'),n=='index.html')):
        target=WEB/name
        if target.is_symlink():raise SystemExit('Unexpected symlink destination')
        if target.exists() and re.search(r'-[a-f0-9]{16}\.',name) and sha(target)!=entries[name]['sha256']:
            raise SystemExit('Immutable payload filename collision')
        temporary=target.with_name('.'+name+'.new')
        shutil.copyfile(source/name,temporary);temporary.chmod(0o644);temporary.replace(target)
    temporary=WEB/'.deployment-manifest.new'
    shutil.copyfile(source/'deployment-manifest.json',temporary);temporary.chmod(0o644)
    temporary.replace(WEB/'deployment-manifest.json')
    for name,record in entries.items():
        if sha(WEB/name)!=record['sha256']:raise SystemExit('Post-publication verification failed: '+name)
    print('Published static browser demo:',WEB,'Backup:',backup if backup.exists() else 'first deployment')
    print('No daemon, container, web configuration, network rule or production service was changed.')


if __name__=='__main__':main()
