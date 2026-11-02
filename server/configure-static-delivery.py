#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Keep the reviewed Daylight HTML unchanged through proxies; no global configuration."""
import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import subprocess

BEGIN = '    # BEGIN DAYLIGHT UNMODIFIED HTML\n'
END = '    # END DAYLIGHT UNMODIFIED HTML\n'
BLOCK = BEGIN + '''    # Prevent injected analytics/email scripts from violating the page CSP.
    # Public static HTML must revalidate; large binary payload policy is unchanged.
    <Directory /var/www/daylightlinux>
        <FilesMatch "\\.html$">
            Header always set Cache-Control "public, max-age=0, must-revalidate, no-transform"
        </FilesMatch>
    </Directory>
''' + END


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    path=Path('/etc/apache2/sites-enabled/daylightlinux.conf').resolve()
    if path.parent!=Path('/etc/apache2/sites-available') or path.name!='daylightlinux.conf':
        raise SystemExit('Unexpected Daylight virtual-host path')
    text=path.read_text()
    if text.count('<VirtualHost')!=1 or 'DocumentRoot /var/www/daylightlinux' not in text:
        raise SystemExit('Unexpected virtual-host scope')
    if BLOCK in text:
        print('The reviewed no-transform HTML policy is already configured.')
        return
    if BEGIN in text or END in text or text.count('</VirtualHost>')!=1:
        raise SystemExit('Existing delivery policy needs review; no changes made')
    modules=subprocess.check_output(['/usr/sbin/apache2ctl','-M'],text=True,stderr=subprocess.PIPE)
    if 'headers_module' not in modules:raise SystemExit('mod_headers must already be loaded')
    print('Scope: only public HTML in the Daylight document root. CSP remains strict.')
    if not args.apply:
        print('Plan only; no files or services changed.')
        return
    if os.geteuid()!=0:raise SystemExit('Root required for the explicit vhost edit')
    subprocess.run(['/usr/sbin/apache2ctl','configtest'],check=True)
    backup=Path('/var/backups/daylight-apache')/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup.mkdir(parents=True,mode=0o700)
    shutil.copy2(path,backup/path.name)
    temporary=path.with_name('.'+path.name+'.delivery-new')
    temporary.write_text(text.replace('</VirtualHost>',BLOCK+'</VirtualHost>'))
    temporary.chmod(path.stat().st_mode & 0o777)
    temporary.replace(path)
    try:
        subprocess.run(['/usr/sbin/apache2ctl','configtest'],check=True)
        subprocess.run(['/usr/bin/systemctl','reload','apache2'],check=True)
    except Exception:
        shutil.copy2(backup/path.name,path)
        subprocess.run(['/usr/sbin/apache2ctl','configtest'],check=True)
        subprocess.run(['/usr/bin/systemctl','reload','apache2'],check=True)
        raise
    print('Daylight HTML transformations disabled. Apache gracefully reloaded; no restart.')
    print('Previous configuration:',backup)


if __name__=='__main__':main()
