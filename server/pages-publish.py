#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein | Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Publish public generated files with repository-specific deploy keys."""
import fcntl,os,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
from email.utils import parsedate_to_datetime
BASE=Path('/var/lib/pages-publisher');BRANCH='publish/cloudflare-pages-20261103'
NAME=sys.argv[1] if len(sys.argv)==2 else ''
if NAME not in ('astro','daylight'):raise SystemExit('Expected astro or daylight')
repo=BASE/'repos'/NAME
env={**os.environ,'GIT_TERMINAL_PROMPT':'0','GIT_SSH_COMMAND':f'ssh -i {BASE}/keys/{NAME} -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o UserKnownHostsFile={BASE}/known_hosts -o ConnectTimeout=20'}
def run(*args):return subprocess.run(args,cwd=repo,env=env,check=True,text=True,timeout=180)
with (BASE/(NAME+'.lock')).open('w') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 if subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True,env=env):raise SystemExit('Uncommitted changes: inspect without resetting')
 run('git','pull','--ff-only','origin',BRANCH)
 if NAME=='astro':
  run('/usr/bin/python3','scripts/build-pages.py');paths=['public-site']
 else:
  source=Path('/var/www/daylightlinux/apt')
  run('gpgv','--keyring',str(source/'daylight-archive-keyring.gpg'),str(source/'dists/daylight/InRelease'))
  release=(source/'dists/daylight/Release').read_text()
  expires=next(l.split(':',1)[1].strip() for l in release.splitlines() if l.startswith('Valid-Until:'))
  if parsedate_to_datetime(expires)<=datetime.now(timezone.utc):raise SystemExit('Expired APT metadata')
  target=repo/'website-src/apt';target.mkdir(parents=True,exist_ok=True)
  run('rsync','-a','--copy-links','--delete','--exclude=.releases/',str(source)+'/',str(target)+'/')
  if any(p.is_symlink() for p in target.rglob('*')):raise SystemExit('Deployment must contain regular files')
  run('gpgv','--keyring',str(target/'daylight-archive-keyring.gpg'),str(target/'dists/daylight/InRelease'))
  paths=['website-src/apt']
 run('git','add','-f','--',*paths)
 changed=subprocess.run(['git','diff','--cached','--quiet'],cwd=repo,env=env)
 if changed.returncode==0:print('No public file changes.');raise SystemExit(0)
 if changed.returncode!=1:raise SystemExit('Cannot compare generated files')
 run('git','-c','user.name=Hamdy Abou El Anein','-c','user.email=info@daylightlinux.ch','commit','-m','Refresh '+('daily orbital catalogue' if NAME=='astro' else 'signed APT metadata'))
 run('git','push','origin',BRANCH)
 print('Published',NAME,subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip())
