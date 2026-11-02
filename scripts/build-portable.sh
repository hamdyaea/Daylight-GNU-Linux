#!/bin/sh
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$root"
python3 scripts/collect-notices.py
rustup target add --toolchain 1.88.0 x86_64-unknown-linux-musl aarch64-unknown-linux-musl
host=$(rustup run 1.88.0 rustc -vV | sed -n 's/^host: //p')
lld="$(rustup run 1.88.0 rustc --print sysroot)/lib/rustlib/$host/bin/rust-lld"
export CARGO_TARGET_X86_64_UNKNOWN_LINUX_MUSL_LINKER="$lld"
export CARGO_TARGET_AARCH64_UNKNOWN_LINUX_MUSL_LINKER="$lld"
cargo +1.88.0 build --locked --release --target x86_64-unknown-linux-musl
cargo +1.88.0 build --locked --release --target aarch64-unknown-linux-musl
python3 scripts/build-debs.py --arch amd64
python3 scripts/build-debs.py --arch arm64
cd dist
sha256sum ./*.deb > SHA256SUMS
