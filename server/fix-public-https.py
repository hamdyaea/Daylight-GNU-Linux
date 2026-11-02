#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Correct only Daylight's canonical redirects behind its HTTPS reverse proxy."""
import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import subprocess


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    path=Path('/etc/apache2/sites-enabled/daylightlinux.conf').resolve()
    if path.parent!=Path('/etc/apache2/sites-available') or path.name!='daylightlinux.conf':
        raise SystemExit('Unexpected Daylight virtual-host location')
    old=path.read_text()
    if 'DocumentRoot /var/www/daylightlinux' not in old or old.count('<VirtualHost')!=1:
        raise SystemExit('Unexpected virtual-host scope; refusing to edit')
    before='    ServerName daylightlinux.ch\n'
    after='    # Public HTTPS is terminated by the existing reverse proxy.\n    ServerName https://daylightlinux.ch:443\n    UseCanonicalName On\n    UseCanonicalPhysicalPort Off\n'
    if after in old:
        print('Canonical HTTPS redirects are already configured. No change.')
        return
    if old.count(before)!=1 or 'UseCanonicalName' in old:
        raise SystemExit('Existing canonical-host settings need review')
    print('Only Daylight ServerName/canonical redirect directives will change.')
    if not args.apply:
        print('Plan only. No configuration or service changed.')
        return
    if os.geteuid()!=0:raise SystemExit('Root required for explicit virtual-host change')
    subprocess.run(['/usr/sbin/apache2ctl','configtest'],check=True)
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup=Path('/var/backups/daylight-apache')/stamp
    backup.mkdir(mode=0o700,parents=True)
    shutil.copy2(path,backup/path.name)
    temporary=path.with_name('.'+path.name+'.daylight-new')
    temporary.write_text(old.replace(before,after));temporary.chmod(path.stat().st_mode & 0o777)
    temporary.replace(path)
    try:
        subprocess.run(['/usr/sbin/apache2ctl','configtest'],check=True)
        subprocess.run(['/usr/bin/systemctl','reload','apache2'],check=True)
    except Exception:
        shutil.copy2(backup/path.name,path)
        subprocess.run(['/usr/sbin/apache2ctl','configtest'],check=True)
        subprocess.run(['/usr/bin/systemctl','reload','apache2'],check=True)
        raise
    print('Daylight canonical HTTPS configured; Apache gracefully reloaded, not restarted.')
    print('Prior configuration retained in',backup)


if __name__=='__main__':main()
