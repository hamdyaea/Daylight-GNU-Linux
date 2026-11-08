# Daylight GNU/Linux 5.0.0-rc.3 package update

This is a package-only release candidate for Debian 12/13 and Raspberry Pi OS 64-bit. It publishes updated APT packages for AMD64 and ARM64. The previously validated `5.0.0-rc.2` live ISO is unchanged.

## Changes

- Adds the opt-in boot telemetry endpoint configuration to the optional telemetry package.
- Keeps telemetry disabled by default. No request is sent unless the administrator installs the optional package and explicitly enables telemetry.
- Accepts telemetry responses only when the collector returns HTTP 204; login redirects and other failures are not reported as successful delivery.
- Documents the endpoint data and Cloudflare transport metadata in the privacy page.
- No kernel, base distribution, existing desktop configuration, or display manager changes.

## Versioning

Debian package version: `5.0.0~rc3`. The package set uses matching exact-version dependencies. The previous `5.0.0~rc2` package files remain immutable in the archive.

## Validation

- Rust unit tests: 27 passed; formatting and Clippy passed with warnings denied.
- Collector tests: 5 passed, including health, aggregate-only storage and identifier rejection.
- Signed APT metadata and tamper-detection test passed.
- The RC3 CLI integration suite passed all 11 checks on AMD64 and on the Raspberry Pi 4 ARM64 executable, run from `/tmp` without installing it.
- Both package architectures and all eight package records were inspected. The optional telemetry package retains `enabled=no`.
- The full Debian package lifecycle GUI suite was not run for this package-only candidate. The previously published RC2 lifecycle checks remain documented separately and do not count as RC3 validation.

The production Raspberry Pi APT check is limited to metadata and a dry-run against already installed Daylight packages; it does not install the update or enable telemetry.