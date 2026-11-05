#!/bin/sh
set -eu
cd "$(dirname "$0")"
build=$(mktemp -d)
trap 'rm -rf "$build"' EXIT
install -Dm755 session-defaults "$build/usr/lib/daylight/session-defaults"
install -Dm755 prerm "$build/DEBIAN/prerm"
cat > "$build/DEBIAN/control" <<'EOF'
Package: daylight-session-defaults
Version: 1.0-1
Architecture: all
Maintainer: Hamdy Abou El Anein <info@daylightlinux.ch>
Depends: daylight-linux, python3, util-linux, polkitd, systemd
Description: Select the Daylight login session and restore previous preferences on removal
EOF
SOURCE_DATE_EPOCH=1700000000 dpkg-deb --root-owner-group -Zxz --build "$build" ../../website-src/daylight-session-defaults_1.0-1_all.deb
