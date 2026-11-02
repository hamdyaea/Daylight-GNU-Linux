#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Publish exact passed artifacts; normalize filenames before hashing; never overwrite a published release."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tomllib

ROOT=Path(__file__).resolve().parent.parent

def gh(*args):
    return subprocess.check_output(['gh',*args],text=True)

def api(path,payload=None):
    command=['gh','api',path]
    if payload is not None:command+=['--method','POST','--input','-']
    return json.loads(subprocess.check_output(command,input=json.dumps(payload) if payload is not None else None,text=True))

def digest(path):
    value=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(4*1024*1024),b''):value.update(block)
    return value.hexdigest()

def main():
    repo=os.environ['GH_REPO'];prefix='repos/'+repo
    request=json.loads((ROOT/'release/READY.json').read_text())
    run_id,sha,tag=request['run_id'],request['commit'],request['tag']
    if not isinstance(run_id,int) or run_id<=0 or not re.fullmatch('[0-9a-f]{40}',sha):raise SystemExit('Invalid validation reference')
    if not re.fullmatch(r'v[0-9]+\.[0-9]+\.[0-9]+(?:-rc\.[0-9]+)?',tag):raise SystemExit('Invalid release version')
    run=api(prefix+'/actions/runs/'+str(run_id))
    valid=run['status']=='completed' and run['conclusion']=='success' and run['head_sha']==sha
    valid &= run['head_branch'] in ('master','build/daylight-v5-rc2') and run['event'] in ('push','workflow_dispatch')
    valid &= run['path']=='.github/workflows/daylight-build.yml' and run['head_repository']['full_name'].lower()==repo.lower()
    if not valid:raise SystemExit('The exact source has not passed the complete candidate workflow')
    cargo=tomllib.loads(subprocess.check_output(['git','show',sha+':Cargo.toml'],text=True))
    if tag!='v'+cargo['package']['version']:raise SystemExit('Tag does not match the tested Cargo version')
    subprocess.run(['git','merge-base','--is-ancestor',sha,'HEAD'],check=True)
    number=str(run['run_number'])
    files=ROOT/'release-files';evidence=ROOT/'validation'
    for name,directory in [('daylight-candidate-'+number,files),('daylight-validation-'+number,evidence)]:
        subprocess.run(['gh','run','download',str(run_id),'--name',name,'--dir',str(directory)],check=True)
    subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=files,check=True)
    shutil.copyfile(files/'SHA256SUMS',evidence/'original-artifact-SHA256SUMS')
    if (evidence/'validation/source-commit.txt').read_text().strip()!=sha:raise SystemExit('Evidence commit mismatch')
    for suite in ('bookworm','trixie'):
        if 'DAYLIGHT_PACKAGE_LIFECYCLE_OK' not in (evidence/'package-tests'/suite/'lifecycle.log').read_text():raise SystemExit('Missing lifecycle evidence: '+suite)
    for mode in ('live-test','boot-bios','boot-uefi','browser-demo'):
        if not (evidence/mode/'result.txt').read_text().startswith('PASS:'):raise SystemExit('Missing validation gate: '+mode)
    version=cargo['package']['version'];iso=files/('daylight-live_'+version+'_amd64.iso')
    subprocess.run(['python3',str(ROOT/'release/package-manifest.py'),str(iso),'--commit',sha,'--output',str(evidence)],check=True)
    (evidence/'verified-run.json').write_text(json.dumps(request,indent=2)+'\n')
    shutil.make_archive(str(files/'daylight-validation'),'zip',evidence)
    for source,name in [('package-tests/bookworm/daylight-desktop.png','daylight-desktop-debian12.png'),('package-tests/trixie/daylight-desktop.png','daylight-desktop-debian13.png'),('live-test/desktop.png','daylight-live-desktop.png'),('boot-bios/desktop.png','daylight-boot-bios.png'),('boot-uefi/desktop.png','daylight-boot-uefi.png'),('browser-demo/browser.png','daylight-browser-demo.png')]:
        shutil.copyfile(evidence/source,files/name)
    for path in list(files.glob('*.deb')):
        if '~' in path.name:path.rename(path.with_name(path.name.replace('~','.')))
    assets=sorted(p for p in files.iterdir() if p.is_file() and p.name!='SHA256SUMS')
    (files/'SHA256SUMS').write_text(''.join(digest(p)+'  '+p.name+'\n' for p in assets))
    assets=sorted(p for p in files.iterdir() if p.is_file())
    expected={p.name:(p.stat().st_size,'sha256:'+digest(p)) for p in assets}
    releases=api(prefix+'/releases?per_page=100')
    existing=next((r for r in releases if r['tag_name']==tag),None)
    if existing and not existing['draft']:
        raise SystemExit('Release is already published; immutable published bytes will not be overwritten')
    if existing and existing['target_commitish']!=sha:raise SystemExit('Existing draft targets another source revision')
    if not existing:
        notes=(ROOT/'docs/RELEASE-RC2.md').read_text()
        existing=api(prefix+'/releases',{'tag_name':tag,'target_commitish':sha,'name':'Daylight GNU/Linux '+version,'body':notes,'draft':True,'prerelease':'-rc.' in version})
    subprocess.run(['gh','release','upload',tag,*map(str,assets),'--clobber'],check=True)
    uploaded=api(prefix+'/releases/'+str(existing['id']))
    actual={a['name']:(a['size'],a.get('digest')) for a in uploaded['assets']}
    if actual!=expected:raise SystemExit('Draft retained: uploaded names, sizes or SHA256 digests differ from validated files')
    payload=json.dumps({'draft':False})
    published=json.loads(subprocess.check_output(['gh','api',prefix+'/releases/'+str(existing['id']),'--method','PATCH','--input','-'],input=payload,text=True))
    print('Published verified release:',published['html_url'])
    current={'version':version,'tag':tag,'commit':sha,'iso':iso.name,'iso_sha256':digest(iso),'iso_bytes':iso.stat().st_size,'validation_run':run_id,'prerelease':'-rc.' in version}
    (ROOT/'release/current.json').write_text(json.dumps(current,indent=2)+'\n')
    subprocess.run(['git','config','user.name','Hamdy Abou El Anein'],check=True)
    subprocess.run(['git','config','user.email','info@daylightlinux.ch'],check=True)
    subprocess.run(['git','add','release/current.json'],check=True)
    if subprocess.run(['git','diff','--cached','--quiet']).returncode:
        subprocess.run(['git','commit','-m','Record the published verified release manifest [skip ci]'],check=True)
        subprocess.run(['gh','auth','setup-git'],check=True)
        subprocess.run(['git','fetch','origin','master'],check=True)
        subprocess.run(['git','merge-base','--is-ancestor','FETCH_HEAD','HEAD'],check=True)
        subprocess.run(['git','push','origin','HEAD:master'],check=True)
    # Only remove the duplicated large archive belonging to this successfully published run.
    for artifact in api(prefix+'/actions/runs/'+str(run_id)+'/artifacts')['artifacts']:
        if artifact['name']=='daylight-candidate-'+number:
            subprocess.run(['gh','api','--method','DELETE',prefix+'/actions/artifacts/'+str(artifact['id'])],check=True)

if __name__=='__main__':main()
