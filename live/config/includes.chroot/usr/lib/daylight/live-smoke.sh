#!/bin/sh
# Developer: Hamdy Abou El Anein
# Contact: contact@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
set -eu
for attempt in $(seq 1 75); do
 if pgrep -x fluxbox >/dev/null && pgrep -x conky >/dev/null; then
   /usr/bin/daylight status --json
   /usr/bin/daylight --version
   printf '\nDAYLIGHT_LIVE_READY\n'
   exit 0
 fi
 sleep 2
done
printf '\nDAYLIGHT_LIVE_FAILED\n'
exit 1
