# Daylight GNU/Linux 5.0.0-rc.2

A release candidate for 64-bit Debian systems, Raspberry Pi OS ARM64 and the AMD64 PC live edition.

## Included

- A small static Rust core, optional native applications and games, an independent Fluxbox session and Conky profiles.
- Genuine photographic 4K backgrounds from pinned CC0 originals, with credits retained and no cropped wordmark.
- A scoped, fingerprint-pinned APT installer. Core-only is the default plan; the desktop is explicit, and telemetry is never enabled by installation.
- A static signed APT archive deployment kit, content-addressed indexes, atomic metadata publication and a constrained daily signature-renewal timer.
- A bilingual static website with a dedicated Old section.
- A private browser-demo configuration that runs this actual AMD64 ISO through QEMU/noVNC, with no guest network or host disks and a bounded session lifetime.

## Validation required for this publication

The exact source revision must pass Rust checks, CLI and collector tests, a signed-repository tamper test, installer/site regressions, package installation/removal and native dialogs on Debian 12 and 13, offline live-filesystem startup, real BIOS and UEFI ISO bootloader tests, and a real Chromium/noVNC connection. The release includes inspectable logs, screenshots, checksums and installed-package provenance. The files are retrieved from the passed build, not rebuilt for publication.

## Boundaries

This is a candidate, not a claim of certification on all physical hardware. UEFI tests do not enable Secure Boot. Wi-Fi, audio and physical Pi desktop testing remain hardware-specific. The live image is temporary, with no disk installer or persistence. ARM32 is not supported by the normal package installer.

The browser environment is private and disposable, not an anonymous public multi-tenant VM service. GitHub Codespaces uses the visitor's own account and allowance; charges can apply beyond that allowance. DistroSea inclusion is controlled by its operator and is not asserted by this release.

The public APT endpoint and website deployment have separate operational checks. See the deployment record in the current documentation rather than treating deployment scripts as proof of an active service.

Daylight code: GPL-3.0-only. Photographs: CC0-1.0. Third-party notices are retained. Developer: Hamdy Abou El Anein.
