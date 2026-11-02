#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Retain exact Alpine copyleft source files/patches, verified against pinned APKBUILD SHA512s."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request

ROOT=Path(__file__).resolve().parent.parent
CACHE=ROOT/'dist/web-live-sources'

def download(url, target, digest=None, algorithm="sha512"):
    if target.is_file() and (digest is None or hashlib.new(algorithm,target.read_bytes()).hexdigest()==digest):return
    request=urllib.request.Request(url,headers={'User-Agent':'Daylight-open-source-archive/1'})
    tmp=target.with_suffix(target.suffix+'.partial')
    target.parent.mkdir(parents=True,exist_ok=True)
    try:
        result=subprocess.run(['curl','--disable','--fail','--silent','--show-error','--location','--proto','=https','--proto-redir','=https','--connect-timeout','10','--max-time','180','--max-filesize',str(220*1024*1024),url,'-o',str(tmp)],capture_output=True,text=True)
        if result.returncode:raise OSError(result.stderr[-250:])
        if digest is not None and hashlib.new(algorithm,tmp.read_bytes()).hexdigest()!=digest:raise ValueError('Source checksum mismatch')
        tmp.replace(target)
    finally:
        if tmp.exists():tmp.unlink()

def collect(package):
    origin=package['o'];commit=package['c']
    if not re.fullmatch(r'[a-z0-9+_.-]+',origin) or not re.fullmatch('[a-f0-9]{40}',commit):raise ValueError('Unexpected source identity')
    directory=CACHE/origin;recipe=directory/'APKBUILD';prefix=None
    for section in ('main','community'):
        url=f'https://gitlab.alpinelinux.org/alpine/aports/-/raw/{commit}/{section}/{origin}/'
        try:
            if recipe.exists():
                prefix=(directory/'origin-url.txt').read_text().strip();break
            download(url+'APKBUILD',recipe)
            prefix=url;(directory/'origin-url.txt').write_text(url+'\n');break
        except (OSError,ValueError):continue
    if not prefix:raise RuntimeError('Pinned APKBUILD unavailable: '+origin)
    source=recipe.read_text()
    blocks=re.findall(r'sha512sums=["\'](.*?)["\']',source,re.S)
    records=[]
    for block in blocks:
        for digest,name in re.findall(r'([a-f0-9]{128})\s+([^\s]+)',block):
            if not re.fullmatch('[A-Za-z0-9_.+@-]+',name):raise ValueError('Unsafe source filename: '+name)
            path=directory/name
            for url in [prefix+urllib.parse.quote(name), 'https://distfiles.alpinelinux.org/distfiles/v3.22/'+urllib.parse.quote(name)]:
                try:download(url,path,digest);break
                except (OSError,ValueError):continue
            else:raise RuntimeError('Exact source unavailable: '+origin+'/'+name)
            records.append({'file':name,'sha512':digest,'bytes':path.stat().st_size})
    if not records:raise RuntimeError('No pinned source checksums found: '+origin)
    result={'origin':origin,'aports_commit':commit,'recipe_url':prefix+'APKBUILD','files':records}
    (directory/'manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

def main():
    packages=json.loads((ROOT/'dist/web-live/packages.json').read_text())
    selected={p['o']:p for p in packages if 'GPL' in p['L']}
    CACHE.mkdir(parents=True,exist_ok=True);results=[];failures=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures={pool.submit(collect,p):name for name,p in selected.items()}
        for future in as_completed(futures):
            name=futures[future]
            try:
                item=future.result();results.append(item)
                print('VERIFIED SOURCE',name,len(item['files']),sum(f['bytes'] for f in item['files']),flush=True)
            except Exception as error:
                failures.append({'origin':name,'error':str(error)});print('SOURCE ERROR',name,str(error),flush=True)
    firmware=json.loads((ROOT/'web-live/upstream-firmware.lock.json').read_text())
    for item in firmware:
        try:
            name=item['file']
            if not re.fullmatch('[A-Za-z0-9_.-]+',name):raise ValueError('Unsafe firmware source path')
            download(item['url'],CACHE/'firmware'/name,item['sha256'],'sha256')
            print('VERIFIED FIRMWARE SOURCE',name,flush=True)
        except Exception as error:failures.append({'origin':'firmware','error':str(error)})
    (CACHE/'firmware').mkdir(exist_ok=True)
    (CACHE/'firmware/manifest.json').write_text(json.dumps(firmware,indent=2)+'\n')
    (CACHE/'collection.json').write_text(json.dumps({'sources':results,'failures':failures},indent=2)+'\n')
    if failures:raise SystemExit('Some corresponding sources remain unavailable; inspect collection.json')
    print('All copyleft origins have exact retained source files and build recipes.',flush=True)

if __name__=='__main__':main()
