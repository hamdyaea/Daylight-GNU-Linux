#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
# Synchronize official APT .deb files to free SourceForge project file hosting.
# Designed for a trusted maintainer's Manjaro machine with SSH access to Raspberry Pi and SourceForge.
set -Eeuo pipefail
export LC_ALL=C
: "${PI_HOST:=hamdy@192.168.0.17}"
: "${PI_PORT:=22000}"
: "${PI_KEY:=$HOME/.ssh/id_rsa_pi}"
: "${SF_USER:=daylight-linux}"
: "${SF_KEY:=$HOME/.ssh/id_ed25519}"
: "${SF_PROJECT:=daylight-linux}"
: "${SF_RELEASE:=Daylight-GNU-Linux-5}"
: "${STATE_DIR:=$HOME/.local/state/daylight-sourceforge}"
for bin in rsync dpkg-deb flock sha256sum; do command -v "$bin" >/dev/null; done
mkdir -p "$STATE_DIR"
exec 9>"$STATE_DIR/.lock"
flock -n 9 || exit 0
mkdir -p "$STATE_DIR/pool"
# Only copy .deb from the official Pi APT pool; never publish an unvalidated build directory.
rsync -rt --include='*/' --include='*.deb' --exclude='*' \
  -e "ssh -i $PI_KEY -p $PI_PORT -o BatchMode=yes" \
  "$PI_HOST:/var/www/daylightlinux/apt/pool/" "$STATE_DIR/pool/"
mapfile -d '' files < <(find "$STATE_DIR/pool" -type f -name '*.deb' -print0)
(("${#files[@]}" > 0)) || { echo "No official APT .deb packages found" >&2; exit 1; }
for file in "${files[@]}"; do dpkg-deb --info "$file" >/dev/null; done
remote="$SF_USER@frs.sourceforge.net:/home/frs/project/$SF_PROJECT/$SF_RELEASE/"
rsync -rtv --ignore-existing -e "ssh -i $SF_KEY -o BatchMode=yes" "${files[@]}" "$remote"
# Compare full content against remote; exit nonzero if the remote differs.
rsync -rtcn --out-format='%n' -e "ssh -i $SF_KEY -o BatchMode=yes" "${files[@]}" "$remote" > "$STATE_DIR/differences"
if [[ -s "$STATE_DIR/differences" ]]; then
  cat "$STATE_DIR/differences" >&2
  echo "SourceForge checksum verification failed" >&2
  exit 1
fi
printf '%s SourceForge sync verified: %s packages\n' "$(date -u +%FT%TZ)" "${#files[@]}"
