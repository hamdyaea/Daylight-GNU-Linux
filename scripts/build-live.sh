#!/bin/sh
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
set -eu
if [ "$(id -u)" -ne 0 ]; then echo 'Run inside a disposable Debian live-build VM/container as root; never on a production server.' >&2; exit 2; fi
command -v lb >/dev/null
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
work=$(mktemp -d /var/tmp/daylight-live.XXXXXX)
echo "Disposable live-build work directory: $work"
cp -a "$root/live/auto" "$work/auto"
cp -a "$root/live/config" "$work/config"
mkdir -p "$work/config/packages.chroot" "$root/dist"
for package in core desktop themes apps games linux; do
  case "$package" in core) arch=amd64 ;; *) arch=all ;; esac
  source="$root/dist/daylight-${package}_5.0.0~rc4-1_${arch}.deb"
  test -s "$source"
  cp "$source" "$work/config/packages.chroot/"
done
# Copy the distribution bootloader templates, then apply small documented overrides.
cp -a /usr/share/live/build/bootloaders "$work/config/bootloaders"
python3 "$root/scripts/configure-boot-menu.py" "$work/config/bootloaders" "$root/assets/branding/boot-splash.png"
cd "$work"
lb config
lb build
cp live-image-amd64.hybrid.iso "$root/dist/daylight-live_5.0.0-rc.4_amd64.iso"
cd "$root/dist"
sha256sum daylight-live_5.0.0-rc.4_amd64.iso > daylight-live_5.0.0-rc.4_amd64.iso.sha256
printf 'ISO created. Build directory retained for inspection: %s\n' "$work"
