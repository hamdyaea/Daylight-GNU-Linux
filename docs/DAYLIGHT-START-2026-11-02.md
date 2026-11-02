# Daylight Start — verified terminal-first preview

Developer and founder: **Hamdy Abou El Anein**. Contact: **info@daylightlinux.ch**. Daylight source license: **GPL-3.0-only**, with upstream licenses retained.

## Published behavior

The no-account browser preview at **https://daylightlinux.ch/live/** now uses **Daylight Start** for the entry button, terminal window/icon title and boot status. It starts **exactly one terminal in the foreground**. The calculator and About dialog remain available through their buttons/menu, but neither starts automatically.

The shared `web-live/daylight-terminal` launcher is used by initial startup, the Fluxbox menu and the keyboard shortcut behind the Terminal button. It consistently applies the title, geometry, colors and welcome shell. The terminal opens at 78 columns by 22 rows, with a compact sun/mountain ASCII banner, kernel and guest-memory information, example commands, developer/contact and technical-base disclosure. The complete welcome and prompt fit in the initial window.

The guest startup waits for Fluxbox, a visible terminal belonging to the launched process, its initialized banner marker and actual X11 focus before announcing desktop readiness. A process existing in the background is not enough. The existing bounded waits fail explicitly instead of advertising a ready desktop when startup is incomplete.

Alpine remains accurately disclosed as the lightweight web preview's technical base. No upstream license notice or OS identity was relabeled as Debian. The installable Raspberry Pi OS/Debian release remains **5.0.0-rc.2** and was not rebuilt or upgraded for this browser-only change.

## Source and exact validation

Reviewed local source commit: `cac321ab6877ce8e0958f86608ae3c1e0b0f2fd4`.
Published source commit: `5711f143bb27de06c5b9016ee0e570a7f264c497`.
Both have the exact source tree `af3a834c0062751f67a31c50cd11054ff9475f71`. Sources were published through the authorized repository integration without force rewriting history or exposing the owner's local credential.

The corresponding-source archive includes the two new shell helpers and the modified build/init recipe. The runtime remains a static client-side v86 guest, with 256 MiB guest RAM plus video/browser overhead. Its six payloads total **41,403,883 bytes**. No package was added to the guest or production Pi for this change.

Runtime manifest SHA256: `7a531dac9319e62f1f1d165ac18e46ddc03b9b1e1825cf91c05250d10a2b9339`.
Tested interface SHA256:

- index.html: `f9dc14713e1ddba2b0e39c1ba87151ab03c00a503710cb9fe5c07fd3da19933a`
- demo.js: `b8a9dd84d42cfb5e94bc108d3319714b0188e3100808b7e08331f1b24b8dfb07`
- demo.css: `51b3ca347a17f5c712a18012aa9fb787fecf27bb032d5bb73a9c9c7f85defe88`

Validation completed:

- Seven new startup-policy regressions and seven existing exact-resource-selection regressions passed.
- Five controlled local transport tests passed, preserving hash rejection, size limits, cancellation and bounded retry behavior.
- The rebuilt bilingual site passed 32-page and 1,572-local-link checks.
- The exact packaged guest passed a real local Chromium boot and interaction test.
- The same test passed against public HTTPS, both from the owner's workstation and independently from GitHub Actions. The startup record is `STARTUP=Daylight Start|1|0|0`: the active window title, one xterm, zero calculators and zero About dialogs.
- Browser keyboard input reached the actual shell. Opening a second terminal preserved the title. Calculator/About were tested on demand, together with menu, desktop hide/restore, pause/resume and stop. No external-origin requests or pre-click guest downloads were observed.
- The website's preview image now shows the actual initial terminal-only desktop, with a content-versioned filename to avoid retaining the earlier calculator screenshot in caches.

Successful independent GitHub Actions runs:

- `41465205897`: publication and source regression checks.
- `41465251232`: terminal-first policy, public access/signatures and actual graphical guest.
- `41465255614`: site build, desktop/mobile and no-JavaScript navigation.
- `41465259239`: public APT installation/removal on disposable Debian 12 and Debian 13 clients.

The graphical proof artifact is `daylight-browser-preview-3`, ID `13153265028`, SHA256 `d2503f35a95b1c26f4a7fc64f33b01c22bed77b894800208c0de0e58663a4063`. It contains `daylight-start.png`, `startup.log`, keyboard evidence and the PASS result. That initial screenshot, not the later test-created calculator windows, represents startup.

## Production boundary

The static deployment was backed up and verified: **66 website-manifest files and 18 browser-runtime files** matched their hashes on the Pi. Apache, cloudflared, Docker and WireGuard kept their active states and main PIDs. Nextcloud remained healthy, outside maintenance mode and without a pending database upgrade. The APT-signing timer and historical site remained available.

No production reboot, service reload/restart, network change, container deployment, new host package or public server-side VM was required in this intervention. Browser computation still happens on the visitor's device; the Pi only serves static files. The preview remains experimental and these checks do not certify every browser or physical device.
