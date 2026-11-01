# Build and validation

## Rust and Debian packages

Prerequisites: Rust/rustup, Python 3, Git, dpkg-deb, ImageMagick, an SVG renderer and DejaVu fonts. On a disposable Debian/Ubuntu build machine the relevant packages include `dpkg-dev imagemagick librsvg2-bin fonts-dejavu-core python3 curl gnupg`. Do not run build dependency installation on a productive server.

```sh
rustup toolchain install 1.88.0 --profile minimal --component rustfmt --component clippy
cargo +1.88.0 fmt --check
cargo +1.88.0 clippy --locked --all-targets -- -D warnings
cargo +1.88.0 test --locked
sh scripts/render-assets.sh
sh scripts/build-portable.sh
python3 tests/test_integration.py
python3 tests/test_collector.py
python3 tests/test_repository.py
```

The Rust application has no Cargo dependencies. Its standard library and musl runtime are statically linked, so their notices and security updates must be maintained. The pinned 1.88.0 toolchain is a build choice, not a claim to be the latest release. Both executable architectures are checked during packaging. Only architecture-independent data/integration packages use Architecture: all.

Rust version `5.0.0-rc.1` corresponds to Debian version `5.0.0~rc1`. SOURCE_DATE_EPOCH defaults to the source commit time. Artifacts and SHA256SUMS are in `dist/`. Reproducible inputs are an aim, not a claim of verified bit-for-bit reproducibility across different toolchains or hosts.

The repository test generates a temporary test signing key, verifies both architecture indexes and package hashes, verifies InRelease, then confirms that tampering is rejected. It never uses an existing private key and does not modify APT configuration.

## Package lifecycle testing

`scripts/test-packages.sh` is exclusively for a disposable Debian container. It requires `DAYLIGHT_DISPOSABLE_TEST=yes`, installs its own test dependencies, starts a Fluxbox/Conky session under Xvfb, exercises native dialogs, reinstalls and removes Daylight, and checks that existing user files and OS identity remain unchanged. Never run it on a production host. Use resource limits and no production data mounts when sharing a host.

GUI tests inspect window names and process arguments to verify state transitions. They do not record generated passwords. The alarm check waits for the completion dialog rather than relying on a fixed VM scheduling delay.

## Live ISO

`live/` contains a Debian 13 Trixie AMD64 live-build recipe. Build only in a disposable Debian VM/container with live-build, debootstrap, squashfs-tools, xorriso and BIOS/UEFI bootloader tools. `scripts/build-live.sh` assembles an ISO from the AMD64 and architecture-independent .deb files in dist; it never clones a personal system.

The live edition is temporary, has no installer or persistence, and does not enable SSH or telemetry. It is not a hardened kiosk. `scripts/test-live.py` boots the ISO filesystem offline in QEMU with the extracted kernel/initrd, no host disks and no network. That test does not certify BIOS/UEFI bootloaders, Secure Boot or physical hardware.

A transient mirror error must not be worked around by disabling APT signatures or checksums. The workflow uses bounded retrieval retries and only cleans index files in newly created disposable build containers.

## Release publication

The release workflow accepts only an exact source commit whose full validation workflow completed successfully. It publishes the tested artifacts without rebuilding them and includes their logs and screenshots. Failed builds retain evidence, but are not accepted by the release gate. No production machine credentials are used by these workflows.

## Development paths

The clean release worktree is separate from the earlier development checkout, which is preserved. Private infrastructure inventory stays outside the public source tree. Read `VALIDATION.md` and the actual release evidence rather than treating a script's presence as proof it was executed.
