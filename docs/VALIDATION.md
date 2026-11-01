# Validation record — 5.0.0-rc.1

## Complete candidate validation

**All build and validation steps passed** in GitHub Actions run **41357700732**, workflow **Daylight candidate validation**, on **2026-11-01**.

Exact tested source commit: `85715705501b18138712173327b7df1fb63ef889`.

Evidence artifacts: `daylight-validation-9` and `daylight-candidate-9`. The publishing workflow retrieves these already-tested files without rebuilding them. Release publication is a separate checked step; consult the release page for availability.

## Rust, CLI and repository checks

- Formatting and strict Clippy (`-D warnings`) passed.
- **27 Rust unit tests** passed.
- **11 CLI integration tests** passed, covering invalid inputs, isolated settings, JSON output, CPU sampling, password lengths and disabled telemetry.
- **4 collector tests** passed, including daily aggregation and rejection of extra identifying fields.
- **1 signed APT repository test** passed: both architecture indexes, package SHA256 hashes, InRelease verification and rejection of tampered metadata. Its key and repository were generated in a disposable temporary directory; no existing signing key was used.
- Static AMD64 and ARM64 executables compiled and their ELF architectures were checked.
- Seven package types were built, with two core architectures: **eight .deb files** total.

## Debian 12 and Debian 13 desktop lifecycle

The full package lifecycle passed on both **Bookworm and Trixie** in disposable GitHub-hosted containers during the complete validation run above.

- Installation of all seven package types and validation of desktop launchers.
- All 11 installed CLI integration tests passed in each environment.
- A real Xvfb display with Fluxbox, Daylight's configuration and Conky started successfully.
- The Daylight terminal opened; the Trixie Fastfetch configuration also ran successfully.
- **16 native application GUI tests passed on each Debian release**, exercising input dialogs, result windows, game cancellation and the completed alarm. No generated password text was captured or logged.
- Same-version core reinstallation succeeded.
- APT removal simulation and actual removal succeeded without autoremove.
- The base OS identity and existing shell, Conky and wallpaper files remained byte-identical.
- A second test user with existing classic Fluxbox files retained those files byte-for-byte after a Daylight session and removal.

These are graphical integration tests, not a physical monitor/input/audio test. Earlier first-run Fluxbox configuration and wallpaper ordering defects were corrected and re-tested. Fluxbox may create missing compatibility files under `~/.fluxbox`; Daylight's active settings are separate.

## Debian 13 AMD64 live ISO

The image was built successfully from the same candidate packages. The complete workflow then booted its live filesystem offline under **QEMU TCG**, with no host disks attached.

The guest created its `daylight` user, started Fluxbox and Conky, and emitted **DAYLIGHT_LIVE_READY**. The retained result file reports PASS. The final desktop screenshot was inspected and shows the Daylight mountain/sun background, custom toolbar and system monitor.

The test uses the ISO's extracted kernel and initrd. It **does not certify BIOS/UEFI bootloaders, Secure Boot, physical hardware, Wi-Fi or audio**. The graphic assets remain prototypes; the large wallpaper's wordmark can be cropped by cover scaling at some aspect ratios.

During earlier validation, APT correctly rejected a transient mirror hash mismatch; verification was not weakened. A separate diagnostic of an earlier ISO found that disabling recommended packages omitted `user-setup`, preventing live user creation. That dependency is now explicit and the complete corrected image passed the run cited above.

## Real Raspberry Pi 4

The ARM64 core .deb was extracted in a dedicated unprivileged workbench, **not installed into the host package database**. The extracted executable ran natively on Debian 12 and read the Pi model, memory, temperature and active interface.

The native check used the same Rust application sources as the final candidate; later changes concerned desktop integration, build/test helpers and the live recipe.

- All 11 CLI tests and 4 temporary loopback collector tests passed.
- Apache, cloudflared, Docker and WireGuard were active before and after, with identical main PID values.
- Nextcloud's local status response remained unchanged.
- No reboot, display-manager change, production container restart, global package upgrade or desktop installation occurred.

## Additional local checks

Two consecutive package constructions with identical inputs on the development PC produced identical SHA256 hashes for all seven AMD64/data package outputs. This is a same-host check, **not proof of cross-host reproducibility**.

Two hundred calendar date differences agreed with Python datetime. Thirty generated passwords satisfied their requested length and printable-character constraints; their values were not logged. These checks are **not a cryptographic audit**.

## Release gates and remaining scope

Publication requires a successful complete validation of the exact tagged source commit, both package lifecycle markers, a successful live result and matching uploaded asset names/sizes. The published candidate includes inspectable logs, screenshots and exact live package provenance.

Public signed APT hosting, production telemetry collection, delivery to `contact@daylightlinux.ch`, 32-bit ARM compatibility, final photorealistic artwork and physical desktop/hardware certification remain separate tasks. No public endpoint or mailbox is declared operational merely because configuration exists in the repository. The version remains a **release candidate**, not a stable production release.
