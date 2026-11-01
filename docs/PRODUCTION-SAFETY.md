# Production Raspberry Pi precautions

The original machine hosts production applications. Daylight development must not restart or reconfigure Apache, Docker, Nextcloud, Cloudflare Tunnel, WireGuard, networking or SSH. No reboot, general OS upgrade, automatic dependency cleanup, display-manager replacement or boot-target switch is part of this package's installation.

Compile on the development PC. First inspect the package contents and APT simulation. Core and themes contain no service start/stop scripts and have no graphical dependency. Installing a complete desktop still requires reviewing APT's dependency plan.

Record service PIDs, container start times and configuration checksums before and after authorized host operations; keep these records outside the public repository. Existing backups must be preserved. Current remote-tool restrictions on privileged commands must not be bypassed.

The package-lifecycle test is for a disposable container only, with CPU, memory and process limits, no host networking, no privileged mode and no production data mounts. It must never run directly on the production host.

Daylight registers an additional session and isolates settings under ~/.config/daylight. It does not overwrite ~/.fluxbox, ~/.conkyrc or existing shell rcfiles. Removal targets only Daylight packages, never runs autoremove and deliberately preserves user Daylight settings and pre-existing dependencies.

A successful headless Xvfb test is not proof of a physically tested desktop. Resource limits and backups reduce risk; they are not an availability guarantee.
