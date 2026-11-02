#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Create an allowlisted static deployment and a separate corresponding-source archive."""
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT=Path(__file__).resolve().parent.parent
RUNTIME=ROOT/'dist/web-live'
SOURCES=ROOT/'dist/web-live-sources'
OUT=ROOT/'dist/web-live-publish'


def digest(path):
    value=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):value.update(block)
    return value.hexdigest()


def main():
    collection=json.loads((SOURCES/'collection.json').read_text())
    if collection['failures']:raise SystemExit('Corresponding source collection is incomplete')
    packages=json.loads((RUNTIME/'packages.json').read_text())
    required={p['o'] for p in packages if 'GPL' in p['L']}
    if {s['origin'] for s in collection['sources']}!=required:raise SystemExit('Source collection does not match the guest’s copyleft origins')
    for source in collection['sources']:
        for item in source['files']:
            path=SOURCES/source['origin']/item['file']
            if not path.is_file() or hashlib.sha512(path.read_bytes()).hexdigest()!=item['sha512']:raise SystemExit('Changed corresponding source: '+str(path))
    for item in json.loads((ROOT/'web-live/upstream-firmware.lock.json').read_text()):
        if digest(SOURCES/'firmware'/item['file'])!=item['sha256']:raise SystemExit('Firmware source checksum mismatch')
    manifest=json.loads((RUNTIME/'manifest.json').read_text())
    for name,record in manifest['files'].items():
        path=RUNTIME/name
        if path.is_symlink() or digest(path)!=record['sha256'] or path.stat().st_size!=record['bytes']:raise SystemExit('Runtime bytes changed: '+name)
    OUT.mkdir(parents=True,exist_ok=True)
    sources_zip=OUT/'daylight-web-sources.zip'
    with zipfile.ZipFile(sources_zip,'w',zipfile.ZIP_STORED,allowZip64=True) as archive:
        for path in sorted(SOURCES.rglob('*')):
            if path.is_file() and not path.is_symlink() and not path.name.endswith('.partial'):archive.write(path,'upstream/'+str(path.relative_to(SOURCES)))
        for path in sorted((ROOT/'web-live').iterdir()):
            if path.is_file() and (path.name=='init' or path.suffix in ('.py','.sh','.mjs','.cjs','.js','.css','.html','.json','.md','.license')):archive.write(path,'daylight/'+path.name)
        archive.write(ROOT/'LICENSE','daylight/LICENSE-GPL-3.txt')
    license_text='''Daylight Web Preview — experimental browser edition
Developer: Hamdy Abou El Anein
Contact: info@daylightlinux.ch

This is an Alpine Linux x86 / Fluxbox preview running on the visitor’s device.
The actual Daylight installable release remains Debian / Raspberry Pi OS ARM64.
No guest network relay, shared host disk, persistent storage or telemetry is used.

Daylight glue, build recipes and interface: GPL-3.0-only.
v86: BSD-2-Clause; unmodified npm release 0.5.473 (source ref 315b2b0).
SeaBIOS and SeaVGABIOS: upstream rel-1.16.2, LGPL-3.0; original config and source retained.
Alpine packages retain their original licenses. packages.json records their names,
versions, SPDX license fields, origin packages and exact aports source commits.
The image is pruned: unused kernel modules and OpenGL/LLVM payloads are omitted.
This is not a complete or generally upgradeable Alpine distribution.

The free corresponding-source archive is served at:
  https://daylightlinux.ch/live/daylight-web-sources.zip
It contains exact source archives/patches and build recipes for the guest’s
copyleft-origin packages, checked against the pinned APKBUILD SHA512 values,
plus the SeaBIOS and v86 upstream sources and the Daylight preview recipe.
The source archive is NOT downloaded when starting the demo.
Original permissive package sources are identified by the immutable aports
commits in packages.json, at https://gitlab.alpinelinux.org/alpine/aports .

Upstream projects:
  https://github.com/copy/v86
  https://www.seabios.org/
  https://alpinelinux.org/
  https://fluxbox.org/
Daylight source:
  https://github.com/hamdyaea/Daylight-GNU-Linux/tree/master/web-live
Artwork provenance:
  https://github.com/hamdyaea/Daylight-GNU-Linux/blob/master/docs/ARTWORK.md

No standalone host font files, credentials, signing keys or workbench logs are
published. Fonts inside the Linux guest come from the original Alpine packages.
Browser support and measured boot tests are described in the preview README.
'''
    (OUT/'SOURCES.txt').write_text(license_text+'\nCorresponding-source ZIP SHA256: '+digest(sources_zip)+'\n')
    # Immutable payload names allow old clients to finish during future updates.
    for name,record in manifest['files'].items():
        original=Path(name)
        filename=original.stem+'-'+record['sha256'][:16]+original.suffix
        shutil.copyfile(RUNTIME/name,OUT/filename);record['file']=filename
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    names={'packages.json','kernel-modules.json','index.html','demo.css','demo.js','daylight.svg','V86-LICENSE.txt'}
    for name in sorted(names):shutil.copyfile(RUNTIME/name,OUT/name)
    shutil.copyfile(ROOT/'LICENSE',OUT/'DAYLIGHT-LICENSE.txt')
    shutil.copyfile(SOURCES/'firmware/COPYING.LESSER',OUT/'FIRMWARE-LICENSE.txt')
    public_names=names|{record['file'] for record in manifest['files'].values()}|{'manifest.json','SOURCES.txt','daylight-web-sources.zip','DAYLIGHT-LICENSE.txt','FIRMWARE-LICENSE.txt'}
    final={name:{'bytes':(OUT/name).stat().st_size,'sha256':digest(OUT/name)} for name in sorted(public_names)}
    (OUT/'deployment-manifest.json').write_text(json.dumps({'schema':1,'files':final},indent=2)+'\n')
    print('Runtime bytes:',sum(x['bytes'] for x in manifest['files'].values()))
    print('Corresponding source bytes:',sources_zip.stat().st_size)
    print('Reviewed static files:',len(final),'in',OUT)


if __name__=='__main__':main()
