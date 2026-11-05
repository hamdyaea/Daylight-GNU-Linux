#!/bin/sh
set -eu
cd "$(dirname "$0")"
build=$(mktemp -d)
trap 'rm -rf "$build"' EXIT
install -Dm755 session-defaults "$build/usr/lib/daylight/session-defaults"
install -Dm755 prerm "$build/DEBIAN/prerm"
version=1.1-1
extra=
if [ "${1:-}" = pi ]; then
    version=1.1-1+pi1
    extra=", labwc, swaybg, waybar, xwayland, dbus-user-session"
    install -Dm644 wayland/daylight-wayland.desktop "$build/usr/share/wayland-sessions/daylight-wayland.desktop"
    install -Dm755 wayland/session "$build/usr/lib/daylight/wayland-session"
    for name in autostart bar.json bar.css monitor.conf rc.xml menu.xml; do
        install -Dm644 "wayland/$name" "$build/usr/share/daylight/labwc/$name"
    done
    chmod 755 "$build/usr/share/daylight/labwc/autostart"
fi
cat > "$build/DEBIAN/control" <<EOF
Package: daylight-session-defaults
Version: $version
Architecture: all
Maintainer: Hamdy Abou El Anein <info@daylightlinux.ch>
Depends: daylight-linux, python3, util-linux, polkitd, systemd$extra
Description: Select the Daylight login session and restore previous preferences on removal
EOF
SOURCE_DATE_EPOCH=1700000000 dpkg-deb --root-owner-group -Zxz --build "$build" ../../website-src/daylight-session-defaults_${version}_all.deb
