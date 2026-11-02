# Graphical browser preview and CI correction — 2 November 2026

Developer: Hamdy Abou El Anein — info@daylightlinux.ch.

## Public, working preview

The public preview is **https://daylightlinux.ch/live/?lang=fr** (English: `?lang=en`). The website's Try online page leads directly to it. No GitHub account or Codespace is required for this path.

It runs an actual Alpine Linux x86 guest with Fluxbox in v86/WebAssembly on the visitor's device. It has a graphical wallpaper, movable windows, a taskbar, a real terminal and the Fluxbox desktop menu. Desktop, Linux menu and Terminal controls operate the actual guest. It is not a static screenshot or an imitation shell. The main installable product remains Debian/Raspberry Pi OS ARM64; this deliberately small Alpine preview is not the complete Daylight distribution or Raspberry Pi emulation.

The guest uses 256 MiB RAM, plus video memory and browser/emulator overhead. Initial runtime payload is about 42 MB. The source archive is a separate optional download. Nothing boots before Start; background tabs pause a running guest, Stop/reset/closing discards changes, and the session is bounded. No external guest-network relay, shared host disk, account or telemetry is configured. The production Raspberry Pi serves static files, not visitor containers or VMs; bandwidth use still exists.

## Why the public browser test failed

GitHub Actions run **41453755155**, first attempt, reached the real desktop and passed keyboard/window interactions but failed the no-external-request/CSP checks. Its retained evidence shows an automatically injected Cloudflare RUM script from `static.cloudflareinsights.com`. The page's strict CSP correctly blocked that script. Local European testing did not expose the same injection.

The fix was applied to **HTML under the Daylight virtual host only**:

```text
Cache-Control: public, max-age=0, must-revalidate, no-transform
```

The change uses `server/configure-static-delivery.py`, with an explicit apply flag, configuration checks, backup, rollback on failure and a graceful Apache reload. No CSP permission was widened and no analytics endpoint was allowed to make the test pass. The public HTML no longer contains the injected beacon or email-rewriting scripts. This header policy does not alter the large binary payload cache policy.

Cloudflare documents this origin-side control in its Web Analytics FAQ and Email Address Obfuscation documentation:

- https://developers.cloudflare.com/web-analytics/faq/
- https://developers.cloudflare.com/waf/tools/scrape-shield/email-address-obfuscation/

The **unchanged GitHub workflow passed on its second attempt**, against the actual public HTTPS endpoint, after the delivery fix. The exact source under test was `3d52ff22c0184006181d3f1c881491b28ec2c890`.

The retained result confirms a 1024 × 768 graphical surface, actual browser keyboard input into xterm, two real terminal windows, desktop hide/restore, pause/resume/stop, no automatic startup and **zero external-origin browser requests**. The complete boot-and-interaction sequence took 117,225 ms on that CI runner; this is not a promise of startup speed on other devices.

Evidence artifact: `13146651425`, name `daylight-browser-preview-1`, SHA256 `2be492f73ca4a1b5d7ab060337cda8de11b79ef885d9996ee4d2ee36a2bbc30e`. Earlier failed attempts remain in history; notification settings were not changed to hide failures.

## Access and production checks

A final check confirmed 200 responses for `/apt`, `/apt/`, `/live`, `/live/`, `/fr/try-online.html`, `/live/manifest.json` and `/apt/dists/daylight/InRelease`; directory redirects remain on HTTPS. HTML responses include no-transform. The APT landing page solves human browsing without enabling directory listing or relaxing file permissions. Internal directories need not expose automatic indexes.

Apache, Docker, cloudflared and WireGuard remained active with the same main PIDs; Nextcloud reported maintenance mode false. The signing timer remained active and the installed Daylight CLI reported 5.0.0-rc.2. Only the scoped HTML response policy was changed in this intervention; no production reboot or container restart occurred.

## Additional improvement prepared, not deployed

A separate local branch, `preview/native-widgets-20261102`, contains a corrected Daylight Fluxbox theme (the former upstream Black theme path did not exist), a native X11 calculator and an About dialog, and stronger deployment checks for the exact tested HTML/JS/CSS. The added Alpine packages are xcalc 1.1.2-r0 and xmessage 1.0.7-r0; no host package was installed.

Its local real-browser tests passed, including the calculator/About processes, actual keyboard, windows and lifecycle controls. Payload total: 41,401,978 bytes. Source/runtime provenance remains pinned. Its deployment was blocked by the tool security check and was not retried through a bypass. These additional native widgets are therefore **not claimed as publicly deployed**. The previously validated graphical preview remains available. Local sources, staged files and results are preserved for a subsequent authorized deployment.

## Boundaries

No claim is made of physical Safari/iOS certification, arbitrary hardware support or the complete Debian edition running in v86. A future public full-ISO remote-desktop service would need a separately isolated host, per-visitor sessions, quotas, abuse controls and capacity testing; it should not share the production Pi's unrestricted Docker socket, storage or secrets.
