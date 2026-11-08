#!/bin/sh
# Developer: Hamdy Abou El Anein
# SPDX-License-Identifier: GPL-3.0-only
# Only for a new disposable Debian container; never run this on the Raspberry Pi.
set -eu
if [ "${DAYLIGHT_DISPOSABLE_TEST:-}" != yes ] || [ ! -f /.dockerenv ]; then
    echo 'This test requires an explicitly authorised disposable Docker container.' >&2
    exit 2
fi
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
previous=${DAYLIGHT_PREVIOUS_PACKAGES:-/previous}
arch=$(dpkg --print-architecture)
export DEBIAN_FRONTEND=noninteractive
printf '#!/bin/sh\nexit 101\n' > /usr/sbin/policy-rc.d
chmod 755 /usr/sbin/policy-rc.d
apt-get -o Acquire::Retries=3 update -qq
apt-get -o Acquire::Retries=3 install -y --no-install-recommends adduser util-linux gnupg dpkg-dev xvfb xauth x11-utils procps python3
# Install the old real packages first. In particular do not install python3-tk
# here: pulling this new dependency is the behaviour under test.
apt-get install -y --no-install-recommends \
    "$previous/daylight-core_5.0.0~rc3_${arch}.deb" \
    "$previous/daylight-themes_5.0.0~rc3_all.deb" \
    "$previous/daylight-desktop_5.0.0~rc3_all.deb" \
    "$previous/daylight-apps_5.0.0~rc3_all.deb" \
    "$previous/daylight-games_5.0.0~rc3_all.deb" \
    "$previous/daylight-telemetry_5.0.0~rc3_all.deb" \
    "$previous/daylight-linux_5.0.0~rc3_all.deb"
/usr/bin/daylight --version | grep -F '5.0.0-rc.3'
if dpkg-query -W -f='${db:Status-Status}' python3-tk 2>/dev/null | grep -qx installed; then
    echo 'Fixture already contains python3-tk; cannot prove the dependency upgrade.' >&2
    exit 1
fi
adduser --disabled-password --gecos '' daylight-upgrade
runuser -u daylight-upgrade -- env HOME=/home/daylight-upgrade /usr/bin/daylight setup-session
runuser -u daylight-upgrade -- env HOME=/home/daylight-upgrade /usr/bin/daylight settings set profile minimal
printf '# Existing personal shell configuration\n' > /home/daylight-upgrade/.bashrc
printf '# Existing classic Conky configuration\n' > /home/daylight-upgrade/.conkyrc
# Simulate an existing opt-in without starting a service or sending an event.
sed -i 's/^enabled=no$/enabled=yes/' /etc/daylight/telemetry.conf
# Keep a real RC3 desktop running while APT replaces its package files. This
# tests the first-open handoff, not a fresh login to the new session script.
runtime=/run/user/$(id -u daylight-upgrade)
install -d -m 700 -o daylight-upgrade -g daylight-upgrade "$runtime"
Xvfb :99 -screen 0 1280x800x24 -nolisten tcp > /tmp/daylight-upgrade-xvfb.log 2>&1 &
xpid=$!
old_session=
old_wm=
cleanup() {
    pkill -u daylight-upgrade -f '/usr/share/daylight/ui/daylight_gui.py' 2>/dev/null || :
    if [ -n "$old_session" ]; then kill "$old_session" 2>/dev/null || :; fi
    if [ -n "$old_wm" ]; then kill "$old_wm" 2>/dev/null || :; fi
    kill "$xpid" 2>/dev/null || :
}
trap cleanup EXIT HUP INT TERM
sleep 1
runuser -u daylight-upgrade -- env HOME=/home/daylight-upgrade DISPLAY=:99 \
    XDG_RUNTIME_DIR="$runtime" XDG_SESSION_ID=daylight-upgrade-test \
    /usr/bin/daylight-session > /tmp/daylight-old-session.log 2>&1 &
old_session=$!
tries=0
while :; do
    old_wm=$(pgrep -u daylight-upgrade -x fluxbox || :)
    old_conky=$(pgrep -u daylight-upgrade -x conky || :)
    if [ -n "$old_wm" ] && [ -n "$old_conky" ]; then break; fi
    tries=$((tries + 1))
    if [ "$tries" -ge 40 ]; then cat /tmp/daylight-old-session.log >&2; exit 1; fi
    sleep 0.25
done
test "$(printf '%s\n' "$old_wm" | wc -l)" -eq 1
test "$(printf '%s\n' "$old_conky" | wc -l)" -eq 1
DISPLAY=:99 xprop -root _NET_SUPPORTING_WM_CHECK | grep -F 'window id'
# Fluxbox can canonicalise its init on first opening; record the established
# running session state, then demand that update and handoff preserve it.
sleep 1
sha256sum /etc/daylight/telemetry.conf \
    /home/daylight-upgrade/.bashrc /home/daylight-upgrade/.conkyrc \
    /home/daylight-upgrade/.config/daylight/settings.conf \
    /home/daylight-upgrade/.config/daylight/fluxbox/init > /tmp/daylight-before-upgrade.sha256
printf 'RC3_LIVE_SESSION wm=%s conky=%s\n' "$old_wm" "$old_conky"

# Build a signed file repository with a short-lived test key. Neither the real
# public signing key nor an unauthenticated/trusted=yes source is used.
export GNUPGHOME=/tmp/daylight-upgrade-gnupg
mkdir -m 700 "$GNUPGHOME"
gpg --batch --pinentry-mode loopback --passphrase '' --quick-generate-key \
    'Disposable Daylight upgrade test <ci@example.invalid>' ed25519 sign 1d
