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
apt-get install -y --no-install-recommends xvfb xauth x11-utils x11-apps xdotool procps python3 imagemagick desktop-file-utils
adduser --disabled-password --gecos '' daylight-test
sha256sum /etc/os-release > /tmp/daylight-os-before
printf 'existing user config\n' > /home/daylight-test/.conkyrc
printf '# existing shell config\n' > /home/daylight-test/.bashrc
printf '# existing wallpaper setting\n' > /home/daylight-test/.fehbg
chown daylight-test:daylight-test /home/daylight-test/.conkyrc /home/daylight-test/.bashrc /home/daylight-test/.fehbg
sha256sum /home/daylight-test/.conkyrc /home/daylight-test/.bashrc /home/daylight-test/.fehbg > /tmp/daylight-user-before
apt-get install -y --no-install-recommends "$root/dist/daylight-core_5.0.0~rc1_${arch}.deb" "$root/dist/daylight-themes_5.0.0~rc1_all.deb" "$root/dist/daylight-desktop_5.0.0~rc1_all.deb" "$root/dist/daylight-apps_5.0.0~rc1_all.deb" "$root/dist/daylight-games_5.0.0~rc1_all.deb" "$root/dist/daylight-telemetry_5.0.0~rc1_all.deb" "$root/dist/daylight-linux_5.0.0~rc1_all.deb"
for entry in /usr/share/applications/daylight*.desktop /usr/share/xsessions/daylight*.desktop; do desktop-file-validate "$entry"; done
if apt-cache show fastfetch >/dev/null 2>&1; then
  apt-get install -y --no-install-recommends fastfetch
  runuser -u daylight-test -- fastfetch --config /usr/share/daylight/fastfetch/config.jsonc > /tmp/daylight-fastfetch.log
  if [ -d /out ]; then cp /tmp/daylight-fastfetch.log /out/; fi
fi
/usr/bin/daylight --version
runuser -u daylight-test -- env HOME=/home/daylight-test DAYLIGHT_BINARY=/usr/bin/daylight python3 "$root/tests/test_integration.py"
runuser -u daylight-test -- env HOME=/home/daylight-test XDG_CONFIG_HOME=/home/daylight-test/.config /usr/bin/daylight setup-session
Xvfb :99 -screen 0 1280x800x24 -nolisten tcp > /tmp/daylight-xvfb.log 2>&1 &
xpid=$!
xpid2=
cleanup() {
  kill "$xpid" 2>/dev/null || :
  if [ -n "$xpid2" ]; then kill "$xpid2" 2>/dev/null || :; fi
}
trap cleanup EXIT
sleep 2
runuser -u daylight-test -- env HOME=/home/daylight-test DISPLAY=:99 /usr/bin/daylight-session > /tmp/daylight-session.log 2>&1 &
session=$!
sleep 6
pgrep -u daylight-test -x fluxbox
pgrep -u daylight-test -x conky
DISPLAY=:99 xprop -root _NET_DESKTOP_NAMES | grep '"Work"'
grep -E '^session.styleFile:[[:space:]]*/usr/share/daylight/fluxbox/style' /home/daylight-test/.config/daylight/fluxbox/init
runuser -u daylight-test -- env DISPLAY=:99 xwininfo -root -tree > /tmp/daylight-windows.log
runuser -u daylight-test -- env HOME=/home/daylight-test DISPLAY=:99 GTK_THEME=Adwaita:dark /usr/bin/daylight-terminal > /tmp/daylight-terminal.log 2>&1 &
terminal=$!
sleep 3
pgrep -u daylight-test -x xterm
if [ -d /out ]; then
  DISPLAY=:99 xwd -root -silent -out /out/daylight-terminal.xwd
  convert /out/daylight-terminal.xwd /out/daylight-terminal.png
  cp /tmp/daylight-terminal.log /out/
fi
pkill -u daylight-test -x xterm || :
wait "$terminal" || :
runuser -u daylight-test -- env HOME=/home/daylight-test DISPLAY=:99 GTK_THEME=Adwaita:dark /usr/bin/daylight control-center > /tmp/daylight-center.log 2>&1 &
center=$!
sleep 2
pgrep -u daylight-test -x yad
if [ -d /out ]; then
  DISPLAY=:99 xwd -root -silent -out /out/daylight-desktop.xwd
  cp /tmp/daylight-session.log /tmp/daylight-center.log /tmp/daylight-windows.log /out/
  cp /home/daylight-test/.config/daylight/fluxbox/init /out/daylight-fluxbox-init
  convert /out/daylight-desktop.xwd /out/daylight-desktop.png
fi
pkill -u daylight-test -x yad || :
wait "$center" || :
runuser -u daylight-test -- env HOME=/home/daylight-test DISPLAY=:99 GTK_THEME=Adwaita:dark DAYLIGHT_DISPOSABLE_TEST=yes python3 "$root/tests/test_gui.py"
kill "$session" 2>/dev/null || :
# Check a second user with pre-existing classic Fluxbox files.
adduser --disabled-password --gecos '' daylight-existing
mkdir /home/daylight-existing/.fluxbox
for file in init keys menu apps overlay windowmenu; do printf '# pre-existing %s\n' "$file" > "/home/daylight-existing/.fluxbox/$file"; done
chown -R daylight-existing:daylight-existing /home/daylight-existing/.fluxbox
sha256sum /home/daylight-existing/.fluxbox/* > /tmp/daylight-classic-before
Xvfb :100 -screen 0 1280x800x24 -nolisten tcp > /tmp/daylight-xvfb-existing.log 2>&1 &
xpid2=$!
sleep 1
runuser -u daylight-existing -- env HOME=/home/daylight-existing DISPLAY=:100 /usr/bin/daylight-session > /tmp/daylight-existing.log 2>&1 &
existing=$!
sleep 5
pgrep -u daylight-existing -x fluxbox
DISPLAY=:100 xprop -root _NET_DESKTOP_NAMES | grep '"Work"'
kill "$existing" 2>/dev/null || :
# Reinstall the same version to check non-destructive idempotency.
dpkg -i "$root/dist/daylight-core_5.0.0~rc1_${arch}.deb"
/usr/bin/daylight remove --dry-run
apt-get remove -y --no-auto-remove daylight-linux daylight-desktop daylight-apps daylight-games daylight-telemetry daylight-themes daylight-core
sha256sum -c /tmp/daylight-os-before
sha256sum -c /tmp/daylight-user-before
sha256sum -c /tmp/daylight-classic-before
! command -v daylight
printf '\nDAYLIGHT_PACKAGE_LIFECYCLE_OK\n'
