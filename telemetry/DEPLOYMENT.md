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

**Cloudflare Access currently redirects public requests on this hostname to a
login page.** Before telemetry can receive events, add a Bypass policy for only
`/v1/boot` and `/healthz` on `miner.daylightlinux.ch`; keep the rest of the
MinerWatch hostname protected. The client accepts only HTTP 204, so redirects
are reported as undelivered. Then verify `https://miner.daylightlinux.ch/healthz`
returns 204. A valid `POST /v1/boot` returns 204. Test events increment the
aggregate; remove any synthetic test row after verification. Cloudflare
processes source IP metadata, so this service does not promise network
anonymity. Never report boot events as unique users.
