#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
# Run after downloading and reviewing this script and daylight-mirror-sync.py.
set -Eeuo pipefail
[[ "$EUID" -eq 0 ]] || { echo "Run as root" >&2; exit 1; }
: "${MIRROR_HOST:?Set MIRROR_HOST to your HTTPS mirror hostname}"
[[ "$MIRROR_HOST" =~ ^[a-zA-Z0-9.-]+$ && "$MIRROR_HOST" == *.* ]] || { echo "Invalid hostname" >&2; exit 1; }
: "${TRUSTED_KEYRING:=/etc/daylight/archive-keyring.gpg}"
[[ -s "$TRUSTED_KEYRING" ]] || { echo "Install and verify the official archive key at $TRUSTED_KEYRING first" >&2; exit 1; }
[[ -f ./daylight-mirror-sync.py ]] || { echo "Download daylight-mirror-sync.py into this directory" >&2; exit 1; }
for program in python3 gpgv systemctl; do command -v "$program" >/dev/null || { echo "Missing $program" >&2; exit 1; }; done
id daylight-mirror >/dev/null 2>&1 || useradd --system --home /srv/daylight-mirror --shell /usr/sbin/nologin daylight-mirror
install -d -m 0755 -o daylight-mirror -g daylight-mirror /srv/daylight-mirror
install -m 0755 ./daylight-mirror-sync.py /usr/local/sbin/daylight-mirror-sync
cat >/etc/systemd/system/daylight-mirror-sync.service <<EOF
[Unit]
Description=Synchronize the signed Daylight APT mirror
Wants=network-online.target
After=network-online.target
[Service]
Type=oneshot
User=daylight-mirror
Group=daylight-mirror
ExecStart=/usr/bin/python3 /usr/local/sbin/daylight-mirror-sync --trusted-keyring $TRUSTED_KEYRING --dest /srv/daylight-mirror
NoNewPrivileges=true
ProtectSystem=strict
ReadWritePaths=/srv/daylight-mirror
PrivateTmp=true
EOF
cat >/etc/systemd/system/daylight-mirror-sync.timer <<'EOF'
[Unit]
Description=Synchronize Daylight mirror every 15 minutes
[Timer]
OnCalendar=*:0/15
RandomizedDelaySec=120
Persistent=true
[Install]
WantedBy=timers.target
EOF
systemctl daemon-reload
systemctl enable --now daylight-mirror-sync.timer
echo "Timer installed. Configure your existing HTTPS web server to serve /srv/daylight-mirror."
echo "Then run: systemctl start daylight-mirror-sync.service"
echo "After the first successful sync, request registration at:"
echo "https://github.com/hamdyaea/Daylight-GNU-Linux/issues/new?template=community_mirror.yml"
echo "Mirror hostname: $MIRROR_HOST"
