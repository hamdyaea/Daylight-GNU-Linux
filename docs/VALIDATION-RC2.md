# Daylight 5.0.0-rc.2 — validation record

Developer: Hamdy Abou El Anein — info@daylightlinux.ch

## Exact candidate

**All candidate gates passed** in GitHub Actions run **41413451558**, run number **15**, completed on **2026-11-02**.

- Exact tested source: `1e234ed4d13bb1961cb1c9fc29bdf2f3393d59d2`.
- Workflow: `Daylight candidate validation` (`.github/workflows/daylight-build.yml`).
- Candidate artifact: `daylight-candidate-15`.
- Evidence artifact: `daylight-validation-15`, ZIP SHA256 `4e2cfb552dabcf8d7e502709333ec98e5a9ba1cfaf62ceac064ac362e133ed7a`.
- Tested ISO SHA256: `d41b373386f081e5d76926e356cb6ac8355c9b31935bacd628b9336e0e807e27`.

The publishing workflow consumes those tested files without rebuilding them. A source revision or a completed build is not itself proof of public release availability; check the release page and published manifest.

## Source, package and application checks

Rust formatting, strict Clippy, 27 Rust unit tests, 11 CLI integration tests, four collector tests, a signed-repository tamper test and ten release-tool/installer/site regression tests passed. Eight `.deb` files were produced: two native core architectures and six architecture-independent companion packages.

On both **Debian 12 Bookworm and Debian 13 Trixie**, the pipeline installed the packages, checked desktop entries, ran installed CLI tests and started a real Xvfb/Fluxbox/Conky desktop. Sixteen native application GUI tests passed on each release. It tested reinstallation and actual removal without autoremove and checked that the original OS identity and existing shell, Conky, wallpaper and classic Fluxbox files were retained.

These are focused integration tests, not a complete security audit or proof that every arbitrary third-party configuration is compatible.

## Real live boot and browser checks

The ISO's live filesystem first passed an offline direct-kernel smoke test. Separate tests then booted the **unmodified ISO through its actual BIOS and UEFI bootloaders**, with no guest network or host disks attached. Both reached the live user, Fluxbox and Conky and retained screenshots. UEFI **Secure Boot was disabled**.

The strengthened browser test started the actual private demo runtime, connected real Chromium through noVNC/WebSocket, waited for the guest's explicit live-user/Fluxbox/Conky readiness report and required a nonblank rendered desktop frame. The captured browser screenshot was inspected: it shows the approved Alpine-lake wallpaper, the exact Daylight Linux wordmark, Conky and the Fluxbox toolbar.

The readiness report uses a dedicated observation-only virtio serial channel. It does not share a host directory, disk, repository token or SSH agent with the guest.

Earlier failures were not hidden:

- The original BIOS menu had no automatic timeout.
- The shared GRUB configuration omitted a timeout entirely, leaving UEFI at its menu. Both menus now explicitly default to the first live entry after eight seconds; missing, zero and negative timeouts plus idempotency were regression-tested.
- An earlier browser test only proved VNC connectivity and captured a black frame before boot completed. It was replaced with the actual desktop-readiness and rendered-frame assertions above, then the entire candidate was rebuilt and revalidated.
- Full-image wallpaper scaling replaced cover cropping to preserve the wordmark on non-widescreen displays.

## Deployed website and APT verification

The static website and signed repository were deployed on the existing Daylight host without restarting Apache, Docker or the machine. An origin-file audit verified all 44 files in the initial deployment manifest. Public-file comparisons also passed, allowing only the specifically identified Cloudflare email-obfuscation transformation in HTML; all other content matched its source hash.

Both English and French editions were tested at desktop and mobile widths: **32 page/viewport combinations** passed without horizontal overflow or JavaScript exceptions. Automated axe-core WCAG 2 A/AA and 2.1 AA checks found no violations on the **16 main pages**. This does not replace a manual accessibility review.

The book page points to the supplied author store, and `linux-book.html` redirects to it. The old website is preserved under `old/site`. The current email in active sources and UI is `info@daylightlinux.ch`; historical immutable releases are not rewritten.

A genuine unprivileged APT client verified the public pinned signing key, InRelease signature, AMD64 and ARM64 indexes and package downloads using temporary state, without modifying host APT configuration. The production archive's restricted daily signing service was executed successfully and its timer is active. Its private key directory is outside the web root and mode 0700.

The deployed client bootstrap also passed on clean **Debian 12 and 13** in independent run **41410814616**: plan-only behavior, actual public installation, repeated repository setup without configuration drift, update/removal simulation and actual removal. No autoremove occurred and the base OS identity remained unchanged. That initial test used the then-published RC1; the RC2 archive import and native upgrade are recorded separately in the deployment report.

## Production Raspberry Pi boundaries

A core-only installation from the public repository was performed on the real Raspberry Pi. The initial installed version was the published RC1. Main PID/state snapshots for Apache, Docker, cloudflared and WireGuard, all running container start times, Nextcloud status and hashes of the OS identity, SSH configuration and Daylight virtual host were unchanged before/after installation. The desktop was **not** installed; no reboot, remote-access change or global upgrade was performed.

The subsequent RC2 archive import and the native core/themes upgrade must be verified against the actual published files. Do not infer that upgrade from this image-build result alone. Private infrastructure snapshots remain outside the public repository.

## Remaining boundaries

This remains a release candidate. Physical PC hardware, Pi graphical output/input, Wi-Fi, audio, Secure Boot and ARM32 are not certified by these tests. The browser demo is private, offline and disposable, not an anonymous public multi-tenant hosting service. Codespaces uses its user's allowance and can incur charges; stop/delete the Codespace separately.

The approved generated artwork is delivered at 1672 × 941, not falsely labeled native 4K. Two additional real CC0 photographs are rendered at 3840 × 2160 with provenance. No font files are redistributed as standalone artwork assets.

DistroSea listing depends on its operator and is not claimed. Mailbox delivery is not certified by the build. The optional telemetry collector is not activated in production, and the normal installer does not install or enable it. The immutable RC1 record remains in `VALIDATION.md`.
