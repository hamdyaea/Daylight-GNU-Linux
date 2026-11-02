#!/bin/sh
# Developer: Hamdy Abou El Anein
# Contact: contact@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
# Installs only a static signed archive and a low-resource local signing timer.
set -eu
PATH=/usr/sbin:/usr/bin:/sbin:/bin
export PATH
usage() { echo 'Usage: sudo sh server/install-apt-server.sh --packages DIR --key-home DIR --apply'; }
packages=
keyhome=
apply=no
while [ "$#" -gt 0 ]; do
 case "$1" in
  --packages) packages=${2:?Missing packages directory}; shift 2 ;;
  --key-home) keyhome=${2:?Missing key directory}; shift 2 ;;
  --apply) apply=yes; shift ;;
  --help) usage; exit 0 ;;
  *) usage >&2; exit 2 ;;
 esac
done
[ "$apply" = yes ] || { usage; echo 'No changes made.'; exit 0; }
[ "$(id -u)" -eq 0 ] || { echo 'Root is required for the explicit server installation.' >&2; exit 2; }
[ -n "$packages" ] && [ -n "$keyhome" ] || { usage >&2; exit 2; }
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
packages=$(CDPATH= cd -- "$packages" && pwd)
keyhome=$(CDPATH= cd -- "$keyhome" && pwd)
for tool in gpg gpgv dpkg-scanpackages python3 runuser systemctl; do command -v "$tool" >/dev/null; done
[ -d /var/www/daylightlinux ] || { echo 'Expected existing Daylight Apache document root is missing.' >&2; exit 1; }
[ ! -L /var/www/daylightlinux/apt ] || { echo 'Refusing an unexpected APT-root symlink.' >&2; exit 1; }
[ -s "$packages/PACKAGE-SHA256SUMS" ] || { echo 'Verified package checksum manifest is required.' >&2; exit 1; }
(cd "$packages" && sha256sum -c PACKAGE-SHA256SUMS)
# Validate manifest paths before copying anything to a privileged location.
python3 - "$packages" <<'PY'
import pathlib,re,sys
base=pathlib.Path(sys.argv[1])
lines=(base/'PACKAGE-SHA256SUMS').read_text().splitlines()
if len(lines)!=8: raise SystemExit('Expected exactly eight reviewed Daylight package files')
for line in lines:
 digest,name=line.split(None,1);name=name.strip().lstrip('*')
 if not re.fullmatch('[a-f0-9]{64}',digest) or not re.fullmatch(r'daylight-[a-z-]+_[A-Za-z0-9.~+-]+_(?:all|amd64|arm64)\.deb',name): raise SystemExit('Invalid manifest path')
 if (base/name).is_symlink(): raise SystemExit('Symlink package input rejected')
PY
fingerprint=$(gpg --homedir "$keyhome" --batch --with-colons --list-secret-keys 2>/dev/null | awk -F: '$1=="fpr"{print $10;exit}')
[ "$fingerprint" = B0575F821A31DD20753DE07C50D21240F4BCB02E ] || { echo 'Unexpected archive signing key.' >&2; exit 1; }
state=/var/lib/daylight-archive
if id daylight-archive >/dev/null 2>&1; then
 [ "$(getent passwd daylight-archive | cut -d: -f6)" = "$state" ] || { echo 'Existing service account has an unexpected home.' >&2; exit 1; }
else
 useradd --system --user-group --home-dir "$state" --shell /usr/sbin/nologin daylight-archive
fi
install -d -m 755 "$state" "$state/packages" /usr/local/lib/daylight-archive /var/www/daylightlinux/apt
install -d -m 700 -o daylight-archive -g daylight-archive "$state/gnupg"
install -d -m 755 -o daylight-archive -g daylight-archive "$state/work"
if [ ! -e "$state/gnupg/pubring.kbx" ]; then
 cp -a "$keyhome/private-keys-v1.d" "$keyhome/pubring.kbx" "$state/gnupg/"
 chown -R daylight-archive:daylight-archive "$state/gnupg"
 chmod 700 "$state/gnupg" "$state/gnupg/private-keys-v1.d"
 find "$state/gnupg/private-keys-v1.d" -type f -exec chmod 600 {} \;
fi
# The reviewed key remains in its original mode-0700 staging directory as an owner backup.
for file in "$packages"/daylight-*.deb; do
 destination="$state/packages/$(basename "$file")"
 if [ -f "$destination" ]; then cmp "$file" "$destination" >/dev/null || { echo 'Refusing to overwrite an existing package version.' >&2; exit 1; }; else install -m 644 "$file" "$destination"; fi
done
install -m 644 "$root/scripts/build-apt-repository.py" /usr/local/lib/daylight-archive/build-apt-repository.py
install -m 644 "$root/server/refresh-apt.py" /usr/local/lib/daylight-archive/refresh-apt.py
install -m 644 "$root/server/daylight-archive-refresh.service" /etc/systemd/system/daylight-archive-refresh.service
install -m 644 "$root/server/daylight-archive-refresh.timer" /etc/systemd/system/daylight-archive-refresh.timer
touch "$state/refresh.lock"
chown daylight-archive:daylight-archive "$state/refresh.lock" /var/www/daylightlinux/apt
runuser -u daylight-archive -- env HOME="$state" GNUPGHOME="$state/gnupg" python3 /usr/local/lib/daylight-archive/refresh-apt.py
systemctl daemon-reload
systemctl enable --now daylight-archive-refresh.timer
printf '%s\n' 'APT files published under https://daylightlinux.ch/apt/' 'Apache, Cloudflare, Docker, Nextcloud, network and desktop services were not restarted or reconfigured.' 'Keep the private signing key and revocation certificate outside the public document root and source repository.'
