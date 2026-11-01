# Build and validation

## Rust and Debian packages

Prerequisites: Rust/rustup, Python 3, Git, dpkg-deb and ImageMagick.

```sh
rustup toolchain install 1.88.0 --profile minimal --component rustfmt --component clippy
cargo +1.88.0 fmt --check
cargo +1.88.0 clippy --all-targets -- -D warnings
cargo +1.88.0 test --locked
./scripts/render-assets.sh
./scripts/build-portable.sh
python3 tests/test_integration.py
python3 tests/test_collector.py
```

The Rust application has no Cargo dependencies. The standard library and musl runtime are statically linked, so their notices and security updates must be maintained. The pinned 1.88.0 toolchain is a build choice, not a claim to be the latest release. Both executable architectures are checked during packaging. Only architecture-independent data/integration packages use Architecture: all.

Rust version `5.0.0-rc.1` corresponds to Debian version `5.0.0~rc1`. SOURCE_DATE_EPOCH defaults to the source commit time. Artifacts and SHA256SUMS are in `dist/`.

## Package lifecycle testing

`scripts/test-packages.sh` is exclusively for a disposable Debian container. It requires `DAYLIGHT_DISPOSABLE_TEST=yes`, installs test dependencies inside that container, verifies a Fluxbox/Conky session under Xvfb, opens native dialogs, reinstalls and removes Daylight, and checks that existing user files and OS identity remain unchanged. It must never run on a production host. Resource limits and no production data mounts are required when sharing a host.

## Live ISO

`live/` contains a Debian 13 Trixie AMD64 live-build recipe. Build only in a disposable Debian build VM/container with live-build, debootstrap, squashfs-tools, xorriso and BIOS/UEFI bootloader tools. `scripts/build-live.sh` assembles the ISO from the AMD64 and architecture-independent .deb files in dist; it does not copy a personal system.

The live edition is temporary, has no installer or persistence by default and does not enable SSH or telemetry. Standard Debian Live local-session conventions apply. It is not a hardened kiosk. Physical hardware, UEFI/Secure Boot and live-session behavior must be validated before claiming a stable release.

## Development paths

The isolated development checkout is separate from the original historical checkout. Keep private infrastructure inventory and test logs outside the public source tree. Read `VALIDATION.md` for performed tests rather than treating a script's presence as proof it was executed.
