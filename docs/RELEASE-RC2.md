# Daylight GNU/Linux 5.0.0-rc.2

A release candidate for 64-bit Debian systems, compatible Raspberry Pi OS ARM64 installations and the AMD64 PC live edition.

Developer and founder: **Hamdy Abou El Anein**. Project contact: **info@daylightlinux.ch**.

## Included

- A static Rust core, optional native applications/games, a separate Fluxbox session and Conky profiles. Existing shell, Conky and classic Fluxbox settings are not replaced.
- The approved photorealistic Alpine-lake artwork with an exact **Daylight Linux** wordmark, plus darker desktop/terminal derivatives. The delivered native resolution is 1672 × 941; these generated scenes are not advertised as documentary photographs or native 4K.
- Two additional real CC0 mountain photographs rendered at 3840 × 2160 with the same Daylight Linux signature. Provenance, author credits and checksums are retained. Full-image scaling keeps the lettering visible on different screen aspect ratios.
- Fastfetch configuration and an ASCII fallback. No external request is made when opening the terminal.
- A scoped, exact-fingerprint-pinned APT bootstrap. The default is a core-only plan; the desktop and application/game profiles require explicit flags. Installation never enables telemetry or performs a global distribution upgrade.
- Static signed APT hosting, by-hash indexes, atomic metadata publication, a dedicated archive account/private-key directory and a restricted daily signature-renewal timer.
- A bilingual static website, an Old section preserving the previous site, and an author/books page linking to the supplied official Amazon author page.
- A private QEMU/noVNC browser-demo environment using this real AMD64 ISO, with no guest network, no host disks and a bounded session lifetime. The production website host does not run visitors' VMs.
- Native BIOS and UEFI boot menus with an explicit eight-second default, correcting the indefinite menu waits found during testing.

## Publication gates

The exact source revision must pass Rust checks, CLI and collector tests, a signed-repository tamper test, installer/site regressions, package installation/removal and native dialogs on Debian 12 and 13, offline live-filesystem startup, real BIOS and UEFI ISO bootloader tests, and an actual Chromium/noVNC connection.

Published files are taken from that successful run, without rebuilding them. The release includes inspectable logs, actual screenshots, SHA256SUMS and installed-package provenance. Debian package filenames are normalized for GitHub downloads; internal version ordering retains `5.0.0~rc2`.

## Deployment checks

The public website and signed repository at **daylightlinux.ch** have been deployed separately from the image build. A genuine APT client verified both architecture indexes/downloads. The public client script was also exercised on clean Debian 12 and 13 containers: installation, repeated repository setup, update/removal simulation and actual removal without autoremove.

Consult the current deployment record and `/apt/status.json` for the state of the running service. A downloadable release and a public archive import are distinct steps; build files alone are not proof of deployment.

## Boundaries

This remains a candidate, not certification on all physical hardware. UEFI tests do not enable Secure Boot. Wi-Fi, audio and physical Pi desktop behavior need hardware-specific validation. The live image is temporary, with no disk installer or persistence by default. ARM32 is not supported by the normal installer.

The browser environment is private and disposable, not an anonymous public multi-tenant VM service. Codespaces uses the visitor's account and allowance; costs can apply. Ending the demo does not stop/delete the Codespace. DistroSea inclusion is controlled by its operator and has not been claimed or submitted automatically.

The optional boot collector is disabled and is not activated by this release. The contact address is used in current sources and UI; mailbox delivery is not certified by a software build. Historical immutable releases retain their original metadata.

Daylight code: **GPL-3.0-only**. Original photographs: **CC0-1.0**. Generated Daylight artwork is distributed under the project's stated terms to the extent copyright applies. Third-party notices are preserved; no standalone font files are redistributed with the artwork.
