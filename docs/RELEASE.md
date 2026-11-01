# Daylight GNU/Linux 5.0.0-rc.1

Founder and developer: **Hamdy Abou El Anein**. Daylight source code is licensed under **GNU GPL v3**; third-party notices are retained.

This is a **release candidate**, not a stable production release. The publishing workflow only accepts the exact commit that passed its full validation run and publishes those tested artifacts without rebuilding them.

## Included

A small dependency-free Rust application suite, an independent Fluxbox session, configurable Conky profiles, custom terminal information with Fastfetch and an ASCII fallback, mountain/sun vector themes and the historical wallpaper. Utilities include passwords, temperature conversion, dates, local network information, speech integration and a visible cancellable timer. Games are optional. No Electron or resident settings service is required.

Seven package types are supplied: core, themes, desktop, apps, games, optional telemetry and the linux metapackage. Core is built separately for **ARM64** and **AMD64**. Select exactly one core architecture; do not install both together. The other six packages are architecture-independent.

The **Debian 13 AMD64 live ISO** uses the same packages. It does not clone a personal machine. SSH and boot telemetry are disabled, swap activation is disabled, and no disk installer or persistence is included. Do not mount or modify internal drives when trying the live session.

## Validation evidence

The accompanying `daylight-validation.zip` contains the source commit, automated test logs and desktop captures. Checks cover Rust unit tests and strict Clippy, CLI integration, optional collector input validation, and package installation/reinstallation/removal on Debian 12 and 13. Native application windows are exercised under Xvfb. Existing shell, Conky, wallpaper and classic Fluxbox configuration fixtures are checked for preservation.

The ISO filesystem is additionally booted offline with QEMU using the ISO's extracted kernel/initrd; Fluxbox and Conky startup are checked and a screenshot is retained. **This is not certification of BIOS/UEFI bootloaders, Secure Boot, Wi-Fi/audio hardware or physical PC compatibility.**

Native ARM64 CLI tests were also performed on the maintainer's Raspberry Pi without installing a desktop or interrupting production services; see the validation document for scope.

## Installation and limitations

See `docs/INSTALL.md` for architecture-specific APT commands and dry-run removal. Existing home configurations are not overwritten. Fluxbox itself may create missing compatibility files under `~/.fluxbox`; Daylight's active settings remain separate. Removal keeps personal settings and shared dependencies and does not run autoremove or restore a disk snapshot.

The signed APT repository builder is supplied, but a public repository on daylightlinux.ch is **not yet deployed**. `daylight update` needs an explicitly configured repository with newer packages or newer local `.deb` files.

Telemetry is an optional package, disabled by default, and its reference collector is not deployed. It counts received boot events, not unique users, and does not promise that transport IP addresses are invisible.

The public mailbox `contact@daylightlinux.ch` is pending activation; use GitHub issues meanwhile. The new vector graphics are working designs, not the final photorealistic wallpaper collection. A 32-bit ARM build and broader hardware certification remain outside this candidate.

Checksums detect corruption. The release checksum list is not a separately signed public trust anchor. Download only from the official project repository.
