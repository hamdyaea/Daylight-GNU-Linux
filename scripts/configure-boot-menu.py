#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Apply Daylight branding and explicit eight-second BIOS/UEFI menu timeouts."""
from pathlib import Path
import re
import shutil
import sys

GRUB_MARKER = '# Daylight GNU/Linux automatic live boot'
GRUB_SETTINGS = GRUB_MARKER + '\nset default=0\nset timeout_style=menu\nset timeout=8\n'


def grub_config(text):
    """Debian's shared config can contain no timeout at all: create it explicitly."""
    text = text.replace(GRUB_SETTINGS, '')
    text = re.sub(r'(?m)^[ \t]*set[ \t]+(?:timeout|timeout_style|default)=[^\n]*\n?', '', text)
    return text.rstrip() + '\n\n' + GRUB_SETTINGS


def configure(root, background):
    if not root.is_dir() or not background.is_file():
        raise ValueError('Missing copied bootloader templates or rendered Daylight background')
    isolinux = root / 'isolinux' / 'isolinux.cfg'
    if not isolinux.is_file():
        raise ValueError('Unexpected live-build isolinux template layout')
    text = isolinux.read_text()
    if not re.search(r'^timeout\s+\d+', text, flags=re.M | re.I):
        raise ValueError('No reviewed isolinux timeout field')
    # config.cfg is sourced by the real ISO grub.cfg before its menu entries.
    configs = [p for p in root.rglob('config.cfg') if any(part.startswith('grub') for part in p.relative_to(root).parts[:-1])]
    if not configs:
        raise ValueError('No shared GRUB config.cfg template; refuse an unverified UEFI menu')
    isolinux.write_text(re.sub(r'^timeout\s+\d+', 'timeout 80', text, flags=re.M | re.I))
    for path in configs:
        path.write_text(grub_config(path.read_text()))
        print('Configured GRUB template:', path.relative_to(root))
    for name in ('isolinux', 'syslinux'):
        directory = root / name
        if directory.is_dir():
            shutil.copyfile(background, directory / 'splash.png')
            (directory / 'splash.svg').unlink(missing_ok=True)
    print('Daylight native BIOS/UEFI menus configured: eight-second timeout, first live entry.')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('Usage: configure-boot-menu.py COPIED_TEMPLATE_DIR BACKGROUND.png')
    configure(Path(sys.argv[1]), Path(sys.argv[2]))
