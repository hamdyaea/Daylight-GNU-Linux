# Sources and component provenance

Daylight's original code is distributed under GNU GPL v3. The release tag identifies the exact reviewed source commit for the Daylight binaries. Build scripts, package definitions, Cargo.lock and the pinned toolchain are in that tree.

A complete candidate publication includes `daylight-validation.zip`. In addition to tests and screenshots, its package manifest is extracted from the tested ISO's actual dpkg database, not inferred from a requested package list:

- `daylight-live-packages.json`: installed binary packages, exact versions, architectures and source package references.
- `daylight-live-sources.tsv`: the same inventory in a simple tab-separated form.
- `verified-run.json`: the source commit and validation run used for publication.

The manifest's Debian source archive links are generated from installed metadata; the extraction script does not download or independently validate every remote source reference. Keep the inventory when reproducing or auditing a release. Use the source package name and source version, which may differ from the binary package name/version, when retrieving Debian sources.

The live image also includes unmodified Debian components, including explicitly selected firmware. Their own licenses and copyright notices remain applicable; **GPLv3 is not a blanket relicensing of every file in the ISO**. Third-party notices remain under `/usr/share/doc/` in the image.

The Daylight executable statically links the Rust standard library and musl. Their licenses are retained in `licenses/` and installed with `daylight-core`; see `THIRD_PARTY.md`. Static linking means rebuilding is necessary to incorporate future fixes to those runtime components.

The release uses the already-validated artifacts. Package provenance and test evidence are collected without executing or modifying the ISO filesystem. This manifest is a maintenance inventory, not a claim of vulnerability-free components or a complete security audit.
