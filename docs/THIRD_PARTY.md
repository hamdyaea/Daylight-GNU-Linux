# Third-party software and licenses

Daylight source code is GPL-3.0-only. Founder and developer: Hamdy Abou El Anein. Contact: info@daylightlinux.ch.

The Rust executables statically link the Rust standard library and the musl runtime. Those components retain their MIT, Apache-2.0 and other applicable notices. The `licenses/` directory accompanies the core package. Toolchain 1.88.0 is pinned for builds; this is not a claim it is the latest toolchain. The maintainer must rebuild the executable when bundled runtime security updates are relevant.

Fluxbox, Conky, Python, Tcl/Tk, Fastfetch, Terminology and other Debian dependencies retain their original authors and licenses. They are installed using the system package manager rather than attributed to Daylight's developer. Font files are provided by system packages, not included as project assets.

The historical Daylight background is recovered from this repository. The approved
Alpine-lake artwork and its derivatives retain the provenance and native dimensions
recorded in `assets/generated-art.json`. The two CC0 photographs retain their
original authors, licenses and source hashes in `assets/photography.json` and the
wallpaper package's `CREDITS.txt`. System font files are not redistributed.

## Shardturn

The optional `daylight-games` package includes Shardturn's original standalone
Python source and vector identity, copyright (C) 2026 Hamdy Abou El Anein, under
**GPL-3.0-or-later**. This permission is retained rather than replaced by Daylight's
GPL-3.0-only designation. Its upstream repository is
<https://github.com/hamdyaea/Shardturn>, pinned to commit
`658a57e7c7e9e1743d99a8c6a59b68c03b8f7963`.

The vendored `desktop/shardturn/SOURCE.json` lists the exact original files and
SHA-256 hashes. The package installs their source, `LICENSE`, `README.md`,
`VISUAL_IDENTITY.md` and `SOURCE.json` under `/usr/share/daylight/shardturn/`.
Its icon is the unchanged original vector asset. Shardturn draws its cards locally
with Tkinter and does not download artwork or include third-party commercial
card-game logos.

A live image includes other Debian packages and may include non-free firmware. Daylight's GPLv3 does not replace those package licenses. Consult the image's /usr/share/doc/*/copyright files.

Source releases must include the complete Daylight sources and build scripts. Binary release artifacts must preserve all linked-runtime notices; their inclusion is part of the release validation.
