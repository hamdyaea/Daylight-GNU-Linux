# Third-party software and licenses

Daylight source code is GPL-3.0-only. Founder and developer: Hamdy Abou El Anein. Contact: info@daylightlinux.ch (activation pending).

The Rust executables statically link the Rust standard library and the musl runtime. Those components retain their MIT, Apache-2.0 and other applicable notices. The `licenses/` directory accompanies the core package. Toolchain 1.88.0 is pinned for builds; this is not a claim it is the latest toolchain. The maintainer must rebuild the executable when bundled runtime security updates are relevant.

Fluxbox, Conky, YAD, Fastfetch, Terminology and other Debian dependencies retain their original authors and licenses. They are installed using the system package manager rather than attributed to Daylight's developer. Font files are provided by system packages, not included as project assets.

The historical Daylight background is recovered from this repository. The new SVGs are simplified working designs following the mountain/sun direction selected for the project; they are not finalized photorealistic artwork.

A live image includes other Debian packages and may include non-free firmware. Daylight's GPLv3 does not replace those package licenses. Consult the image's /usr/share/doc/*/copyright files.

Source releases must include the complete Daylight sources and build scripts. Binary release artifacts must preserve all linked-runtime notices; their inclusion is part of the release validation.
