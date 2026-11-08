# Telemetry collector deployment

The opt-in client endpoint is `https://miner.daylightlinux.ch/v1/boot`.
Cloudflare terminates public HTTPS. The existing MinerWatch tunnel routes only
`/v1/boot` and `/healthz` to the collector; other requests keep their
existing route. No DNS record is added.

On the Raspberry Pi, check out the repository and run
`sudo scripts/deploy-telemetry-collector.sh`, then
`sudo scripts/configure-telemetry-ingress.sh`. The collector listens only on
`127.0.0.1:8787`, runs as a systemd dynamic user, and writes daily aggregates
to `/var/lib/daylight-counter/counts.sqlite3`. The systemd service hardens
the process; collector request and exception logging are disabled.

The ingress script backs up `/etc/cloudflared/config.yml`, inserts the exact
path rule before the MinerWatch hostname, validates the result, and restarts
the tunnel. It restores the backup if validation or restart fails. The
catch-all 404 rule must remain last.

Cloudflare Access has exact-path Bypass applications for `/v1/boot` and
`/healthz` on `miner.daylightlinux.ch`; the root and other MinerWatch paths
remain protected. Verified on 2026-11-08 from an external client: `GET
/healthz` returned HTTP 204, a valid synthetic `POST /v1/boot` returned HTTP
204, and `GET /` remained an Access login redirect (HTTP 302). The synthetic
aggregate row was removed after the test. The client accepts only HTTP 204, so
Access redirects are reported as undelivered. Cloudflare processes source IP
metadata, so this service does not promise network anonymity. Never report boot
events as unique users.

## Private dashboard and backup

`dashboard/` contains a local-only dashboard and an atomic JSON exporter. Install it on the Pi with `sudo sh telemetry/install-dashboard.sh`. The dashboard binds only to `127.0.0.1:8788`; expose it only through the existing Cloudflare Tunnel after creating a Self-hosted Access application for `telemetry.daylightlinux.ch`, with an Allow policy for the administrator's email and One-time PIN. Do not create a Bypass policy for this host.

The exporter refreshes `/var/backups/daylight-telemetry/counts.json` every five minutes. A dedicated unprivileged dashboard account can read this aggregate snapshot; it cannot access the collector database. The directory is already within the Pi's Restic `--files-from` path `/var/backups`, and the backup validator must require the snapshot path. The encrypted Restic repository is stored on OneDrive, separate from the Pi. The dashboard is a current view; restoring the snapshot from OneDrive recovers the aggregate history if the Pi is lost.