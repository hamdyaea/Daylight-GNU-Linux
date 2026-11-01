#!/bin/sh
# Developer: Hamdy Abou El Anein
# Contact: contact@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$root"
if command -v magick >/dev/null; then renderer=magick; else renderer=convert; fi
for name in daylight-mountains daylight-night; do
 "$renderer" "assets/wallpapers/$name.svg" -quality 88 "assets/wallpapers/$name.jpg"
done
"$renderer" assets/wallpapers/daylight-night.jpg -fill '#080d15' -colorize 58 assets/wallpapers/daylight-terminal.jpg
"$renderer" -background none assets/branding/daylight.svg assets/branding/daylight.png
