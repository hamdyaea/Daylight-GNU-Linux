#!/bin/sh
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
# Never execute on a workstation or a production host.
set -eu
[ "${DAYLIGHT_DISPOSABLE_TEST:-}" = yes ] && [ -e /.dockerenv ] || { echo 'Disposable test container required.' >&2; exit 2; }
export DEBIAN_FRONTEND=noninteractive
printf '#!/bin/sh\nexit 101\n' > /usr/sbin/policy-rc.d
chmod 755 /usr/sbin/policy-rc.d
apt-get -o APT::Update::Error-Mode=any update -qq
apt-get install -y --no-install-recommends ca-certificates curl gnupg gpgv
sha256sum /etc/os-release > /tmp/os-before
# A repository must be understandable in a browser as well as consumable by APT.
curl --disable --fail --silent --show-error --proto '=https' --max-time 30 https://daylightlinux.ch/apt/ -o /tmp/daylight-apt-index.html
grep -q 'daylight-archive-keyring.gpg' /tmp/daylight-apt-index.html
grep -q 'binary-arm64/Packages' /tmp/daylight-apt-index.html
curl --disable --fail --silent --show-error --proto '=https' --max-time 30 https://daylightlinux.ch/apt/apt.css -o /tmp/daylight-apt.css
test -s /tmp/daylight-apt.css
curl --disable --fail --silent --show-error --head --proto '=https' --max-time 30 https://daylightlinux.ch/apt -o /tmp/daylight-apt-redirect.headers
tr -d '\r' < /tmp/daylight-apt-redirect.headers | grep -qi '^location: https://daylightlinux.ch/apt/$'
curl --disable --fail --silent --show-error --proto '=https' --max-time 60 https://daylightlinux.ch/daylight-install.sh -o /tmp/daylight-install.sh
cmp /tmp/daylight-install.sh /src/scripts/daylight-install.sh
sh /tmp/daylight-install.sh --plan
[ ! -e /etc/apt/sources.list.d/daylight.sources ]
sh /tmp/daylight-install.sh --core --yes
/usr/bin/daylight --version
/usr/bin/daylight status --json
/usr/bin/daylight telemetry status | grep disabled
! dpkg-query -W daylight-telemetry 2>/dev/null
sha256sum /etc/apt/sources.list.d/daylight.sources /etc/apt/preferences.d/daylight /etc/apt/keyrings/daylight-archive-keyring.gpg > /tmp/config-before
sh /tmp/daylight-install.sh --repo-only --yes
sha256sum -c /tmp/config-before
apt-cache policy daylight-core
/usr/bin/daylight update --dry-run
/usr/bin/daylight remove --dry-run
printf 'y\n' | /usr/bin/daylight remove
! command -v daylight
for path in /etc/apt/sources.list.d/daylight.sources /etc/apt/preferences.d/daylight /etc/apt/keyrings/daylight-archive-keyring.gpg /etc/dpkg/dpkg.cfg.d/90-daylight-repository; do
    test ! -e "$path"
done
# Keep dependencies and the system identity; no autoremove or global upgrade.
dpkg-query -W curl ca-certificates gnupg
sha256sum -c /tmp/os-before
printf '\nDAYLIGHT_PUBLIC_INSTALLER_LIFECYCLE_OK\n'
