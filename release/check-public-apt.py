#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Verify public HTTPS/signatures/downloads without changing host APT configuration."""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile

BASE = 'https://daylightlinux.ch/apt'
FINGERPRINT = 'B0575F821A31DD20753DE07C50D21240F4BCB02E'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def configuration():
    return {str(p): digest(p) for p in Path('/etc/apt').rglob('*') if p.is_file() and os.access(p, os.R_OK)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--arch', choices=('amd64', 'arm64'), required=True)
    parser.add_argument('--expected-version')
    args = parser.parse_args()
    if os.geteuid() == 0:
        parser.error('Run unprivileged: this test needs no root access')
    before, identity = configuration(), digest(Path('/etc/os-release'))
    with tempfile.TemporaryDirectory(prefix='daylight-public-apt-') as temporary:
        root = Path(temporary)
        for name in ('gnupg', 'lists/partial', 'archives/partial', 'downloads', 'empty'):
            (root / name).mkdir(parents=True)
        (root / 'gnupg').chmod(0o700)
        for name in ('status', 'preferences'):
            (root / name).write_text('')
        for relative, name in [('daylight-archive-keyring.gpg', 'key.gpg'), ('dists/daylight/InRelease', 'InRelease')]:
            subprocess.run(['curl', '--disable', '--fail', '--silent', '--show-error', '--proto', '=https', '--max-time', '45', BASE + '/' + relative, '-o', str(root / name)], check=True)
        info = subprocess.check_output(['gpg', '--homedir', str(root / 'gnupg'), '--batch', '--with-colons', '--show-keys', str(root / 'key.gpg')], text=True)
        fingerprints = [line.split(':')[9] for line in info.splitlines() if line.startswith('fpr:')]
        if not fingerprints or fingerprints[0] != FINGERPRINT or sum(line.startswith('pub:') for line in info.splitlines()) != 1:
            raise RuntimeError('Unexpected public signing key')
        subprocess.run(['gpgv', '--homedir', str(root / 'gnupg'), '--keyring', str(root / 'key.gpg'), '--output', str(root / 'Release'), str(root / 'InRelease')], check=True)
        (root / 'daylight.sources').write_text(f'Types: deb\nURIs: {BASE}\nSuites: daylight\nComponents: main\nArchitectures: {args.arch}\nSigned-By: {root}/key.gpg\n')
        settings = {'Dir::Etc::sourcelist': root / 'daylight.sources', 'Dir::Etc::sourceparts': root / 'empty', 'Dir::Etc::preferencesparts': root / 'empty', 'Dir::Etc::preferences': root / 'preferences', 'Dir::State::status': root / 'status', 'Dir::State::lists': root / 'lists', 'Dir::Cache::archives': root / 'archives', 'Dir::Cache::pkgcache': root / 'pkgcache.bin', 'Dir::Cache::srcpkgcache': root / 'srcpkgcache.bin', 'APT::Architecture': args.arch, 'APT::Update::Error-Mode': 'any'}
        options = [argument for key, value in settings.items() for argument in ('-o', f'{key}={value}')]
        subprocess.run(['apt-get', *options, 'update'], check=True, timeout=90)
        subprocess.run(['apt-get', *options, 'download', 'daylight-core', 'daylight-themes'], cwd=root / 'downloads', check=True, timeout=90)
        packages = sorted((root / 'downloads').glob('*.deb'))
        if len(packages) != 2:
            raise RuntimeError('Expected two verified downloads')
        for package in packages:
            version = subprocess.check_output(['dpkg-deb', '-f', str(package), 'Version'], text=True).strip()
            architecture = subprocess.check_output(['dpkg-deb', '-f', str(package), 'Architecture'], text=True).strip()
            if args.expected_version and version != args.expected_version:
                raise RuntimeError('The public repository does not serve the expected version')
            if architecture not in (args.arch, 'all'):
                raise RuntimeError('Wrong package architecture')
            print('VERIFIED', args.arch, package.name, digest(package))
    if configuration() != before or digest(Path('/etc/os-release')) != identity:
        raise RuntimeError('Host configuration unexpectedly changed')
    print('DAYLIGHT_PUBLIC_APT_PASS: signed downloads verified; no host installation or APT configuration change.')


if __name__ == '__main__':
    main()
