#!/bin/sh
set -eu
cd "$(dirname "$0")"
build=$(mktemp -d)
trap 'rm -rf "$build"' EXIT
install -Dm755 session-defaults "$build/usr/lib/daylight/session-defaults"
install -Dm755 prerm "$build/DEBIAN/prerm"
version=1.2-1
install -Dm644 wayland/daylight-wayland.desktop "$build/usr/share/wayland-sessions/daylight-wayland.desktop"
install -Dm755 wayland/session "$build/usr/lib/daylight/wayland-session"
install -Dm755 wayland/applications-menu "$build/usr/lib/daylight/applications-menu"
for name in autostart bar.json bar.css conky.lua rc.xml menu.xml; do
    install -Dm644 "wayland/$name" "$build/usr/share/daylight/labwc/$name"
done
chmod 755 "$build/usr/share/daylight/labwc/autostart"
cat > "$build/DEBIAN/control" <<EOF
Package: daylight-session-defaults
Version: $version
Architecture: all
Maintainer: Hamdy Abou El Anein <info@daylightlinux.ch>
Depends: daylight-linux, python3, util-linux, polkitd, systemd, labwc | fluxbox, swaybg, waybar, wtype, python3-gi, gir1.2-glib-2.0, libglib2.0-bin, xwayland, dbus-user-session
Description: Select the Daylight login session and restore previous preferences on removal
EOF
out=${1:-../../dist}
mkdir -p "$out"
SOURCE_DATE_EPOCH=1700000000 dpkg-deb --root-owner-group -Zxz --build "$build" "$out/daylight-session-defaults_${version}_all.deb"
