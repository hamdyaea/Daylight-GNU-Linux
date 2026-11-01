#!/bin/sh
# Developer: Hamdy Abou El Anein
# Contact: contact@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
set -eu
printf '\nDAYLIGHT_LIVE_CHECK_STARTED\n'
if ! id daylight >/dev/null 2>&1; then
  printf 'DAYLIGHT_LIVE_FAILED: live user was not created\n'
  exit 1
fi
for attempt in $(seq 1 120); do
 if pgrep -u daylight -x fluxbox >/dev/null && pgrep -u daylight -x conky >/dev/null; then
   /usr/bin/daylight status --json
   /usr/bin/daylight --version
   printf '\nDAYLIGHT_LIVE_READY\n'
   exit 0
 fi
 sleep 2
done
systemctl --no-pager status lightdm.service || :
journalctl -b -u lightdm.service --no-pager -n 80 || :
if [ -f /var/log/lightdm/x-0.log ]; then tail -60 /var/log/lightdm/x-0.log; fi
printf '\nDAYLIGHT_LIVE_FAILED: graphical session did not start\n'
exit 1
