#!/bin/sh
# Developer: Hamdy Abou El Anein
# Contact: contact@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$root"
if command -v magick >/dev/null; then renderer=magick; else renderer=convert; fi
python3 scripts/render-photography.py
"$renderer" -background none assets/branding/daylight.svg assets/branding/daylight.png
