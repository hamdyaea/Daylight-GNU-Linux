#!/bin/sh
# Developer: Hamdy Abou El Anein
# SPDX-License-Identifier: GPL-3.0-only
set -eu
if [ "$(id -u)" -ne 0 ]; then
    echo "Run this script as root." >&2
    exit 1
fi
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
test -f "$root/telemetry/collector.py"
install -d -o root -g root -m 0755 /usr/local/lib/daylight-telemetry
install -o root -g root -m 0644 "$root/telemetry/collector.py" /usr/local/lib/daylight-telemetry/collector.py
install -o root -g root -m 0644 "$root/telemetry/daylight-telemetry-collector.service" /etc/systemd/system/daylight-telemetry-collector.service
systemctl daemon-reload
systemctl enable daylight-telemetry-collector.service
if systemctl is-active --quiet daylight-telemetry-collector.service; then
    systemctl restart daylight-telemetry-collector.service
else
    systemctl start daylight-telemetry-collector.service
fi
systemctl --no-pager --full status daylight-telemetry-collector.service
