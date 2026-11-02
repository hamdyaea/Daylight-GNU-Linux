#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Deploy reviewed static pages, preserving the old website and unrelated services."""
import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil

WEB = Path('/var/www/daylightlinux')
ALLOWED = {'.html', '.css', '.js', '.json', '.svg', '.png', '.jpg', '.webp', '.txt', '.xml', '.gpg', '.asc', '.zip', '.sh'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    source = args.source.resolve()
    if source == WEB or WEB in source.parents or source in WEB.parents:
        parser.error('Source and destination must be separate trees')
    if not (source / 'index.html').is_file() or not (source / 'install.html').is_file():
        parser.error('A complete generated static site is required')
    files = []
    for path in source.rglob('*'):
        if path.is_symlink():
            parser.error('Source symlinks are not allowed')
        if path.is_file():
            rel = path.relative_to(source)
            if rel.parts[0] == 'live':
                continue  # Separately validated runtime, managed by deploy-web-live.py.
            if path.suffix not in ALLOWED or any(p.startswith('.') for p in rel.parts) or rel.parts[0] == 'apt':
                parser.error('Unexpected static publication path: ' + str(rel))
            files.append((path, rel))
    print(f'Reviewed static files: {len(files)}. Destination: {WEB}')
    if not args.apply:
        print('Plan only; no changes.')
        return
    if os.geteuid() != 0:
        raise SystemExit('Root is required for this explicit production-site deployment')
    if not WEB.is_dir() or WEB.is_symlink():
        raise SystemExit('Expected existing document-root directory, not a symlink')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = Path('/var/backups/daylight-site') / stamp
    shutil.copytree(WEB, backup, symlinks=True, ignore=shutil.ignore_patterns('apt', 'old', 'live'))
    archive = WEB / 'old/site'
    if not archive.exists():
        shutil.copytree(backup, archive, symlinks=True)
    # Each page is atomically replaced; versioned assets are copied before pages.
    for path, rel in sorted(files, key=lambda item: item[0].suffix == '.html'):
        destination = WEB / rel
        if destination.is_symlink() or WEB not in destination.resolve().parents:
            raise RuntimeError('Destination escapes the document root: ' + str(rel))
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_name('.' + destination.name + '.daylight-new')
        shutil.copyfile(path, temporary)
        temporary.chmod(0o644)
        temporary.replace(destination)
    print('Site published. Backup:', backup)
    print('Historical site: /old/site/. No services were restarted; APT and other domains were untouched.')


if __name__ == '__main__':
    main()
