# Daylight Web Preview

Developer: **Hamdy Abou El Anein** · Contact: **info@daylightlinux.ch**.
Daylight glue/interface/build scripts: **GPL-3.0-only**. Upstream software retains its own licensing.

## What this is

A real **Alpine Linux 3.22.7 x86** guest, Xorg framebuffer, Fluxbox, Xterm and the Daylight landscape, running in the visitor's browser through **v86 0.5.473 / WebAssembly**. It is not a screenshot simulation, a remote Docker session, the AMD64 Debian live ISO, or the ARM64 Raspberry Pi edition. The full Daylight Rust application suite is not included in this exploratory preview.

The static website supplies approximately 42 MB on first start. The Linux guest receives **256 MiB RAM**; browser/JIT overhead is additional. Starting requires a deliberate click. There is no public guest process on the Raspberry Pi server, no guest network relay, no shared host filesystem, no clipboard bridge, no persistent guest storage and no telemetry. HTTPS hosting still sees ordinary connection metadata; this is not anonymous transport.

The desktop pauses when a running session's tab is hidden. Stop/restart/closing the page discards the guest's temporary changes. A session expires after 20 minutes. This is not a secure memory-erasure guarantee: do not enter secrets. A current desktop browser and physical keyboard are recommended; mobile/Safari compatibility is not certified by the Chromium tests.

## Why not just Docker on the production Pi?

A container still executes on its host. A graphical container plus noVNC would consume host memory/CPU for each visitor and require isolation, quotas, expiry, abuse controls and network restrictions. This preview instead emulates its CPU on the visitor's device. The Pi only serves static files, like downloads. A separately isolated x86/KVM server would be appropriate for future full hosted Debian sessions, not required for this client-side preview.

v86 does not execute 64-bit kernels. The existing AMD64 RC2 ISO therefore remains a separate local/private QEMU-noVNC option. This Alpine x86 guest is deliberately labeled as a preview rather than pretending to be that ISO.

## Build on an unprivileged x86_64 Linux workstation

Requirements: Python 3, bubblewrap with working unprivileged user namespaces, curl, bsdtar, GNU cpio/gzip, Node, and previously rendered Daylight artwork. No host package or production container is changed by the recipe.

```sh
python3 web-live/build.py
```

Use `--reuse` only to reuse the project's existing disposable `dist/web-live-build/root`. A fresh build pins every APK package version and retains normal signed Alpine verification. The minirootfs, npm archive and firmware identities are locked. If an upstream mirror removes a pinned version, the recipe must fail rather than silently select a different version. This recipe has been executed in its documented environment; it is not a claim of cross-host bit-for-bit reproducibility.

Unused DRI/LLVM acceleration payloads and unrelated kernel modules are removed. The transitive bochs, evdev and psmouse dependencies are retained and recorded in `kernel-modules.json`. The absolute VMware-style mouse event device is selected explicitly; selecting its relative sibling caused the initial pointer test to fail.

## Validate the actual guest and interface

```sh
node web-live/test-boot.mjs
python3 -m http.server 34403 --bind 127.0.0.1 --directory dist/web-live
# In another local terminal, with Playwright available:
node web-live/test-browser.cjs
```

The browser test uses a real Chromium window, waits for the guest's actual terminal shell, types a command with physical keyboard events, checks its resulting guest file through the local serial test channel, then verifies pause/resume/stop. Playwright's `keyboard.type()` does not synthesize physical Shift for punctuation; the test explicitly presses Shift+Period for `>` instead of confusing a test-driver limitation with guest input failure. No serial command substitutes for typing the tested command.

The preview's scoped CSP permits WebAssembly compilation and its local blob worker. This exception applies only to the demo page. No external script CDN or guest networking endpoint is permitted. Runtime payloads have content-addressed filenames; SHA256 and sizes are checked before boot. Their manifest is delivered over HTTPS, not advertised as an independently signed software release.

## Sources and static packaging

```sh
python3 web-live/collect-sources.py
python3 web-live/package.py
```

The source collector retains the exact copyleft-origin source archives, patches and APKBUILD recipes using their pinned SHA512 values, plus SeaBIOS/v86 source and build configuration. The separate source ZIP is not fetched during startup. `packages.json` retains all package versions, origins, licenses and aports commits. Original upstream notices must be preserved; Daylight does not claim authorship of Alpine, Linux, Fluxbox, Xorg, v86 or firmware.

Packaging creates `dist/web-live-publish` containing an explicit deployment manifest. Serve that directory locally and repeat the browser test with `DAYLIGHT_DEMO_URL` pointing to it. The test records the exact public manifest SHA256. The deployment helper refuses a payload without a matching successful browser/keyboard result.

```sh
sudo python3 server/deploy-web-live.py \
  --source /reviewed/staging/web-live-publish \
  --evidence /reviewed/staging/browser-result.json --apply
```

That command only publishes static files under the existing Daylight web root. It does not install/start Docker, QEMU, noVNC, a daemon or a public shell service. The main website has a separate deployment helper. Always verify public HTTPS after deployment and retain production-service/Nextcloud before-and-after checks privately.

## References

- https://github.com/copy/v86 — emulator, API, architecture limitations and examples.
- https://github.com/copy/v86/blob/315b2b0/bios/fetch-and-build-seabios.sh — exact firmware build reference.
- https://gitlab.alpinelinux.org/alpine/aports — package build recipes pinned in the manifests.
- https://httpd.apache.org/docs/2.4/mod/core.html#servername — canonical HTTPS redirects behind TLS termination.
