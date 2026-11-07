#!/usr/bin/env python3
"""Read-only option matrix; run on Debian against a downloaded installer."""
import subprocess, sys
script=sys.argv[1]
cases=[([],0,'Packages: daylight-core daylight-themes'),(['--help'],0,'daylight-install.sh'),(['-h'],0,'daylight-install.sh'),(['--core','--plan'],0,'Packages: daylight-core daylight-themes'),(['--desktop','--plan'],0,'Packages: daylight-linux\n'),(['--all','--plan'],0,'Packages: daylight-linux daylight-games'),(['--desktop','--games','--plan'],0,'Packages: daylight-linux daylight-games'),(['--games','--desktop','--plan'],0,'Packages: daylight-linux daylight-games'),(['--all','--games','--plan'],0,'Packages: daylight-linux daylight-games'),(['--repo-only','--plan'],0,'repository configuration only'),(['--remove-repo','--plan'],0,'Plan: clean'),(['--all','--dry-run'],0,'Plan only'),(['--all','--yes','--plan'],0,'Plan only'),(['--all','--yes','--dry-run'],0,'Plan only'),(['--games'],2,'requires --desktop'),(['--core','--games'],2,'requires --desktop'),(['--repo-only','--games'],2,'requires --desktop'),(['--remove-repo','--games'],2,'requires --desktop'),(['--unknown'],2,'Unknown option')]
for args,code,expected in cases:
 r=subprocess.run(['sh',script,*args],text=True,capture_output=True,timeout=15)
 assert r.returncode==code and expected in r.stdout+r.stderr,(args,r.returncode,r.stdout,r.stderr)
 print('PASS', ' '.join(args) or '(default)',flush=True)
print(f'{len(cases)} option checks passed')
