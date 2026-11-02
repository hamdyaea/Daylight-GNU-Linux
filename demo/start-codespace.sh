#!/bin/sh
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
set -eu
# Private Codespaces port forwarding is the authentication boundary, not VNC.
# No paid instance is created by this script; it runs inside an instance its owner chose to create.
nohup flock -n /tmp/daylight-browser-demo.lock python3 /opt/daylight-demo/run.py --cache /opt/daylight-demo/image --listen 127.0.0.1 > /tmp/daylight-browser-demo.log 2>&1 < /dev/null &
printf '%s\n' 'Open the private forwarded port 6080 for the real Daylight AMD64 live session.' 'The guest stops after 20 minutes. Stop/delete the Codespace separately to manage compute and storage usage.'
