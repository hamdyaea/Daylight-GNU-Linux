# Installation, update and removal

This release candidate supports Debian-based AMD64 and ARM64 systems. The packages do not change the kernel, OS identity, network, display-manager selection or existing home configurations. Inspect APT's proposed changes before accepting them. Keep a backup appropriate for your machine; package removal is not a disk snapshot.

## Minimal server-safe core

Choose the matching core architecture. For a 64-bit Raspberry Pi:

```sh
sha256sum -c SHA256SUMS
sudo apt install ./daylight-core_5.0.0~rc1_arm64.deb ./daylight-themes_5.0.0~rc1_all.deb
daylight status
daylight info
daylight doctor
```

A checksum detects corruption but is not independently authenticated when downloaded from the same untrusted source. Obtain releases from the official repository and verify available signatures/provenance.

## Full desktop

In a directory containing one matching core plus the architecture-independent packages:

```sh
sudo apt install ./daylight-core_5.0.0~rc1_arm64.deb ./daylight-themes_5.0.0~rc1_all.deb ./daylight-desktop_5.0.0~rc1_all.deb ./daylight-apps_5.0.0~rc1_all.deb ./daylight-linux_5.0.0~rc1_all.deb
```

Use the AMD64 core instead on a PC. Install `daylight-games` separately when desired. The boot counter is not a dependency of `daylight-linux`.

Select the Daylight GNU/Linux session in an existing display manager. On a suitable local console, `startx /usr/bin/daylight-session` is an alternative. Do not launch it as root or try to replace a productive server's active session remotely. Installing the packages alone does not start a graphical session.

Fastfetch and Terminology are optional. Without them, Daylight uses its built-in ASCII information display and Xterm. On Debian 12, do not add Debian 13 repositories to obtain Fastfetch. User settings are stored under `${XDG_CONFIG_HOME:-$HOME/.config}/daylight`.

## Updates

```sh
daylight update --dry-run
sudo daylight update
```

These commands ask APT to update installed Daylight packages, with no full distribution upgrade and no removal during the upgrade request. A signed Daylight repository must first exist and be configured, or matching newer `.deb` files must be installed locally. No public APT endpoint is assumed operational by this source tree.

## Removal

Log out of the Daylight graphical session before removing its desktop packages.

```sh
daylight remove --dry-run
sudo daylight remove
```

Removal targets installed Daylight packages and never invokes autoremove. APT may propose additional removals if independently installed software depends on Daylight; inspect its confirmation. Shared dependencies and personal Daylight settings remain. Pre-existing shell/Fluxbox/Conky files and OS identity are not overwritten in the first place.

## Privacy

Do not install or enable `daylight-telemetry` unless its collection policy and HTTPS endpoint have been reviewed. The reference collector is not a production deployment. See `PRIVACY.md`.
