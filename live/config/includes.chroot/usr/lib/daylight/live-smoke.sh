#!/bin/sh
# Developer: Hamdy Abou El Anein
# Contact: contact@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
set -eu
channel=/dev/virtio-ports/org.daylightlinux.test
report() {
 if [ -e "$channel" ]; then printf '%s\n' "$1" > "$channel"; fi
 printf '%s\n' "$1"
}
for attempt in $(seq 1 100); do
 if id daylight >/dev/null 2>&1 && pgrep -u daylight -x fluxbox >/dev/null && pgrep -u daylight -x conky >/dev/null; then
   report "$(/usr/bin/daylight status --json)"
   report "$(/usr/bin/daylight --version)"
   report DAYLIGHT_LIVE_READY
   exit 0
 fi
 sleep 2
done
report "$(systemctl --failed --no-pager 2>&1 || true)"
report "$(tail -60 /var/log/lightdm/lightdm.log 2>/dev/null || true)"
report DAYLIGHT_LIVE_FAILED
exit 1
