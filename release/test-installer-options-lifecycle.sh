#!/bin/sh
set -eu
[ -e /.dockerenv ]
export DEBIAN_FRONTEND=noninteractive
printf '#!/bin/sh\nexit 101\n' > /usr/sbin/policy-rc.d
chmod 755 /usr/sbin/policy-rc.d
apt-get update -qq
apt-get install -y --no-install-recommends ca-certificates curl gnupg python3 >/tmp/prereqs.log 2>&1
curl -fsSL https://daylightlinux.ch/daylight-install.sh -o /tmp/daylight-install.sh
cmp /tmp/daylight-install.sh /tests/daylight-install.sh
python3 /tests/test-installer-options.py /tmp/daylight-install.sh
sh /tmp/daylight-install.sh --repo-only --yes
sh /tmp/daylight-install.sh --remove-repo --yes
test ! -e /etc/apt/sources.list.d/daylight.sources
for mode in core desktop all; do
 sh /tmp/daylight-install.sh --$mode --yes > /tmp/install-$mode.log 2>&1 || { tail -70 /tmp/install-$mode.log; exit 1; }
 echo "PASS APPLY --$mode --yes"
 daylight --version
done
for p in daylight-core daylight-themes daylight-apps daylight-desktop daylight-linux daylight-games; do
 test "$(dpkg-query -W -f='${Status}' "$p")" = 'install ok installed'
done
! dpkg-query -W daylight-telemetry 2>/dev/null
if sh /tmp/daylight-install.sh --remove-repo --yes; then echo 'ERROR removal should refuse installed packages'; exit 1; fi
sh /tmp/daylight-install.sh --desktop --games --yes >/tmp/reinstall.log 2>&1
sh /tmp/daylight-install.sh --repo-only --yes >/tmp/repo.log 2>&1
printf 'y\n' | daylight remove
for p in /etc/apt/sources.list.d/daylight.sources /etc/apt/preferences.d/daylight /etc/apt/keyrings/daylight-archive-keyring.gpg; do test ! -e "$p"; done
sh /tmp/daylight-install.sh --remove-repo --yes
echo ALL_INSTALLER_LIFECYCLE_CHECKS_PASSED
