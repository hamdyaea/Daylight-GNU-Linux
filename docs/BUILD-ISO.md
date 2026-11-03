# Build the Daylight GNU/Linux live ISO from source

Developer: Hamdy Abou El Anein
Contact: info@daylightlinux.ch
License: GPL-3.0-only

This is the source recipe for the **current Daylight GNU/Linux 5.0.0-rc2
Debian 13 (Trixie), amd64 live image**. It is not a claim that the
historical images released in 2019 can be rebuilt bit-for-bit.

The relevant source files are:

- [live/auto/config](../live/auto/config) and
  [live/config/package-lists/daylight.list.chroot](../live/config/package-lists/daylight.list.chroot):
  Debian live-build configuration and installed package list.
- [scripts/build-portable.sh](../scripts/build-portable.sh):
  compile the Daylight Rust application and create Debian packages.
- [scripts/build-live.sh](../scripts/build-live.sh):
  assemble the live ISO from the packages and live-build configuration.
- [scripts/configure-boot-menu.py](../scripts/configure-boot-menu.py):
  configure the boot menus.
- [docs/BUILD.md](BUILD.md): build tools, validation and package information.

## Use a disposable Debian 13 amd64 build machine

**Do not run the live ISO build as root on the website host, a production
Raspberry Pi or a personal workstation with valuable data.** Use an
isolated, disposable Debian 13 VM, with internet access, enough disk space
and no host disks mounted for writing. The live-build process downloads
Debian packages and requires root privileges inside the VM.

On the disposable Debian VM install the build tools:

```sh
sudo apt update
sudo apt install -y git curl ca-certificates python3 dpkg-dev \
    imagemagick librsvg2-bin fonts-dejavu-core \
    live-build debootstrap squashfs-tools xorriso \
    isolinux syslinux-common grub-pc-bin grub-efi-amd64-bin
```

Install [Rust/rustup](https://rustup.rs/) according to its official
instructions for the build user, then use the pinned project toolchain:

```sh
rustup toolchain install 1.88.0 --profile minimal
git clone https://github.com/hamdyaea/Daylight-GNU-Linux.git
cd Daylight-GNU-Linux
sh scripts/render-assets.sh
sh scripts/build-portable.sh
sudo sh scripts/build-live.sh
```

The **package build runs as the regular build user**; only the final
live-build assembly runs as root in the disposable VM.

If the build succeeds, the expected output is:

```text
dist/daylight-live_5.0.0-rc.2_amd64.iso
dist/daylight-live_5.0.0-rc.2_amd64.iso.sha256
```

Verify the checksum from the project root:

```sh
cd dist
sha256sum -c daylight-live_5.0.0-rc.2_amd64.iso.sha256
```

## Customise the image

Modify the Debian package list in
`live/config/package-lists/daylight.list.chroot`, the settings in
`live/auto/config`, the branded assets in `assets/`, or Daylight
application sources in `src/`. Rebuild the packages and ISO after
modifying source files. Read the live-build manual to understand which
changes require an additional `live/config/` hook or filesystem
configuration.

The default live edition has **no disk installer or persistence** and
disables SSH and telemetry. The automated test in
`scripts/test-live.py` checks a QEMU boot of the live filesystem;
it does not certify BIOS/UEFI boot, Secure Boot or real hardware. See
[validation notes](VALIDATION.md) for tested scope and limitations.

To request support or report recipe problems, open a GitHub issue with
the commit SHA, build-host OS, command and error message (without secrets).
