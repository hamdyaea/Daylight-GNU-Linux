#!/bin/sh
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
set -eu
[ "$(id -u)" -eq 0 ] || { echo "Run with sudo." >&2; exit 1; }
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
LIB=/usr/local/lib/daylight-telemetry
WEB=/usr/local/share/daylight-telemetry-dashboard
DATA=/var/backups/daylight-telemetry
if [ -L "$DATA" ] || [ -L "$LIB" ] || [ -L "$WEB" ]; then
    echo "Refusing a symlink at a managed destination." >&2
    exit 1
fi
if ! getent group daylight-dashboard >/dev/null; then
    groupadd --system daylight-dashboard
fi
if ! id daylight-dashboard >/dev/null 2>&1; then
    useradd --system --no-create-home --home-dir /nonexistent --shell /usr/sbin/nologin --gid daylight-dashboard daylight-dashboard
fi
install -d -o root -g root -m 0755 "$LIB" "$WEB"
install -d -o root -g daylight-dashboard -m 2750 "$DATA"
install -o root -g root -m 0644 "$HERE/export_snapshot.py" "$LIB/export_snapshot.py"
install -o root -g root -m 0644 "$HERE/dashboard.py" "$LIB/dashboard.py"
install -o root -g root -m 0644 "$HERE/dashboard/index.html" "$WEB/index.html"
install -o root -g root -m 0644 "$HERE/dashboard/app.js" "$WEB/app.js"
install -o root -g root -m 0644 "$HERE/dashboard/style.css" "$WEB/style.css"
install -o root -g root -m 0644 "$HERE/daylight-telemetry-export.service" /etc/systemd/system/daylight-telemetry-export.service
install -o root -g root -m 0644 "$HERE/daylight-telemetry-export.timer" /etc/systemd/system/daylight-telemetry-export.timer
install -o root -g root -m 0644 "$HERE/daylight-telemetry-dashboard.service" /etc/systemd/system/daylight-telemetry-dashboard.service
systemctl daemon-reload
systemctl enable --now daylight-telemetry-export.timer
systemctl enable --now daylight-telemetry-dashboard.service
attempt=0
until /usr/bin/curl --disable --fail --silent --show-error --max-time 2 http://127.0.0.1:8788/healthz >/dev/null; do
    attempt=$((attempt + 1))
    [ "$attempt" -lt 10 ] || { echo "Dashboard did not become healthy." >&2; exit 1; }
    sleep 1
done
echo "Dashboard active on 127.0.0.1:8788; daily Restic includes its snapshot under /var/backups/daylight-telemetry."