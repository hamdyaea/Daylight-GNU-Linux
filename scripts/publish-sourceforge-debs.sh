#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
# Upload locally verified release DEBs to the existing free SourceForge project.
# Requires the operator's configured SourceForge SSH key and account.
set -Eeuo pipefail
: "${SF_USER:?Set SF_USER to your SourceForge login}"
: "${SF_PROJECT:=daylight-linux}"
: "${SF_RELEASE:=Daylight-GNU-Linux-5}"
: "${DEB_DIR:=dist}"
[[ "$SF_USER" =~ ^[a-zA-Z0-9_-]+$ ]] || { echo "Invalid SF_USER" >&2; exit 1; }
[[ "$SF_PROJECT" =~ ^[a-zA-Z0-9_-]+$ ]] || { echo "Invalid project" >&2; exit 1; }
[[ "$SF_RELEASE" =~ ^[a-zA-Z0-9_.-]+$ ]] || { echo "Invalid release" >&2; exit 1; }
shopt -s nullglob
files=("$DEB_DIR"/*.deb)
(("${#files[@]}" > 0)) || { echo "No .deb files in $DEB_DIR" >&2; exit 1; }
command -v rsync >/dev/null || { echo "rsync is required" >&2; exit 1; }
for f in "${files[@]}"; do dpkg-deb --info "$f" >/dev/null; done
# Do not overwrite already published files. Requires SourceForge SSH access.
remote="$SF_USER@frs.sourceforge.net:/home/frs/project/$SF_PROJECT/$SF_RELEASE/"
echo "SourceForge destination: $remote"
rsync -av --ignore-existing --checksum --progress -e 'ssh -o BatchMode=yes' "${files[@]}" "$remote"
