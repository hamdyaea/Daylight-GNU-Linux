# Validation record — 5.0.0-rc.1

## Rust, CLI and repository checks

- Formatting and strict Clippy (`-D warnings`) passed.
- **27 Rust unit tests** passed.
- **11 CLI integration tests** passed, covering invalid inputs, isolated settings, JSON output, CPU sampling, password lengths and disabled telemetry.
- **4 collector tests** passed, including daily aggregation and rejection of extra identifying fields.
- **1 signed APT repository test** passed on the development PC: both architecture indexes, package SHA256 hashes, InRelease signature verification and rejection of tampered metadata. Its key and repository were generated in a disposable temporary directory; no existing signing key was used.
- Static AMD64 and ARM64 executables compiled and their ELF architectures were checked.
- Seven package types were built, with two core architectures: **eight .deb files** total.

## Debian 12 and Debian 13 desktop lifecycle

The full package lifecycle passed on both **Bookworm and Trixie** in disposable GitHub-hosted containers, using source commit `48f8565857c9612cec01d15aa4e5e04f0c37a701` in validation run `41353568850`.

- Installation of all seven package types and validation of desktop launchers.
- All 11 installed CLI integration tests passed in each environment.
- A real Xvfb display with Fluxbox, the Daylight configuration and Conky started successfully.
- The Daylight terminal opened; the Trixie Fastfetch configuration also ran successfully.
- **16 native application GUI tests passed on each Debian release**, exercising input dialogs, result windows, game cancellation and the completed alarm. No generated password text was captured or logged.
- Same-version core reinstallation succeeded.
- APT removal simulation and actual removal succeeded without autoremove.
- The base OS identity and existing shell, Conky and wallpaper files remained byte-identical.
- A second test user with existing classic Fluxbox files retained those files byte-for-byte after a Daylight session and removal.

These are graphical integration tests, not a physical monitor/input/audio test. The first-run Fluxbox configuration overwrite found during validation was fixed before this successful run. Fluxbox may still create missing compatibility files under `~/.fluxbox`; Daylight's active settings are separate.

The same run did **not** complete ISO construction because the Debian mirror supplied an index that failed APT's hash check. Verification was not weakened. Later complete validation runs and their artifacts are the authority for ISO results.

## Real Raspberry Pi 4

The ARM64 core .deb was extracted in a dedicated unprivileged workbench, **not installed into the host package database**. The extracted executable ran natively on Debian 12 and read the Pi model, memory, temperature and active interface.

The latest native check used the same application sources as commit `48f8565857c9612cec01d15aa4e5e04f0c37a701`:

- All 11 CLI tests and 4 temporary loopback collector tests passed.
- Apache, cloudflared, Docker and WireGuard were active before and after, with identical main PID values.
- Nextcloud's local status response remained unchanged.
- No reboot, display-manager change, production container restart, global package upgrade or desktop installation occurred.

## Release gates and limitations

The release publishing workflow requires a successful complete validation of the exact tagged source commit. It retrieves the already-tested packages and ISO rather than rebuilding them. The release evidence archive must include successful lifecycle markers for both Debian versions and a successful live-filesystem smoke test.

The QEMU test boots the ISO's live filesystem using its extracted kernel/initrd, offline and with no host disks attached. This does **not** certify the ISO's BIOS/UEFI bootloaders, Secure Boot, physical PC hardware, Wi-Fi, audio or a real Pi graphical session.

Public signed APT hosting, production telemetry collection, delivery to `contact@daylightlinux.ch`, 32-bit ARM compatibility and final photorealistic artwork remain separate tasks. No public endpoint or mailbox is declared operational merely because configuration exists in the repository. The version remains a release candidate, not a stable production release.
