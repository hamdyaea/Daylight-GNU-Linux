#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: contact@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Refresh Daylight metadata atomically, without network access or package upgrades."""
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

STATE = Path('/var/lib/daylight-archive')
WEB = Path('/var/www/daylightlinux/apt')
BUILDER = Path('/usr/local/lib/daylight-archive/build-apt-repository.py')
FINGERPRINT = 'B0575F821A31DD20753DE07C50D21240F4BCB02E'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    os.umask(0o022)
    with (STATE / 'refresh.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with tempfile.TemporaryDirectory(prefix='publish-', dir=STATE / 'work') as temporary:
            stage = Path(temporary) / 'apt'
            env = dict(os.environ, GNUPGHOME=str(STATE / 'gnupg'), LC_ALL='C')
            subprocess.run(['python3', str(BUILDER), '--packages', str(STATE / 'packages'), '--output', str(stage), '--signing-key', FINGERPRINT], env=env, check=True)
            current = WEB / 'dists'
            # Preserve prior content-addressed indexes for clients racing a publication.
            if current.exists():
                if not current.is_symlink():
                    raise RuntimeError('Existing dists is unmanaged; refusing to replace it')
                for old in current.glob('daylight/main/binary-*/by-hash/SHA256/*'):
                    target = stage / 'dists' / old.relative_to(current)
                    if not target.exists():
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copyfile(old, target)
            for source in (stage / 'pool').rglob('*.deb'):
                target = WEB / source.relative_to(stage)
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists():
                    if sha(target) != sha(source):
                        raise RuntimeError('An already published package name has different bytes: ' + target.name)
                else:
                    temporary_file = target.with_name('.' + target.name + '.new')
                    shutil.copyfile(source, temporary_file)
                    temporary_file.replace(target)
            key = WEB / 'daylight-archive-keyring.gpg'
            new_key = stage / key.name
            if key.exists() and sha(key) != sha(new_key):
                raise RuntimeError('Unexpected key change; a reviewed rotation is required')
            if not key.exists():
                shutil.copyfile(new_key, key)
            stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
            releases = WEB / '.releases'
            releases.mkdir(exist_ok=True)
            generation = releases / stamp
            generation.mkdir()
            shutil.move(str(stage / 'dists'), str(generation / 'dists'))
            link = WEB / ('.dists-' + stamp)
            link.symlink_to(Path('.releases') / stamp / 'dists', target_is_directory=True)
            link.replace(current)
            status = {'signed_at': datetime.now(timezone.utc).isoformat(), 'validity_days': 30, 'fingerprint': FINGERPRINT, 'architectures': ['amd64', 'arm64'], 'packages': len(list((STATE / 'packages').glob('*.deb')))}
            status_file = WEB / '.status.new'
            status_file.write_text(json.dumps(status, indent=2) + '\n')
            status_file.replace(WEB / 'status.json')
            # Keep generations for 35 days, longer than signed metadata validity.
            for previous in releases.iterdir():
                if previous != generation and previous.is_dir() and not previous.is_symlink():
                    age = datetime.now(timezone.utc).timestamp() - previous.stat().st_mtime
                    if age > 35 * 86400:
                        shutil.rmtree(previous)
            print('Daylight archive refreshed; signature verified; generation', stamp)


if __name__ == '__main__':
    main()
