#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Build authenticated APT metadata; never modify a client APT configuration."""
import argparse
from datetime import datetime, timedelta, timezone
import gzip
import hashlib
from pathlib import Path
import re
import shutil
import subprocess

ALLOWED = {'daylight-core', 'daylight-desktop', 'daylight-themes', 'daylight-apps', 'daylight-games', 'daylight-telemetry', 'daylight-linux'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packages', type=Path, default=Path('dist'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--signing-key', required=True)
    parser.add_argument('--valid-days', type=int, default=30)
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Fa-f0-9]{40}|[A-Fa-f0-9]{64}', args.signing_key):
        parser.error('Use a complete signing-key fingerprint')
    if not 1 <= args.valid_days <= 90:
        parser.error('Metadata validity must be 1..90 days')
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        parser.error('Output must be empty; existing repositories are never overwritten')
    packages = sorted(args.packages.glob('daylight-*.deb'))
    if not packages:
        parser.error('No Daylight packages found')
    seen = set()
    for path in packages:
        if path.is_symlink() or not path.is_file():
            parser.error('Package inputs must be regular files')
        fields = subprocess.check_output(['dpkg-deb', '-f', str(path), 'Package', 'Version', 'Architecture'], text=True)
        metadata = dict(line.split(': ', 1) for line in fields.strip().splitlines())
        identity = (metadata['Package'], metadata['Version'], metadata['Architecture'])
        if identity[0] not in ALLOWED or identity[2] not in ('amd64', 'arm64', 'all') or identity in seen:
            parser.error('Unexpected or duplicate package identity: ' + str(identity))
        seen.add(identity)
    pool = output / 'pool/main/d/daylight'
    pool.mkdir(parents=True)
    for package in packages:
        shutil.copyfile(package, pool / package.name)
    suite = output / 'dists/daylight'
    for arch in ('amd64', 'arm64'):
        dest = suite / ('main/binary-' + arch)
        dest.mkdir(parents=True)
        records = subprocess.check_output(['dpkg-scanpackages', '--multiversion', '--arch', arch, 'pool'], cwd=output)
        for name, data in [('Packages', records), ('Packages.gz', gzip.compress(records, mtime=0))]:
            (dest / name).write_bytes(data)
            digest = hashlib.sha256(data).hexdigest()
            by_hash = dest / 'by-hash/SHA256'
            by_hash.mkdir(parents=True, exist_ok=True)
            (by_hash / digest).write_bytes(data)
    now = datetime.now(timezone.utc)
    fmt = '%a, %d %b %Y %H:%M:%S +0000'
    release = 'Origin: Daylight GNU/Linux\nLabel: Daylight GNU/Linux\nSuite: daylight\nCodename: daylight\nArchitectures: amd64 arm64\nComponents: main\nAcquire-By-Hash: yes\nNotAutomatic: yes\nButAutomaticUpgrades: yes\n'
    release += f'Date: {now.strftime(fmt)}\nValid-Until: {(now + timedelta(days=args.valid_days)).strftime(fmt)}\nDescription: Daylight GNU/Linux candidate packages\nSHA256:\n'
    for item in sorted(suite.rglob('Packages*')):
        data = item.read_bytes()
        release += f' {hashlib.sha256(data).hexdigest()} {len(data)} {item.relative_to(suite)}\n'
    (suite / 'Release').write_text(release)
    key = args.signing_key.upper()
    subprocess.run(['gpg', '--batch', '--local-user', key, '--digest-algo', 'SHA256', '--clearsign', '--output', str(suite / 'InRelease'), str(suite / 'Release')], check=True)
    subprocess.run(['gpg', '--batch', '--local-user', key, '--digest-algo', 'SHA256', '--armor', '--detach-sign', '--output', str(suite / 'Release.gpg'), str(suite / 'Release')], check=True)
    with (output / 'daylight-archive-keyring.gpg').open('wb') as stream:
        subprocess.run(['gpg', '--batch', '--export-options', 'export-minimal', '--export', key], stdout=stream, check=True)
    subprocess.run(['gpgv', '--keyring', str(output / 'daylight-archive-keyring.gpg'), str(suite / 'InRelease')], check=True)
    print('Signed repository created:', output)


if __name__ == '__main__':
    main()
