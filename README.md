# Daylight GNU/Linux 5

**A lightweight, customisable desktop for Raspberry Pi OS 64-bit. A PC live edition to discover and test it.**

Founder and developer: **Hamdy Abou El Anein** · Contact: **info@daylightlinux.ch** · Daylight code: **GNU GPL v3**

[Website](https://daylightlinux.ch/) · [Raspberry Pi](https://daylightlinux.ch/raspberry-pi.html) · [Downloads](https://daylightlinux.ch/download.html) · [Community](https://daylightlinux.ch/community.html) · [Install](https://daylightlinux.ch/install.html) · [Try in your browser](https://daylightlinux.ch/try-online.html) · [Books](https://daylightlinux.ch/books.html) · [Old](https://daylightlinux.ch/old/) · [Français](README.fr.md)

## Raspberry Pi first; PC live for discovery

**Debian packages:** a Rust core for ARM64 or AMD64, themes, an independent Fluxbox session and optional native applications, for Debian 12/13 and compatible 64-bit Raspberry Pi OS installations.

**PC live edition:** a Debian 13 AMD64 ISO built from a clean base with those same packages. It does not clone a personal computer. SSH and telemetry are not active; there is no disk installer or persistence by default. The download page and `release/current.json` identify the version actually published. A development branch is not itself a release.

The **5.0.0-rc** series remains a release candidate. Virtual-machine validation is not certification of every physical device.

## Install through the signed public APT repository

Download, inspect and preview the bootstrap:

```sh
curl --fail --show-error --silent --proto '=https' \
  https://daylightlinux.ch/install.sh -o daylight-install.sh
less daylight-install.sh
sh daylight-install.sh --plan
```

Install the minimal core, without changing the desktop:

```sh
sudo sh daylight-install.sh --core --yes
daylight status
daylight info
daylight doctor
```

Choose `--desktop --yes` to add the desktop, or `--desktop --games --yes` to include optional games. `--repo-only --yes` only configures the repository. Without `--yes`, the bootstrap makes no changes.

**https://daylightlinux.ch/apt/** serves signed metadata using a dedicated key and priorities scoped to Daylight packages. Public key fingerprint:

```text
B057 5F82 1A31 DD20 753D E07C 50D2 1240 F4BC B02E
```

The installer does not perform a global distribution upgrade, reboot or enable telemetry. These are Debian/Raspberry Pi OS packages, **not Manjaro/Arch packages**. Read the [installation guide](docs/INSTALL.md), especially before changing a productive server.

## Desktop, terminal and applications

Fluxbox runs as a separate session; Conky provides lightweight profiles; the terminal displays the ASCII logo and system information through Fastfetch or its built-in fallback. Opening a terminal makes no external request. Native dialogs use YAD only while needed: no Electron and no permanent settings daemon.

Utilities and optional games share a small Rust executable: passwords, temperatures, date differences, local network information, alarms, speech integration and offline games. **Conky is configured and optimized, not rewritten in Rust.**

```sh
daylight control-center
daylight monitor
daylight password 24
daylight update --dry-run
sudo daylight update
daylight remove --dry-run
sudo daylight remove
```

APT operations require confirmation. Removal never runs autoremove and preserves shared dependencies and personal settings. Existing shell, Conky and classic Fluxbox configuration files are not replaced. This is not a bit-for-bit snapshot restore. No new display manager is installed automatically.

## Landscapes with the Daylight Linux signature

The approved photorealistic Alpine lake, dark desktop and terminal variants preserve the delivered generated artwork at **1672 × 941**. Two real CC0 mountain photographs complete the collection at **3840 × 2160**. The **Daylight Linux** wordmark remains visible across display aspect ratios.

Credits explicitly distinguish generated scenery from real photography. Original sources, checksums and native dimensions are recorded; an upscale is never advertised as native 4K. Fonts are rasterized during rendering, not redistributed as standalone font files. [Wallpapers](https://daylightlinux.ch/wallpapers.html) · [Artwork provenance](docs/ARTWORK.md)

## Browser testing without burdening the production server

**One-click lightweight preview:** [Daylight Web](https://daylightlinux.ch/live/?lang=en) boots a real Alpine x86 Linux/Fluxbox desktop inside the visitor's browser using v86/WebAssembly. No account or installation is required. The initial runtime download is about 42 MB and the Linux guest receives 256 MiB of RAM, with additional browser overhead. It has no external guest-network relay or persistent storage. This is explicitly an experimental Alpine preview, not the complete Debian/Raspberry Pi OS release. [Build, validation and sources](web-live/README.md)

**Complete Debian live edition:**

`demo/` supplies a private QEMU/noVNC environment using the real ISO, not an HTML imitation. The website links to its Codespaces configuration. **No visitor VM runs on the Raspberry Pi hosting the website.**

Codespaces uses the visitor's account and allowance; charges can apply. The guest has no network, host disk or persistence, and its lifetime is bounded. Stop/delete the Codespace separately after testing. This is not an anonymous public multi-tenant VM service. DistroSea inclusion is controlled by its operator and is not claimed. [Operation and security boundaries](demo/README.md)

## Evidence, privacy and maintenance

The pipeline validates Rust, CLI behavior, the collector, signed APT metadata, resources, installation/removal and native dialogs on Debian 12/13. It also tests the live filesystem, the actual BIOS/UEFI ISO bootloaders and a browser connection to an actually ready, rendered desktop. Exact revisions, results and remaining limits are documented in [the RC2 validation record](docs/VALIDATION-RC2.md) and retained release evidence.

The optional boot counter is disabled and is not installed by the bootstrap. Its server is not activated in production. It counts received boots, **not unique users**; an IP address is necessarily visible at the transport layer. See [privacy documentation](docs/PRIVACY.md).

Current sources, configuration and archive signatures use `info@daylightlinux.ch`. A software build does not certify mailbox delivery; GitHub issues remain available. Historical immutable releases retain their original metadata.

[Build](docs/BUILD.md) · [Archive and website operations](docs/OPERATIONS.md) · [Production safety](docs/PRODUCTION-SAFETY.md) · [Historical editions](https://daylightlinux.ch/old/)
