# Validation record — 5.0.0-rc.1

## Performed on the development PC

- Rust formatting and strict Clippy lint (`-D warnings`) passed.
- 27 Rust unit tests passed.
- 11 CLI integration tests passed, including invalid-input handling, isolated settings, JSON output, CPU sampling, password lengths and disabled telemetry.
- 4 collector integration tests passed, including daily aggregation and rejection of extra identifying fields.
- Static AMD64 and ARM64 executables compiled; actual ELF architectures verified.
- Seven package types were built; the core has separate AMD64/ARM64 builds. SHA256SUMS were generated.

## Performed on the real Raspberry Pi 4

The ARM64 core .deb was extracted under a dedicated, unprivileged workbench; it was **not installed into the host package database**. The extracted executable ran on Debian 12 Bookworm and correctly read the Pi model, memory, temperature and active interface.

- 11 CLI integration tests passed on the Pi.
- 4 collector tests passed using a temporary loopback-only test server and temporary database.
- Apache, cloudflared, Docker and WireGuard remained active. Their main PID values matched before and after the test.
- No reboot, display-manager change, production container restart or global package upgrade was performed.

## Not established by those tests

Full APT installation/removal, a physical graphical session, a booted live ISO, UEFI/Secure Boot, production telemetry infrastructure, public signed APT hosting and receipt of mail at the proposed contact address are separate validation gates. Remote privileged operations were blocked by the tool's safety restrictions and were not forced.

The presence of build scripts is not evidence that an ISO or deployment exists. The RC designation remains until relevant release gates are satisfied. New artwork is a working design, not a finalized photorealistic wallpaper set.
