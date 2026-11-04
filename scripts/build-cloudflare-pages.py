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
 # Apply canonical redirects to HTML routes only: VM binaries and APT stay static.
 shutil.copy2(ROOT/'scripts/cloudflare-canonical-worker.js',out/'_worker.js')
 routes={'/robots.txt','/sitemap.xml'}
 for page in out.rglob('*.html'):
  path='/'+str(page.relative_to(out))
  routes.add(path)
  if path.endswith('/index.html'):
   routes.add(path[:-10])
   if path != '/index.html':routes.add(path[:-11])
  else:routes.add(path[:-5])
 assert len(routes)<=100, 'Pages routing rule limit exceeded'
 (out/'_routes.json').write_text(json.dumps({'version':1,'include':sorted(routes),'exclude':[]},indent=2)+'\n')
 files=[p for p in out.rglob('*') if p.is_file()]
 assert len(files)<=20000
 for p in files:
  assert not p.is_symlink() and p.stat().st_size<=25*1024*1024,p
 print('Pages ready:',len(files),'files;',sum(p.stat().st_size for p in files),'bytes; maximum',max(p.stat().st_size for p in files))
if __name__=='__main__':main()