fingerprint=$(gpg --batch --with-colons --list-keys | awk -F: '$1=="fpr" {print $10; exit}')
python3 "$root/scripts/build-apt-repository.py" --packages "$root/dist" \
    --output /tmp/daylight-upgrade-repository --signing-key "$fingerprint"
cp /tmp/daylight-upgrade-repository/daylight-archive-keyring.gpg /usr/share/keyrings/daylight-upgrade-test.gpg
printf '%s\n' 'deb [signed-by=/usr/share/keyrings/daylight-upgrade-test.gpg] file:/tmp/daylight-upgrade-repository daylight main' > /etc/apt/sources.list.d/daylight-upgrade-test.list
printf '%s\n' 'Package: daylight-*' 'Pin: origin ""' 'Pin-Priority: 700' > /etc/apt/preferences.d/daylight-upgrade-test

# This is the RC3 executable invoking its original APT path. There is no second
# installer, pip call, individual package install or setup-session after update.
printf 'Y\n' | /usr/bin/daylight update
/usr/bin/daylight --version | grep -F '5.0.0-rc.4'
for package in daylight-core daylight-themes daylight-desktop daylight-apps daylight-games daylight-telemetry daylight-linux; do
    test "$(dpkg-query -W -f='${Version}' "$package")" = '5.0.0~rc4'
done
test "$(dpkg-query -W -f='${db:Status-Status}' python3-tk)" = installed
/usr/bin/python3 -c 'import tkinter; import sys; sys.path.insert(0,"/usr/share/daylight/ui"); import daylight_ui.shell'
test -f /usr/share/daylight/shardturn/Shardturn.py
test -f /usr/share/applications/daylight-shardturn.desktop
test -f /usr/share/daylight/games.enabled
grep -F '/usr/bin/daylight app launcher' /usr/share/daylight/fluxbox/keys
grep -F '/usr/bin/daylight app sky' /usr/share/daylight/fluxbox/menu
sha256sum -c /tmp/daylight-before-upgrade.sha256

# Open a page through the newly installed public Rust command before exercising
# the Python widgets directly. No setup or migration command is required.
runuser -u daylight-upgrade -- env HOME=/home/daylight-upgrade DISPLAY=:99 \
    XDG_RUNTIME_DIR="$runtime" XDG_SESSION_ID=daylight-upgrade-test \
    DAYLIGHT_SESSION=1 XDG_CURRENT_DESKTOP=Daylight:Fluxbox \
    /usr/bin/daylight app cards > /tmp/daylight-upgraded-app.log 2>&1 &
bridge=$!
sleep 2
if ! kill -0 "$bridge" 2>/dev/null; then
    cat /tmp/daylight-upgraded-app.log >&2
    exit 1
fi
pgrep -u daylight-upgrade -f '/usr/share/daylight/ui/daylight_gui.py cards'
DISPLAY=:99 xwininfo -root -tree | grep -F 'Daylight GNU/Linux'
# First ordinary application opening must adopt the old running session. The
# manager is a singleton, retires the session-owned legacy Conky and leaves
# the exact Fluxbox process alive: no logout, restart or manual setup command.
tries=0
while :; do
    manager=$(pgrep -u daylight-upgrade -f '/usr/share/daylight/ui/daylight_gui.py --session-appearance' || :)
    new_conky=$(pgrep -u daylight-upgrade -x conky || :)
    if [ -n "$manager" ] && [ -n "$new_conky" ] && [ "$new_conky" != "$old_conky" ] \
            && [ "$(printf '%s\n' "$manager" | wc -l)" -eq 1 ] \
            && [ "$(printf '%s\n' "$new_conky" | wc -l)" -eq 1 ]; then break; fi
    tries=$((tries + 1))
    if [ "$tries" -ge 60 ]; then
        cat /tmp/daylight-upgraded-app.log /tmp/daylight-old-session.log >&2
        ps -u daylight-upgrade -o pid,ppid,stat,args >&2
        exit 1
    fi
    sleep 0.25
done
test "$(pgrep -u daylight-upgrade -x fluxbox)" = "$old_wm"
kill -0 "$old_wm"
if [ -r "/proc/$old_conky/status" ] && ! grep -Eq '^State:[[:space:]]+Z' "/proc/$old_conky/status"; then
    echo 'The old session-owned Conky was not retired.' >&2
    exit 1
fi
sha256sum -c /tmp/daylight-before-upgrade.sha256
printf 'RC4_LIVE_HANDOFF manager=%s wm=%s conky=%s\n' "$manager" "$old_wm" "$new_conky"
pkill -u daylight-upgrade -f '/usr/share/daylight/ui/daylight_gui.py cards' || :
wait "$bridge" || :
runuser -u daylight-upgrade -- env HOME=/home/daylight-upgrade DISPLAY=:99 \
    XDG_RUNTIME_DIR="$runtime" XDG_SESSION_ID=daylight-upgrade-test \
    DAYLIGHT_SESSION=1 XDG_CURRENT_DESKTOP=Daylight:Fluxbox DAYLIGHT_UI_ROOT=/usr/share/daylight/ui \
    /usr/bin/python3 "$root/tests/test_gui.py"
test "$(pgrep -u daylight-upgrade -x fluxbox)" = "$old_wm"
test "$(pgrep -u daylight-upgrade -x conky | wc -l)" -eq 1
test "$(pgrep -u daylight-upgrade -f '/usr/share/daylight/ui/daylight_gui.py --session-appearance' | wc -l)" -eq 1
sha256sum -c /tmp/daylight-before-upgrade.sha256
printf '\nDAYLIGHT_RC3_TO_RC4_UPDATE_ONLY_OK\n'
