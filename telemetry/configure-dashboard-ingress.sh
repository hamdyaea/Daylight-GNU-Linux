#!/bin/sh
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
set -eu
[ "$(id -u)" -eq 0 ] || { echo "Run as root." >&2; exit 1; }
config=/etc/cloudflared/config.yml
action=${1:-add}
[ "$action" = add ] || [ "$action" = remove ] || { echo "Usage: $0 [add|remove]" >&2; exit 2; }
backup=$(python3 - "$config" "$action" <<'PY'
from datetime import datetime, timezone
import os, shutil, stat, sys, tempfile
from pathlib import Path

path = Path(sys.argv[1])
action = sys.argv[2]
source = path.read_text()
route = ("# Daylight private telemetry dashboard; Cloudflare Access protects this host.\n"
         "- hostname: telemetry.daylightlinux.ch\n"
         "  service: http://127.0.0.1:8788\n")
marker = "- service: http_status:404\n"
if action == "add":
    if route in source:
        print("")
        raise SystemExit(0)
    if source.count(marker) != 1:
        raise SystemExit("Expected one final Cloudflare 404 ingress rule; no changes made")
    updated = source.replace(marker, route + marker, 1)
else:
    if route not in source:
        print("")
        raise SystemExit(0)
    updated = source.replace(route, "", 1)

stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
backup = path.with_name(path.name + ".bak.dashboard-" + stamp)
shutil.copy2(path, backup)
mode = stat.S_IMODE(path.stat().st_mode)
fd, temporary = tempfile.mkstemp(prefix=".config.yml.dashboard-", dir=path.parent)
try:
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(updated)
        stream.flush()
        os.fsync(stream.fileno())
    os.chown(temporary, path.stat().st_uid, path.stat().st_gid)
    os.chmod(temporary, mode)
    os.replace(temporary, path)
except Exception:
    try: os.unlink(temporary)
    except FileNotFoundError: pass
    raise
print(backup)
PY
)
if [ -z "$backup" ]; then
    echo "Dashboard ingress already in requested state."
    exit 0
fi
if ! cloudflared tunnel ingress validate; then
    cp -a "$backup" "$config"
    echo "Ingress validation failed; configuration restored." >&2
    exit 1
fi
if systemctl restart cloudflared && systemctl is-active --quiet cloudflared; then
    echo "Dashboard ingress updated; backup: $backup"
    exit 0
fi
cp -a "$backup" "$config"
cloudflared tunnel ingress validate || true
systemctl restart cloudflared || true
echo "Tunnel restart failed; previous configuration restored from $backup." >&2
exit 1