# Daylight Web Preview

Developer: Hamdy Abou El Anein — info@daylightlinux.ch.
Daylight glue and interface: GPL-3.0-only. Upstream licenses remain separate.

## What users get

https://daylightlinux.ch/live/ opens a real graphical Linux guest without a GitHub account. The **Démarrer / Start** button downloads the emulator, firmware, kernel and initramfs; it then boots Alpine x86 and Fluxbox inside WebAssembly. Startup opens exactly one visible, focused terminal titled **Daylight Start**. Calculator and About stay closed until explicitly requested. The same terminal launcher is used by automatic startup, the native menu and guest keyboard shortcut. The boot-ready event is emitted only after the real terminal is mapped, focused and its prompt initialised.

Windows, the taskbar, the desktop menu, xterm, the calculator and the About dialog are real guest processes. The preview uses the same dark/gold Fluxbox theme as Daylight, not a missing upstream theme name. The web toolbar contains only Start, Restart and Stop. Applications remain accessible in the native Fluxbox menu and through guest shortcuts.

The guest receives 256 MiB of RAM plus 8 MiB video memory. The browser/emulator needs additional memory. The six runtime payloads total about 42 MB; timing depends on the device and network. Nothing boots or downloads the guest payload before Start. Background tabs pause a running guest; returning to the tab resumes it automatically. The session stops after 20 minutes. Stop/reset/closing discards modifications. No guest network relay, shared host filesystem, account, clipboard bridge or telemetry is configured. Serving the page still exposes ordinary connection metadata to hosting/network providers.

This is an experimental, deliberately pruned Alpine preview, not the complete Debian Daylight release, a Raspberry Pi emulator, or a generally upgradeable Alpine system. The main product remains Raspberry Pi OS/Debian ARM64. The full Debian AMD64 ISO remains available separately.

## Why it does not need a dedicated server

v86 executes the guest on the visitor's device; the production Raspberry Pi only serves static files. Docker is not required at runtime. A future server-side full-ISO service would be a different design, requiring isolated per-user guests, resource/session limits, abuse controls and capacity planning. It must not share an unrestricted Docker socket, production disks, SSH agent or application credentials with visitors.

## Rebuild safely

Build on an unprivileged x86_64 Linux workstation, not on the production Pi. Prerequisites are Python 3, Node.js, bubblewrap, curl, bsdtar, cpio, gzip and Bash, with working user namespaces. The build never installs guest packages into the host. Alpine package signature verification stays enabled.

```sh
python3 web-live/build.py
node web-live/test-boot.mjs
python3 web-live/collect-sources.py
python3 web-live/package.py
```

An existing disposable root requires explicit `--reuse`. Inputs, package versions, firmware and original source hashes are pinned. Distribution mirrors can eventually remove old package versions; preserve published release inputs and corresponding sources. This is not a claim of cross-host byte reproducibility.

`collect-sources.py` retains the exact copyleft-origin sources/patches and aports recipes and the upstream firmware/emulator sources. `package.py` checks those hashes and creates an allowlisted runtime plus a separate corresponding-source ZIP. The large source ZIP is never part of the normal startup download. No host font files, credentials, signing keys, host homes or private logs are published.

## Validate the actual graphical guest

Serve `dist/web-live-publish` on 127.0.0.1:34403. With Playwright and Chromium installed in a project-local environment:

```sh
node web-live/test-browser.cjs
```

The browser check waits for actual graphical readiness, captures the canvas, types through the browser into xterm and verifies the resulting guest file, requires the Daylight Start title and terminal focus, verifies zero automatic calculators/About dialogs, opens a second consistently titled terminal and an on-demand calculator, verifies the native About dialog, hides/restores real windows, opens the menu, and checks pause/resume/stop. It rejects external-origin requests and pre-consent guest downloads. A serial boot message alone is not sufficient.

Use `DAYLIGHT_DEMO_URL=https://daylightlinux.ch/live/` to repeat it against public HTTPS. `DAYLIGHT_PLAYWRIGHT` and `DAYLIGHT_BROWSER` can point to existing project-local tools. This is not physical Safari/iOS certification; a desktop/laptop browser with keyboard and mouse is recommended.

Publication uses `server/deploy-web-live.py`, requiring successful browser evidence for the exact runtime manifest. The general website deployer skips `/live` so a site rebuild cannot replace a validated runtime. Payload filenames contain content hashes; metadata and the HTML entry point are replaced last. No emulator daemon or public server-side container is launched.

Upstream documentation: https://github.com/copy/v86 and https://copy.sh/v86/ .

## Public HTML and CI failures

The Daylight virtual host sets `Cache-Control: public, max-age=0, must-revalidate, no-transform` on HTML. This prevents a reverse proxy from injecting analytics or email-rewriting scripts into reviewed pages. The strict CSP is retained; third-party scripts are not allowlisted to make a test pass. `server/configure-static-delivery.py` applies only that scoped policy, with configuration checks, a backup and a graceful Apache reload.

An actual public CI failure in run 41453755155 was caused by Cloudflare's injected RUM beacon outside Europe. The guest had reached its desktop and passed the keyboard/window tests, but the browser correctly rejected the unexpected external script. The unchanged run passed after the origin delivery policy was corrected. Old failed attempts remain in GitHub history; notifications were not disabled to hide errors.

## Transport and cache regressions

Runtime downloads retry transport failures at most three times, with a 90-second per-attempt deadline. Cancellation is respected. An incorrect SHA256 or oversized response is rejected immediately; no verification is bypassed. `node web-live/test-transfer.cjs` injects controlled local transport failures and tests retry recovery, integrity rejection, size bounds, cancellation and exhaustion.

The public check follows the exact fingerprinted JS/CSS URLs in the current HTML, rather than testing stale unversioned CDN compatibility URLs. `python3 tests/test_web_live_interface.py` checks same-origin resource selection and rejects missing, duplicated, old or external resources.

The graphical browser test polls the actual X11 mapping state of launched windows within a fixed limit instead of assuming that an emulated process is visible exactly two seconds after creation. It still fails when the expected windows do not become visible.

## Three-button startup and network handling

The toolbar has only Démarrer / Redémarrer / Stop (Start / Restart / Stop in English). The terminal still opens in the foreground as Daylight Start. Native menu and shortcuts remain available; calculator and About are not automatically launched. A running guest pauses when the tab is hidden and resumes on return without a separate Pause button.

All startup file requests, including the initial JSON manifest and emulator library bytes, use cancellable bounded transfers. A transient network failure or selected transient HTTP response gets at most three attempts. The manifest is limited to 64 KiB and validated before payload downloads. Invalid JSON, wrong hashes, oversized content and non-retryable HTTP errors are rejected. Error messages identify the failed step rather than expose only “Failed to fetch”. A failing browser/network cannot be made reachable by retries alone; the UI never claims that it can.

The script element retains Subresource Integrity and same-origin loading, after its bytes have been independently verified. No CSP restriction is relaxed. Stop aborts the current transfer/retry and suppresses stale errors; Restart starts a new session.

`web-live/test-startup-network.cjs` runs only against a localhost preview. It reproduces a failed initial manifest request, checks recovery, bounded failure, invalid replies, cancellation and the three-control layout. It must not fault-inject the public server.
