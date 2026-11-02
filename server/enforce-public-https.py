#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Redirect public HTTP behind the existing proxy, only for the Daylight vhost."""
import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import subprocess
BEGIN='    # BEGIN DAYLIGHT PUBLIC HTTPS\n'
BLOCK=BEGIN+'    # X-Forwarded-Proto is set by the existing HTTPS-terminating proxy.\n    # Local origin requests without this header remain available for diagnostics.\n    RewriteEngine On\n    RewriteCond %{HTTP:X-Forwarded-Proto} ^http$ [NC]\n    RewriteRule ^ https://daylightlinux.ch%{REQUEST_URI} [R=308,L,NE]\n    # END DAYLIGHT PUBLIC HTTPS\n'
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    target=Path('/etc/apache2/sites-enabled/daylightlinux.conf').resolve()
    if target!=Path('/etc/apache2/sites-available/daylightlinux.conf'):
        raise SystemExit('Unexpected virtual-host path')
    original=target.read_text()
    if BLOCK in original:
        print('Scoped public HTTPS redirect already present.');return
    if BEGIN in original or original.count('<VirtualHost')!=1 or original.count('</VirtualHost>')!=1 or 'DocumentRoot /var/www/daylightlinux' not in original:
        raise SystemExit('Unexpected configuration; unchanged')
    modules=subprocess.check_output(['/usr/sbin/apache2ctl','-M'],text=True,stderr=subprocess.PIPE)
    if 'rewrite_module' not in modules:raise SystemExit('Existing mod_rewrite is required; nothing enabled globally')
    if not args.apply:
        print('Plan: public HTTP -> HTTPS for Daylight only; local origin and other vhosts unchanged.');return
    if os.geteuid()!=0:raise SystemExit('Root required for explicit application')
    subprocess.run(['/usr/sbin/apache2ctl','configtest'],check=True)
    backup=Path('/var/backups/daylight-apache')/('https-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    backup.mkdir(parents=True,mode=0o700);shutil.copy2(target,backup/target.name)
    temporary=target.with_name('.daylight-https.new')
    temporary.write_text(original.replace('</VirtualHost>',BLOCK+'</VirtualHost>'))
    temporary.chmod(target.stat().st_mode & 0o777);temporary.replace(target)
    try:
        subprocess.run(['/usr/sbin/apache2ctl','configtest'],check=True)
        subprocess.run(['/usr/bin/systemctl','reload','apache2'],check=True)
    except Exception:
        shutil.copy2(backup/target.name,target)
        subprocess.run(['/usr/sbin/apache2ctl','configtest'],check=True)
        subprocess.run(['/usr/bin/systemctl','reload','apache2'],check=True)
        raise
    print('Daylight public HTTP redirected to HTTPS. Graceful reload, no restart. Backup:',backup)
if __name__=='__main__':main()
