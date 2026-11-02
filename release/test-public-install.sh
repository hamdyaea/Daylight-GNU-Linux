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
curl --disable --fail --silent --show-error --proto '=https' --max-time 60 https://daylightlinux.ch/install.sh -o /tmp/daylight-install.sh
cmp /tmp/daylight-install.sh /src/scripts/install-daylight.sh
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
# Keep dependencies and the system identity; no autoremove or global upgrade.
dpkg-query -W curl ca-certificates gnupg
sha256sum -c /tmp/os-before
printf '\nDAYLIGHT_PUBLIC_INSTALLER_LIFECYCLE_OK\n'
