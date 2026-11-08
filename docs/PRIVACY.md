# Privacy and boot statistics

Developer: Hamdy Abou El Anein. Project contact: info@daylightlinux.ch.

Daylight's default environment works offline. The optional `daylight-telemetry`
package is not installed by the desktop metapackage. Its timer is disabled and
its configuration has `enabled=no`; installation does not activate it. Only
`sudo daylight telemetry on` enables the timer, after explicit administrator
action. Use `sudo daylight telemetry off` to opt out.

An enabled timer makes one best-effort attempt after boot. The HTTPS POST body
contains only `event=boot`, the Daylight version and `mode=live|installed`.
There is no installation ID, hostname, username, serial number, MAC address or
IP field. There is no polling, persistent queue or automatic retry.

The collector binds to loopback on the Raspberry Pi. It stores daily aggregate
counts by version and mode, not individual requests or headers; HTTP request
and exception logging are disabled. Cloudflare handles public HTTPS and
necessarily processes transport metadata, including source IP. Daylight cannot
promise that the provider never processes or retains that metadata.

The endpoint is `https://miner.daylightlinux.ch/v1/boot`. The public
`/healthz` route returns only an empty HTTP 204 response. Counts are boot
events, not unique users; they can be affected by reboots, offline machines,
shared devices, copied images and spoofed requests.
