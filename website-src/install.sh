#!/bin/sh
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
# Download, inspect, then execute. A plan is printed unless --yes is explicit.
set -eu
PATH=/usr/sbin:/usr/bin:/sbin:/bin
export PATH
BASE=https://daylightlinux.ch/apt
FINGERPRINT=B0575F821A31DD20753DE07C50D21240F4BCB02E
mode=core
games=no
apply=no
usage() {
    printf '%s\n' 'Daylight GNU/Linux installer (Debian 12/13 and compatible ARM64 systems)' 'Usage: sh install-daylight.sh [--core|--desktop|--repo-only] [--games] [--yes|--plan]' 'Default: show the core-only installation plan; no changes.' 'Desktop selection never changes or starts your display manager.' 'Telemetry is never installed or enabled by this script.'
}
for argument in "$@"; do
    case "$argument" in
        --core) mode=core ;;
        --desktop) mode=desktop ;;
        --repo-only) mode=repo ;;
        --games) games=yes ;;
        --yes) apply=yes ;;
        --plan|--dry-run) apply=no ;;
        --help|-h) usage; exit 0 ;;
        *) printf 'Unknown option: %s\n' "$argument" >&2; exit 2 ;;
    esac
done
if [ "$games" = yes ] && [ "$mode" != desktop ]; then echo '--games requires --desktop' >&2; exit 2; fi
command -v dpkg >/dev/null 2>&1 || { echo 'This installer is only for Debian-based systems, not Arch/Manjaro.' >&2; exit 2; }
[ -r /etc/debian_version ] || { echo 'No Debian base detected; no changes made.' >&2; exit 2; }
arch=$(dpkg --print-architecture)
case "$arch" in amd64|arm64) ;; *) echo 'Supported architectures: amd64 and arm64 only.' >&2; exit 2 ;; esac
packages='daylight-core daylight-themes'
if [ "$mode" = desktop ]; then packages='daylight-linux'; fi
if [ "$mode" = repo ]; then packages=''; fi
if [ "$games" = yes ]; then packages="$packages daylight-games"; fi
printf 'Repository: %s\nSigning fingerprint: %s\nArchitecture: %s\nPackages: %s\n' "$BASE" "$FINGERPRINT" "$arch" "${packages:-repository configuration only}"
if [ "$apply" != yes ]; then echo 'Plan only. Add --yes to apply. No file, service or package was changed.'; exit 0; fi
[ "$(id -u)" -eq 0 ] || { echo 'Run the inspected script with sudo and --yes to apply.' >&2; exit 2; }
export DEBIAN_FRONTEND=noninteractive
missing=no
for tool in curl gpg gpgv; do command -v "$tool" >/dev/null 2>&1 || missing=yes; done
if [ "$missing" = yes ]; then
    apt-get -o APT::Update::Error-Mode=any update
    apt-get install --no-remove --no-install-recommends -y ca-certificates curl gnupg gpgv
fi
temporary=$(mktemp -d)
backup=
changed=no
success=no
source=/etc/apt/sources.list.d/daylight.sources
key=/etc/apt/keyrings/daylight-archive-keyring.gpg
pin=/etc/apt/preferences.d/daylight
cleanup() {
    code=$?
    if [ "$changed" = yes ] && [ "$success" != yes ]; then
        for name in source key pin; do
            case "$name" in source) destination=$source ;; key) destination=$key ;; pin) destination=$pin ;; esac
            if [ -f "$backup/$name" ]; then cp -p "$backup/$name" "$destination"; else rm -f "$destination"; fi
        done
        echo 'Daylight APT configuration restored after failure. Existing package/dependency changes, if any, are not a disk rollback.' >&2
    fi
    rm -rf "$temporary"
    exit "$code"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
mkdir -m 700 "$temporary/gnupg"
fetch() { curl --disable --fail --silent --show-error --location --proto '=https' --proto-redir '=https' --tlsv1.2 --retry 3 --connect-timeout 10 --max-time 90 "$1" -o "$2"; }
fetch "$BASE/daylight-archive-keyring.gpg" "$temporary/key.gpg"
gpg --homedir "$temporary/gnupg" --batch --with-colons --show-keys --fingerprint "$temporary/key.gpg" > "$temporary/key.info"
actual=$(awk -F: '$1=="fpr" {print $10;exit}' "$temporary/key.info")
count=$(awk -F: '$1=="pub" {n++} END {print n+0}' "$temporary/key.info")
[ "$actual" = "$FINGERPRINT" ] && [ "$count" = 1 ] || { echo 'Signing key does not match the pinned fingerprint; nothing installed.' >&2; exit 1; }
fetch "$BASE/dists/daylight/InRelease" "$temporary/InRelease"
gpgv --homedir "$temporary/gnupg" --keyring "$temporary/key.gpg" --output "$temporary/Release" "$temporary/InRelease"
grep -qx 'Origin: Daylight GNU/Linux' "$temporary/Release"
grep -qx 'Codename: daylight' "$temporary/Release"
for destination in "$source" "$key" "$pin"; do
    [ ! -L "$destination" ] || { echo 'Refusing to replace a symbolic-link configuration.' >&2; exit 1; }
done
for destination in "$source" "$pin"; do
    if [ -e "$destination" ] && ! grep -q '^# Managed by Daylight GNU/Linux installer$' "$destination"; then
        printf 'Refusing to overwrite existing unmanaged file: %s\n' "$destination" >&2; exit 1
    fi
done
if [ -e "$key" ] && [ ! -e "$source" ]; then echo 'Unmanaged Daylight key already exists; refusing to replace it.' >&2; exit 1; fi
mkdir -p /var/backups /etc/apt/keyrings /etc/apt/sources.list.d /etc/apt/preferences.d
backup=$(mktemp -d /var/backups/daylight-apt.XXXXXX)
for name in source key pin; do
    case "$name" in source) destination=$source ;; key) destination=$key ;; pin) destination=$pin ;; esac
    if [ -f "$destination" ]; then cp -p "$destination" "$backup/$name"; fi
done
cat > "$temporary/daylight.sources" <<EOF
# Managed by Daylight GNU/Linux installer
Types: deb
URIs: $BASE
Suites: daylight
Components: main
Architectures: $arch
Signed-By: $key
EOF
cat > "$temporary/preferences" <<'EOF'
# Managed by Daylight GNU/Linux installer
Package: daylight-*
Pin: origin daylightlinux.ch
Pin-Priority: 500

Package: *
Pin: origin daylightlinux.ch
Pin-Priority: -1
EOF
changed=yes
install -m 644 "$temporary/key.gpg" "$key"
install -m 644 "$temporary/daylight.sources" "$source"
install -m 644 "$temporary/preferences" "$pin"
# Authentication and expiry checking remain enabled, including all failures.
apt-get -o APT::Update::Error-Mode=any update
if [ -n "$packages" ]; then
    # Word splitting is deliberate: this is a fixed internal package allowlist.
    apt-get install --no-remove --no-install-recommends -y $packages
fi
success=yes
printf 'Daylight installation completed. Configuration backup: %s\n' "$backup"
printf '%s\n' 'No reboot, display-manager change, telemetry activation or autoremove was performed.' 'For a desktop installation, select Daylight GNU/Linux at your next graphical login.'
