#!/bin/sh
# Developer: Hamdy Abou El Anein
# Contact: contact@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
set -eu
# Run only in a disposable Debian container. Never run this lifecycle test on production.
if [ "${DAYLIGHT_DISPOSABLE_TEST:-}" != yes ]; then echo 'Set DAYLIGHT_DISPOSABLE_TEST=yes only in a disposable test container.' >&2; exit 2; fi
export DEBIAN_FRONTEND=noninteractive
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
arch=$(dpkg --print-architecture)
printf '#!/bin/sh\nexit 101\n' > /usr/sbin/policy-rc.d
chmod 755 /usr/sbin/policy-rc.d
apt-get update -qq
apt-get install -y --no-install-recommends xvfb xauth x11-utils procps python3 imagemagick desktop-file-utils
adduser --disabled-password --gecos '' daylight-test
sha256sum /etc/os-release > /tmp/daylight-os-before
printf 'existing user config\n' > /home/daylight-test/.conkyrc
printf 'existing shell config\n' > /home/daylight-test/.bashrc
chown daylight-test:daylight-test /home/daylight-test/.conkyrc /home/daylight-test/.bashrc
sha256sum /home/daylight-test/.conkyrc /home/daylight-test/.bashrc > /tmp/daylight-user-before
apt-get install -y --no-install-recommends "$root/dist/daylight-core_5.0.0~rc1_${arch}.deb" "$root/dist/daylight-themes_5.0.0~rc1_all.deb" "$root/dist/daylight-desktop_5.0.0~rc1_all.deb" "$root/dist/daylight-apps_5.0.0~rc1_all.deb" "$root/dist/daylight-games_5.0.0~rc1_all.deb" "$root/dist/daylight-telemetry_5.0.0~rc1_all.deb" "$root/dist/daylight-linux_5.0.0~rc1_all.deb"
find /usr/share/applications /usr/share/xsessions -name "daylight*.desktop" -exec desktop-file-validate {} \;
/usr/bin/daylight --version
runuser -u daylight-test -- env HOME=/home/daylight-test DAYLIGHT_BINARY=/usr/bin/daylight python3 "$root/tests/test_integration.py"
runuser -u daylight-test -- env HOME=/home/daylight-test XDG_CONFIG_HOME=/home/daylight-test/.config /usr/bin/daylight setup-session
Xvfb :99 -screen 0 1280x800x24 -nolisten tcp > /tmp/daylight-xvfb.log 2>&1 &
xpid=$!
trap 'kill "$xpid" 2>/dev/null || :' EXIT
sleep 2
runuser -u daylight-test -- env HOME=/home/daylight-test DISPLAY=:99 /usr/bin/daylight-session > /tmp/daylight-session.log 2>&1 &
session=$!
sleep 6
pgrep -u daylight-test -x fluxbox
pgrep -u daylight-test -x conky
runuser -u daylight-test -- env DISPLAY=:99 xwininfo -root -tree
runuser -u daylight-test -- env HOME=/home/daylight-test DISPLAY=:99 /usr/bin/daylight control-center > /tmp/daylight-center.log 2>&1 &
center=$!
sleep 2
pgrep -u daylight-test -x yad
if [ -d /out ]; then
  DISPLAY=:99 xwd -root -silent -out /out/daylight-desktop.xwd
  cp /tmp/daylight-session.log /tmp/daylight-center.log /out/
  convert /out/daylight-desktop.xwd /out/daylight-desktop.png
fi
kill "$center" "$session" 2>/dev/null || :
# Reinstall the same version to check non-destructive idempotency.
dpkg -i "$root/dist/daylight-core_5.0.0~rc1_${arch}.deb"
/usr/bin/daylight remove --dry-run
apt-get remove -y --no-auto-remove daylight-linux daylight-desktop daylight-apps daylight-games daylight-telemetry daylight-themes daylight-core
sha256sum -c /tmp/daylight-os-before
sha256sum -c /tmp/daylight-user-before
! command -v daylight
printf '\nDAYLIGHT_PACKAGE_LIFECYCLE_OK\n'
