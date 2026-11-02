# RC2 validation record

This branch adds photographic wallpapers, scoped signed APT installation, atomic repository hosting with automated signature renewal, a bilingual static website, and a private QEMU/noVNC browser demo.

The candidate workflow is being extended to validate the exact committed sources, native dialogs, package lifecycle on Debian 12 and Debian 13, the live filesystem, real BIOS and UEFI ISO bootloaders and a real Chromium/noVNC connection.

**Do not interpret the existence of these scripts as proof that these gates have passed or that production endpoints are deployed.** The completed run, retained artifacts and deployment checks must be recorded here before final publication.

The previous immutable RC1 evidence remains in `VALIDATION.md`. Physical hardware, Wi-Fi, audio and Secure Boot are separate from the offline BIOS/UEFI tests. The browser demo is a private disposable environment, not a publicly exposed multi-tenant service.
