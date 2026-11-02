# Security reports

Project maintainer: Hamdy Abou El Anein.

Please do not publish credentials, exploit details exposing a third party, or private infrastructure logs in a public issue. Contact info@daylightlinux.ch with a minimal description and safe reproduction outline. If delivery fails, open a public issue requesting a private contact route without including sensitive details. No response-time guarantee is stated.

The 5.0.0-rc series is a release candidate. Review the version-specific validation record before production use. Preserve APT signature and checksum verification; do not use trusted=yes or allow-unauthenticated as a workaround.

The optional boot counter is off by default. Browser demos must remain isolated and must not expose host disks, repository credentials or production network access. Do not turn the production Raspberry Pi into a public multi-user VM service.
