#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: contact@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Extract package provenance from the tested ISO without executing its contents."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import tempfile
from urllib.parse import quote


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('iso', type=Path)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[0-9a-f]{40}', args.commit):
        parser.error('An exact source commit is required')
    with tempfile.TemporaryDirectory(prefix='daylight-provenance-') as temporary:
        squash = Path(temporary)/'filesystem.squashfs'
        subprocess.run(['xorriso', '-osirrox', 'on', '-indev', str(args.iso.resolve()),
                        '-extract', '/live/filesystem.squashfs', str(squash)], check=True)
        status = subprocess.check_output(['unsquashfs', '-cat', str(squash),
                                          'var/lib/dpkg/status'], text=True)
    packages = []
    for paragraph in status.strip().split('\n\n'):
        fields = {}
        for line in paragraph.splitlines():
            if line and not line[0].isspace() and ': ' in line:
                key, value = line.split(': ', 1)
                fields[key] = value
        if fields.get('Status') != 'install ok installed':
            continue
        name, version = fields['Package'], fields['Version']
        source = re.fullmatch(r'([^ ()]+)(?: \(([^()]+)\))?', fields.get('Source', name))
        if source is None:
            raise ValueError('Unexpected source metadata for '+name)
        source_name, source_version = source.group(1), source.group(2) or version
        own = name.startswith('daylight-')
        reference = ('https://github.com/hamdyaea/Daylight-GNU-Linux/tree/'+args.commit if own else
                     'https://snapshot.debian.org/package/'+quote(source_name, safe='')+'/'+quote(source_version, safe='')+'/')
        packages.append({'package': name, 'version': version,
                         'architecture': fields.get('Architecture', 'unknown'),
                         'source_package': source_name, 'source_version': source_version,
                         'source_reference': reference})
    packages.sort(key=lambda p: p['package'])
    if not packages or not any(p['package']=='daylight-core' for p in packages):
        raise ValueError('The image does not contain the expected installed Daylight packages')
    args.output.mkdir(parents=True, exist_ok=True)
    document = {'iso': args.iso.name, 'daylight_commit': args.commit,
                'note': 'Exact installed package metadata; Debian source archive references are generated, not individually fetched or validated by this script. Third-party copyright notices remain in the live image.',
                'packages': packages}
    (args.output/'daylight-live-packages.json').write_text(json.dumps(document, indent=2)+'\n')
    header = ['package','version','architecture','source_package','source_version','source_reference']
    lines = ['\t'.join(header)] + ['\t'.join(p[k] for k in header) for p in packages]
    (args.output/'daylight-live-sources.tsv').write_text('\n'.join(lines)+'\n')
    print('Recorded exact installed package provenance for',len(packages),'packages.')


if __name__ == '__main__':
    main()
