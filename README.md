# Daylight GNU/Linux 5

**A lightweight, reversible desktop layer for Debian and Raspberry Pi OS.**

Founder and developer: **Hamdy Abou El Anein**. Daylight code license: **GNU GPL v3**.

[Français](README.fr.md) · [Download 5.0.0-rc.1](https://github.com/hamdyaea/Daylight-GNU-Linux/releases/tag/v5.0.0-rc.1) · [Installation](docs/INSTALL.md) · [Verified tests](docs/VALIDATION.md)

## Published release candidate

**5.0.0-rc.1 is available**, with eight Debian package files, a Debian 13 AMD64 live ISO, screenshots, SHA256 checksums and inspectable test evidence. It is a release candidate, not a fully hardware-certified stable release.

The live image is approximately 1.27 GB. It uses the same packages and is not a clone of a personal machine. Boot telemetry and SSH are disabled; no disk installer or persistent storage is included.

![Actual Daylight live desktop](https://github.com/hamdyaea/Daylight-GNU-Linux/releases/download/v5.0.0-rc.1/daylight-live-desktop.png)

## Components

- A dependency-free Rust CLI for local information, diagnosis, settings and APT update/removal operations.
- An isolated Fluxbox session, configurable Conky profiles, Fastfetch and a built-in ASCII fallback.
- Native on-demand application dialogs using YAD, with utilities and optional offline games. No Electron or resident settings daemon.
- Mountain/sun vector theme prototypes and the historical wallpaper.
- An optional boot counter, disabled by default. The reference collector is not deployed.

Package types: `daylight-core`, `daylight-themes`, `daylight-desktop`, `daylight-apps`, `daylight-games`, `daylight-telemetry`, and the `daylight-linux` metapackage. Core has separate ARM64 and AMD64 builds; the six other packages are architecture-independent.

## Installation

Read [INSTALL.md](docs/INSTALL.md) and inspect APT's changes before applying them. Debian packages are not Manjaro/Arch packages. For the minimal core on a 64-bit Raspberry Pi, download the matching release assets and run:

```sh
sudo apt install ./daylight-core_5.0.0.rc1_arm64.deb ./daylight-themes_5.0.0.rc1_all.deb
daylight status
daylight info
daylight remove --dry-run
```

GitHub normalizes `~` to `.` in release filenames. The internal Debian version remains `5.0.0~rc1`; local builds retain the tilde filenames. Install only one core architecture.

Installation does not replace existing shell/Fluxbox/Conky configuration or start a display manager. Removal does not run autoremove and retains personal settings and shared dependencies. It is not a disk-snapshot restore.

## Validation

The exact candidate commit `85715705501b18138712173327b7df1fb63ef889` passed the complete validation workflow: 27 Rust unit tests, 11 CLI tests, 4 collector tests, a signed APT repository test, and installation/reinstallation/removal on Debian 12 and 13. Sixteen GUI tests passed on each Debian release. The live filesystem booted offline under QEMU with the live user, Fluxbox and Conky; the screenshot above is from that test.

Native ARM64 CLI checks also passed on the maintainer's Raspberry Pi without installing a desktop or interrupting production services. See [VALIDATION.md](docs/VALIDATION.md) for exact scope and limitations. The live test does not certify BIOS/UEFI bootloaders, Secure Boot, physical Wi-Fi/audio or a physical Pi graphical session.

## Remaining work and contact

The signed APT builder is implemented and tested, but no public Daylight APT repository is deployed. `daylight update` requires a configured source of newer packages. Production telemetry hosting, 32-bit ARM, final photorealistic wallpapers and broader hardware certification remain separate tasks.

The project mailbox **contact@daylightlinux.ch is pending activation**. Use this repository's issues until delivery has been verified.

Original code retains GPLv3; third-party component licenses remain applicable. See [SOURCES.md](docs/SOURCES.md), [THIRD_PARTY.md](docs/THIRD_PARTY.md), [PRIVACY.md](docs/PRIVACY.md) and [BUILD.md](docs/BUILD.md). Historical versions are preserved under `old/*`, with their original branches also retained.
