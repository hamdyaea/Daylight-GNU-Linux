# Installation, update and removal

This release candidate supports Debian-based AMD64 and ARM64 systems. The packages do not change the kernel, OS identity, network, display-manager selection or existing home configurations. Inspect APT's proposed changes before accepting them. Keep an appropriate backup; package removal is not a disk snapshot. These .deb files are not Arch/Manjaro packages.

## Published filenames versus local builds

The public release is `v5.0.0-rc.1`. GitHub normalized the tilde in uploaded filenames, so downloaded files use `5.0.0.rc1`, while locally built files use `5.0.0~rc1`. Their internal Debian version is **5.0.0~rc1** in both cases. The following commands use the published filenames. Select exactly one core architecture.

## Minimal server-safe core

For a 64-bit Raspberry Pi, after downloading the matching files:

```sh
sudo apt install ./daylight-core_5.0.0.rc1_arm64.deb ./daylight-themes_5.0.0.rc1_all.deb
daylight status
daylight info
daylight doctor
```

`sha256sum -c SHA256SUMS` verifies the complete downloaded set. If only selected assets are downloaded, verify their corresponding lines and distinguish missing files from mismatched hashes. Checksums detect corruption but are not independent authentication when obtained from the same untrusted source; obtain files from the official repository.

## Full desktop

```sh
sudo apt install ./daylight-core_5.0.0.rc1_arm64.deb ./daylight-themes_5.0.0.rc1_all.deb ./daylight-desktop_5.0.0.rc1_all.deb ./daylight-apps_5.0.0.rc1_all.deb ./daylight-linux_5.0.0.rc1_all.deb
```

Use the AMD64 core instead on a PC. Games and telemetry are separate optional packages. Installing the desktop does not automatically install or start a display manager. Select the Daylight GNU/Linux session in an existing display manager; on a suitable local console, `startx /usr/bin/daylight-session` is an alternative. Do not launch a desktop as root or replace a productive server's active session remotely.

Fastfetch and Terminology are optional. Without them, Daylight uses its built-in ASCII information display and Xterm. Do not add Debian 13 repositories to Debian 12 merely to obtain Fastfetch. User settings are stored under `${XDG_CONFIG_HOME:-$HOME/.config}/daylight`. Fluxbox may create missing compatibility files under `~/.fluxbox`, but existing files there are not replaced.

## Updates

```sh
daylight update --dry-run
sudo daylight update
```

These commands ask APT to update installed Daylight packages, not to perform a distribution upgrade. A signed Daylight repository must first exist and be configured, or newer .deb files must be installed locally. The public repository is **not yet deployed**; the builder and its signature/tamper tests are supplied.

## Removal

Log out of the Daylight graphical session before removing its desktop packages.

```sh
daylight remove --dry-run
sudo daylight remove
```

Removal targets installed Daylight packages and never invokes autoremove. APT may propose additional removals if other installed software depends on Daylight; inspect its confirmation. Shared dependencies and personal settings remain. Existing shell/Fluxbox/Conky files and base OS identity are not overwritten in the first place. This is not a snapshot rollback.

## Live ISO and privacy

The AMD64 ISO is for PC exploration, not a Raspberry Pi boot image. The validated QEMU test boots its live filesystem with extracted kernel/initrd; BIOS/UEFI, Secure Boot and physical hardware require separate validation. It includes no disk installer, persistence or active telemetry. Do not mount or modify internal disks when exploring the live session.

Do not enable `daylight-telemetry` unless its collection policy and HTTPS endpoint have been reviewed. The reference collector and public mailbox are not deployed/activated. See `PRIVACY.md` and `VALIDATION.md`.
