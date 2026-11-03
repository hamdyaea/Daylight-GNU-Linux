#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein | Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Prepare verified <=16 MiB runtime assets from a reviewed publication manifest."""
from pathlib import Path
import argparse, hashlib, json, re, shutil
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--runtime',type=Path,required=True);a=p.parse_args()
source=a.runtime.resolve();out=ROOT/'pages-runtime';out.mkdir(exist_ok=True)
manifest=json.loads((source/'manifest.json').read_text())
assert manifest['schema']==1 and manifest['network_relay'] is False
for name,record in manifest['files'].items():
 filename=record.get('file',name)
 assert re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]+',filename)
 src=source/filename;data=src.read_bytes()
 assert not src.is_symlink() and len(data)==record['bytes'] and hashlib.sha256(data).hexdigest()==record['sha256'],name
 if len(data)>16*1024*1024:
  assert name!='libv86.js' and len(data)<=100000000
  record.pop('file',None);record['parts']=[]
  for i,start in enumerate(range(0,len(data),16*1024*1024)):
   part=data[start:start+16*1024*1024];digest=hashlib.sha256(part).hexdigest();file=f'{Path(name).stem}-part-{i:02d}-{digest[:16]}.bin'
   (out/file).write_bytes(part);record['parts'].append(dict(file=file,bytes=len(part),sha256=digest))
 else:shutil.copyfile(src,out/filename);record['file']=filename
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Verified chunk manifest:',out/'manifest.json')
