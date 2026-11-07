# Installation, update and removal

Developer: Hamdy Abou El Anein — info@daylightlinux.ch

Daylight adds optional components to Debian 12/13 and compatible 64-bit Raspberry Pi OS installations. Supported executable architectures are **amd64 and arm64**. It is not a Manjaro/Arch package and the PC live ISO is not a Raspberry Pi boot image.

## Public signed repository

The repository is operational at **https://daylightlinux.ch/apt/**. It publishes only the seven Daylight package types, with separate AMD64/ARM64 core binaries. APT verifies the signed metadata and package checksums. The dedicated signing-key fingerprint is:

```text
B057 5F82 1A31 DD20 753D E07C 50D2 1240 F4BC B02E
```

Metadata expires after 30 days and is renewed by a restricted daily service. `/apt/status.json` reports the last signing time and package-file count. The private key is not published. The source tree's `release/current.json` identifies the release that was actually published; a development branch or a pending CI run is not a downloadable release.

## Download, inspect and choose a profile

```sh
curl --fail --show-error --silent --proto '=https' \
  https://daylightlinux.ch/daylight-install.sh -o daylight-install.sh
less daylight-install.sh
sh daylight-install.sh --plan
```

The default is **plan-only and core-only**. No files or packages change without `--yes`. The script refuses unsupported architectures, pins the exact archive key and scopes repository priority to Daylight packages. It checks signatures and metadata expiration without disabling APT authentication.

Minimal command-line core and backgrounds:

```sh
sudo sh daylight-install.sh --core --yes
daylight status
daylight info
daylight doctor
```

Full optional desktop:

```sh
sudo sh daylight-install.sh --desktop --yes
```

Add `--games` only with `--desktop`. Use `--repo-only --yes` to configure the repository without installing Daylight packages. Telemetry is never installed or activated by this bootstrap. It does not perform a global package upgrade or reboot.

The bootstrap saves any existing managed repository configuration under `/var/backups/daylight-apt.*` and restores those files if installation fails. This is a configuration rollback, not a rollback of every dependency operation. Unmanaged files and symlink configuration targets are not overwritten. Keep an appropriate system backup, especially on a productive server.

## Graphical session

Desktop installation does not install/start a new display manager or change the default boot target. Choose **Daylight GNU/Linux** at the next login in your existing graphical login manager. On an appropriate local console, `startx /usr/bin/daylight-session` is an alternative. Do not run the desktop as root or replace a productive server's active session remotely.

Fastfetch and Terminology are optional; the fallbacks are the built-in ASCII information display and Xterm. Never mix Debian 13 system repositories into Debian 12 just to obtain Fastfetch. Daylight settings live in `${XDG_CONFIG_HOME:-$HOME/.config}/daylight`. Existing shell, Conky and classic Fluxbox files are not replaced. Fluxbox can create missing compatibility files under `~/.fluxbox`.

## Updates

```sh
daylight update --dry-run
sudo daylight update
```

Only installed Daylight packages are requested for upgrade. APT can propose dependency changes: inspect its confirmation. An index-refresh error aborts the upgrade. No distribution upgrade or autoremove is performed.

## Removal

Log out of the Daylight graphical session before removing desktop packages.

```sh
daylight remove --dry-run
sudo daylight remove
```

The command targets installed Daylight packages, without autoremove. APT may propose removal of other software that explicitly depends on them; inspect its confirmation. Shared dependencies, personal settings and the repository configuration are retained. This is deliberately not presented as a bit-for-bit restoration or a filesystem snapshot.

## Offline release files

Download the architecture-appropriate `.deb` files and SHA256SUMS from the official GitHub release. Install exactly one core architecture with its architecture-independent companion packages using `sudo apt install ./<filename>.deb`. Public filenames replace the Debian version's `~` with `.`, while the internal package version retains `~` and correct Debian release-candidate ordering.

`sha256sum -c SHA256SUMS` checks a complete downloaded set. For a partial set, verify its corresponding lines and distinguish missing files from mismatches. A checksum from the same source is not an independent publisher signature; the public APT repository provides signed metadata.

## Live session and privacy

The live image uses temporary storage, has no disk installer or persistence by default, and does not activate SSH or telemetry. Do not mount or modify internal disks while exploring. Read the version-specific validation record for actual BIOS/UEFI/browser evidence; virtual-machine tests do not certify Secure Boot, physical Wi-Fi/audio or all Raspberry Pi graphics hardware.

The optional collector remains a separate deployment. No activation or mail delivery is inferred merely from an email address or a configuration file being present. See `PRIVACY.md`, `VALIDATION.md` and `VALIDATION-RC2.md`.
