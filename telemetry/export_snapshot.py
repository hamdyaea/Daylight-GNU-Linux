#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Atomically export aggregate counts for the private dashboard and offsite backup."""
import argparse
from datetime import datetime, timezone
import grp
import json
import os
from pathlib import Path
import sqlite3
import tempfile

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=Path("/var/lib/daylight-counter/counts.sqlite3"))
    parser.add_argument("--output", type=Path, default=Path("/var/backups/daylight-telemetry/counts.json"))
    parser.add_argument("--group", default="daylight-dashboard")
    args = parser.parse_args()

    group = grp.getgrnam(args.group)
    args.output.parent.mkdir(mode=0o750, parents=True, exist_ok=True)
    os.chown(args.output.parent, 0, group.gr_gid)
    os.chmod(args.output.parent, 0o2750)

    uri = "file:" + str(args.database) + "?mode=ro"
    with sqlite3.connect(uri, uri=True, timeout=5) as connection:
        rows = connection.execute(
            "SELECT day, version, mode, boots FROM counts ORDER BY day, version, mode"
        ).fetchall()
    snapshot = {
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "records": [
            {"day": day, "version": version, "mode": mode, "boots": boots}
            for day, version, mode, boots in rows
        ],
    }
    fd, temporary = tempfile.mkstemp(prefix=".counts-", suffix=".json", dir=args.output.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(snapshot, stream, ensure_ascii=False, separators=(",", ":"))
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.chown(temporary, 0, group.gr_gid)
        os.chmod(temporary, 0o640)
        os.replace(temporary, args.output)
        directory_fd = os.open(args.output.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
    print(f"Exported {len(rows)} aggregate rows to {args.output}")

if __name__ == "__main__":
    main()