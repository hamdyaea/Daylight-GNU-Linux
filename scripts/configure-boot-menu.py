#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Apply Daylight branding and an eight-second timeout to copied Debian templates."""
from pathlib import Path
import re
import shutil
import sys


def configure(root, background):
    if not root.is_dir() or not background.is_file():
        raise ValueError('Missing copied bootloader templates or rendered Daylight background')
    isolinux = root / 'isolinux' / 'isolinux.cfg'
    if not isolinux.is_file():
        raise ValueError('Unexpected live-build isolinux template layout')
    text = isolinux.read_text()
    if not re.search(r'^timeout\s+\d+', text, flags=re.M | re.I):
        raise ValueError('No reviewed isolinux timeout field')
    isolinux.write_text(re.sub(r'^timeout\s+\d+', 'timeout 80', text, flags=re.M | re.I))
    # Preserve the original bootloader templates and license notices; only adjust timeout.
    for path in root.rglob('*.cfg'):
        if 'grub' in str(path.relative_to(root)):
            text = path.read_text()
            text = re.sub(r'(?m)^(\s*set\s+timeout=)["\']?\d+["\']?\s*$', r'\g<1>8', text)
            path.write_text(text)
    for name in ('isolinux', 'syslinux'):
        directory = root / name
        if directory.is_dir():
            shutil.copyfile(background, directory / 'splash.png')
            (directory / 'splash.svg').unlink(missing_ok=True)
    print('Daylight ISO boot menu configured: native bootloader, eight-second timeout.')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('Usage: configure-boot-menu.py COPIED_TEMPLATE_DIR BACKGROUND.png')
    configure(Path(sys.argv[1]), Path(sys.argv[2]))
