#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Read-only public access and signature checks. No host APT configuration is changed."""
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parent.parent
BASE='https://daylightlinux.ch'
FPR='B0575F821A31DD20753DE07C50D21240F4BCB02E'


def main():
    checks=[]
    with tempfile.TemporaryDirectory(prefix='daylight-public-check-') as temporary:
        work=Path(temporary)
        def get(path):
            target=work/('fetch-'+str(len(checks)))
            run=subprocess.run(['curl','--disable','--fail','--silent','--show-error','--location','--proto','=https','--proto-redir','=https','--retry','2','--connect-timeout','10','--max-time','45','--max-filesize','2097152','--output',str(target),'--write-out','%{http_code} %{url_effective}',BASE+path],capture_output=True,text=True,timeout=150)
            if run.returncode:raise RuntimeError(path+': '+run.stderr[-300:])
            status,url=run.stdout.split(' ',1)
            if status!='200' or not url.startswith(BASE+'/'):raise RuntimeError('Unexpected public route: '+path+' '+run.stdout)
            data=target.read_bytes();checks.append({'path':path,'bytes':len(data),'status':int(status),'final_url':url})
            return data
        landing=get('/apt')
        if b'daylight-archive-keyring.gpg' not in landing or b'binary-arm64/Packages' not in landing:raise RuntimeError('Missing APT landing-page links')
        get('/apt/apt.css')
        for path in ['/fr','/fr/try-online.html','/fr/books.html','/old/site/index.html']:
            data=get(path)
            if path.endswith('try-online.html') and (b'/live/?lang=fr' not in data or b'Ouvrir le bureau graphique' not in data):raise RuntimeError('The public entry still does not lead to the no-account graphical demo')
        public=json.loads(get('/live/manifest.json'))
        expected=json.loads((ROOT/'web-live/published-runtime.json').read_text())
        if public!=expected:raise RuntimeError('Public runtime differs from the source-pinned manifest')
        for name in ['demo.js','demo.css']:
            if hashlib.sha256(get('/live/'+name)).digest()!=hashlib.sha256((ROOT/'web-live'/name).read_bytes()).digest():raise RuntimeError('Public interface differs from reviewed source: '+name)
        page=get('/live/')
        for marker in [b'id="desktop"',b'id="menu"',b'id="terminal"',b'id="screen"']:
            if marker not in page:raise RuntimeError('Missing graphical demo control')
        home=work/'gnupg';home.mkdir(mode=0o700)
        key=work/'archive.gpg';key.write_bytes(get('/apt/daylight-archive-keyring.gpg'))
        details=subprocess.check_output(['gpg','--homedir',str(home),'--batch','--with-colons','--show-keys','--fingerprint',str(key)],text=True,stderr=subprocess.PIPE)
        keys=[line.split(':')[9] for line in details.splitlines() if line.startswith('fpr:')]
        if not keys or keys[0]!=FPR:raise RuntimeError('Unexpected public archive key')
        signed=work/'InRelease';signed.write_bytes(get('/apt/dists/daylight/InRelease'))
        release=work/'Release'
        subprocess.run(['gpgv','--homedir',str(home),'--keyring',str(key),'--output',str(release),str(signed)],check=True,capture_output=True)
        text=release.read_text()
        until=next(line.split(': ',1)[1] for line in text.splitlines() if line.startswith('Valid-Until:'))
        if parsedate_to_datetime(until)<=datetime.now(timezone.utc):raise RuntimeError('Archive signature metadata expired')
        for arch in ['arm64','amd64']:
            name='main/binary-'+arch+'/Packages'
            line=next(line for line in text.split('SHA256:',1)[1].splitlines() if line.endswith(' '+name))
            digest,size,_=line.split()
            data=get('/apt/dists/daylight/'+name)
            if len(data)!=int(size) or hashlib.sha256(data).hexdigest()!=digest:raise RuntimeError('APT index checksum mismatch: '+arch)
            if b'Version: 5.0.0~rc2' not in data:raise RuntimeError('Published RC2 is missing')
        result={'result':'PASS','no_account_demo':True,'public_runtime_pinned':True,'archive_signature_verified':True,'archive_key':FPR,'checks':checks}
        output=ROOT/'dist/web-live-validation';output.mkdir(parents=True,exist_ok=True)
        (output/'access.json').write_text(json.dumps(result,indent=2)+'\n')
        print('PASS: '+str(len(checks))+' public HTTPS resources, graphical controls, pinned runtime/interface, APT key/signature/expiry and both architecture indexes.')


if __name__=='__main__':main()
