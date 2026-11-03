#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein | Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Build the reviewed static Pages site; no network, secret, server or VM build."""
from pathlib import Path
import hashlib, json, shutil
ROOT=Path(__file__).resolve().parents[1]
def main():
 out=ROOT/'dist/cloudflare-pages'
 if out.exists():shutil.rmtree(out)
 shutil.copytree(ROOT/'website-src',out,ignore=shutil.ignore_patterns('README.md','.htaccess','.git','*.php','*.log','__pycache__'))
 shutil.copytree(ROOT/'pages-runtime',out/'live',dirs_exist_ok=True)
 manifest=json.loads((out/'live/manifest.json').read_text())
 for name,record in manifest['files'].items():
  parts=record.get('parts',[record]);data=bytearray()
  for part in parts:
   content=(out/'live'/part['file']).read_bytes()
   assert len(content)==part['bytes'] and hashlib.sha256(content).hexdigest()==part['sha256'],part['file']
   data.extend(content)
  assert len(data)==record['bytes'] and hashlib.sha256(data).hexdigest()==record['sha256'],name
 files=[p for p in out.rglob('*') if p.is_file()]
 assert len(files)<=20000
 for p in files:
  assert not p.is_symlink() and p.stat().st_size<=25*1024*1024,p
 print('Pages ready:',len(files),'files;',sum(p.stat().st_size for p in files),'bytes; maximum',max(p.stat().st_size for p in files))
if __name__=='__main__':main()
