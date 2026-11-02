# Privacy and boot statistics

Developer: Hamdy Abou El Anein. Project contact: info@daylightlinux.ch (activation pending).

The default environment works offline. The terminal banner, Conky and local tools make no automatic Internet request. A network check requires an explicit `daylight connect --check HOST` action.

`daylight-telemetry` is an optional package, not a dependency of the desktop metapackage. Its timer is disabled and its configuration has `enabled=no` with no endpoint. Installation does not enable or start it. Activation refuses to proceed until a valid HTTPS endpoint has been configured.

An enabled timer makes one best-effort attempt after boot, outside the critical startup path. The JSON has only `event=boot`, the Daylight version and `mode=live|installed`. There is no installation ID, hostname, username, serial number, MAC address or IP field. There is no permanent polling, persistent queue or automatic retry.

**Network anonymity is not promised.** The receiving server and transport providers necessarily process a source IP. Before public deployment, audit access logs, error logs, TLS termination, CDN analytics and provider retention. Suppressing application logs alone does not make the entire connection anonymous.

The reference collector binds to loopback only and stores daily aggregate counts by version and mode. It does not persist individual requests or headers. Default per-client HTTP and exception logging are disabled. Its global rate limiter uses no client identifier; it does not prevent fraudulent counts.

**Boot events are not unique users.** Reboots, opt-outs, offline machines, copied images and shared devices prevent a reliable user count with this protocol. Never label the resulting metric "users".

The counter is disabled with `sudo daylight telemetry off`. No public endpoint is assumed to exist merely because the client and collector source code exist. Collector deployment and complete proxy/provider privacy review remain release gates.
