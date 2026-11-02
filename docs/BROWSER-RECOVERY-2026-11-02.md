# Browser preview recovery and verification — 2 November 2026

Developer and founder: **Hamdy Abou El Anein**. Contact: **info@daylightlinux.ch**.

## Public result

**https://daylightlinux.ch/live/** opens the actual Alpine/Fluxbox graphical preview without a GitHub account. The main site's Try online entry points to this page, not to Codespaces. Start explicitly downloads and starts the guest; nothing starts automatically.

The preview includes the branded landscape and dark/gold Fluxbox theme, real movable windows, taskbar, desktop menu, terminals, a native calculator and a native About dialog. The web controls send fixed keyboard shortcuts to the real guest window manager. This is not an interactive screenshot or a server-side terminal session.

It is deliberately a small **Alpine Linux x86 browser preview**, not the complete Debian/Raspberry Pi OS Daylight release, nor a Raspberry Pi emulator. The installable release remains **5.0.0-rc.2**, with ARM64 and AMD64 packages.

The guest executes through v86/WebAssembly on the visitor's device. It receives **256 MiB RAM plus 8 MiB video memory**; the browser needs additional memory. The six runtime payloads total **41,401,978 bytes**, approximately 42 MB. The separate corresponding-source ZIP is not part of the startup download. No public Docker container, QEMU process or other guest runtime was started on the production Pi. A dedicated server is not needed for this client-side design; hosting full server-side sessions would require a different isolated, capacity-limited service.

Guest networking has no external relay; host disks, persistent session storage and a clipboard bridge are not attached. There is no guest telemetry. The browser still downloads static files over HTTPS, with ordinary hosting/network connection metadata. Closing or stopping discards session changes; a running guest pauses when its tab is hidden and its session limit is 20 minutes. These are design constraints, not a claim of complete anonymity or a security audit.

## Failures corrected, not ignored

1. **Interrupted transfers and workstation DNS/network loss.** Runtime download failures now have at most three transport attempts and a 90-second per-attempt deadline. Stop cancels transfers. A bad SHA256 or oversized payload still fails immediately. This does not claim to repair the workstation's physical Internet connection.
2. **Stale CDN compatibility URL.** The entry page already selects versioned JS/CSS URLs. The access test was mistakenly comparing an old cached unversioned `demo.js`. It now parses and verifies the exact fingerprinted resources used by the current page, requiring the expected same-origin URL and full content hash. No integrity checks were removed.
3. **Premature X11 assertion.** A second terminal process existed before its window was mapped. The browser test now polls the actual expected process/visible-window state within a bounded limit instead of assuming that two seconds is always sufficient. The visibility requirements are unchanged.
4. **HTTP entry path.** Public HTTP requests now redirect to HTTPS for the Daylight virtual host only. This avoids entering the WebAssembly/crypto-based preview from an insecure context. Query strings and missing-trailing-slash routes were checked. Local origin diagnostics without the proxy header are unchanged.

The existing `no-transform` HTML policy remains in place so proxy-injected analytics do not violate the strict page CSP. The earlier Cloudflare RUM failure is described in `GRAPHICAL-PREVIEW-STATUS-2026-11-02.md`. CSP was not weakened and GitHub failure notifications were not disabled.

The APT root has a human-readable landing page. Automatic directory listing remains disabled. Repository keys, signed metadata, expiry and package index hashes continue to be checked.

## Exact validation

Published native-preview source tree: `dec3f1bdfa18a9ebb3d63d5ac94ce8c84bcff0b1`, published on master in commit `56c2bbf94f72cb8173989f1ae23a17d3d6d33e80`. This matches reviewed local source commit `593c8f6e23ca347703ae07aef5fc1ab4129a25fb` at the tree level. The later HTTP redirect script is a separate scoped configuration fix, not a rebuild of the Linux image.

Runtime manifest SHA256: `5ae2cdf4e22623bae0af292f6ff3f7111ad8a3da3614b4b80c5041e5909770fc`.

Tested interface SHA256:

- index.html: `2ffcdc921c204c043db313b0ab23976e721c5de0d36ab71c5dd269e4f78fd1f1`
- demo.js: `b8a91ac96994537450cbd0e1c6658773c19965691233b35e812c94794a23ee0c`
- demo.css: `51b3ca347a17f5c712a18012aa9fb787fecf27bb032d5bb73a9c9c7f85defe88`

Completed checks:

- **Seven offline regression tests** for exact versioned resource selection, same-origin absolute URLs, obsolete URLs, wrong versions, external URLs, duplicates and missing stylesheets.
- **Five controlled local transport tests** for recovery, hash rejection, size limits, cancellation and retry exhaustion. Faults were injected only into the local test browser, not the production service.
- A real local browser boot and interaction check for the exact runtime and interface bytes.
- The same complete check against **public HTTPS**: real keyboard input into xterm, two visible terminal windows, a native calculator, native About dialog, desktop hide/restore, menu, pause/resume and stop. The frame was 1024 × 768. No external-origin requests or pre-consent guest downloads were observed.
- **Fourteen public HTTPS resource checks**, including APT key, signature, expiry and both architecture indexes.
- Rebuilt website structure: **32 pages and 1,572 local links**.

Independent GitHub Actions checks all completed successfully:

- **41460431455**: reviewed source publication and regression checks.
- **41460500135**: public graphical guest and exact public access checks.
- **41460504282**: website build, structure and desktop/mobile/no-JavaScript navigation.
- **41460507824**: actual public APT installation/removal on disposable Debian 12 and Debian 13 clients.

The graphical evidence artifact is `daylight-browser-preview-2`, SHA256 `cf7561616998e64e3eea10c48c6273e98a707e03f85ec2afded80abcf3fb2584`. It contains actual screenshots, input evidence and the PASS result. The calculator/About screenshot was visually inspected. Older failed attempts remain in history; they are not represented as successful runs.

## Production boundary and final access

Final origin verification checked **67 website-manifest files and 18 browser-deployment files** against their hashes. Apache, cloudflared, Docker and WireGuard retained their active states and main PIDs. Nextcloud remained installed, outside maintenance mode and without a pending database upgrade. The APT refresh timer and historical site remained available.

The only service operation in this recovery was a **graceful Apache reload** for the Daylight-only public HTTP redirect, after configuration validation and backup. There was no Pi reboot, production-container restart, global upgrade or server-side guest deployment.

Verified public routes include `/apt`, `/live`, their trailing-slash forms, the www host, and HTTP-to-HTTPS conversion for `/live/?lang=fr` and `/apt/`.

A desktop/laptop browser with keyboard and mouse is recommended. These tests do not certify physical Safari/iOS behavior, all graphics hardware, or the complete Raspberry Pi desktop. The preview remains experimental and the Debian release remains a release candidate.
