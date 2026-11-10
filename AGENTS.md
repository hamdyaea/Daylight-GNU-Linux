# Daylight GNU/Linux maintainer rules

## Release and mirrors (mandatory for every change, including future chats)

Whenever changing a Daylight version, .deb package, APT repository, or release, ensure that the official signed APT repository and GitHub release assets remain in sync, and **also synchronize the free SourceForge mirror** at https://sourceforge.net/projects/daylight-linux/files/Daylight-GNU-Linux-5/.

On the authorized Manjaro maintainer machine, run `~/.local/bin/daylight-sync-sourceforge` and verify its checksum comparison before reporting a release complete. A daily systemd user timer `daylight-sourceforge-sync.timer` is an additional fallback, not a substitute for verifying each release. Do not publish unvalidated packages, do not overwrite older release files, and never claim SourceForge is updated without checking the transfer result.

When changing mirror registration or APT distribution, keep `docs/community-mirrors.md`, `website-src/mirrors.html`, and the public mirror health service consistent. Do not enable telemetry by default.
