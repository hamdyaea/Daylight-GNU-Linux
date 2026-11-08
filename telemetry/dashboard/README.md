# Daylight telemetry dashboard

The dashboard is a private, loopback-only service intended to sit behind
Cloudflare Access on `telemetry.daylightlinux.ch`. Do not create a public
bypass policy for this hostname. The Access allow policy should identify the
administrator by email and use Cloudflare One-time PIN.

The Python dashboard reads only the atomic JSON export at
`/var/backups/daylight-telemetry/counts.json`. It does not open the collector's
SQLite database and does not log requests or identity headers. The exporter
refreshes the file every five minutes. The dashboard binds to
`127.0.0.1:8788`; cloudflared is the only public route.

Run `sudo sh install-dashboard.sh` on the Raspberry Pi to install the local
service and timer. The export folder is under `/var/backups`, already covered
by the Pi's daily Restic backup to OneDrive. The Restic backup script verifies
the exported file is included before it accepts a snapshot. Restore the JSON
snapshot from OneDrive if the Pi's local database is lost.

Cloudflare routing must be completed separately:
1. Create a Self-hosted Access application for `telemetry.daylightlinux.ch`.
2. Set an Allow policy limited to the administrator's email and enable One-time PIN.
3. Add the hostname route to the existing cloudflared tunnel, pointing to
   `http://127.0.0.1:8788`, before the catch-all 404 rule.
4. Create the proxied DNS route to that tunnel and verify the Access login from
   outside the home network.

The dashboard displays aggregate boot events, not unique installations or
people. Cloudflare processes transport metadata such as source IP addresses.