# Final independent verification — 2 November 2026

Developer: Hamdy Abou El Anein — info@daylightlinux.ch.

This supplements `DEPLOYMENT-2026-11-02.md`; it does not change software versions or certify untested hardware.

## Published source and website

The Raspberry Pi-first source tree `54dc561f7cc56f1a51f4be1b89aacd35c97691a2` is published on master and matches the locally reviewed website sources. There are 16 pages per language (English/French), a complete native mobile menu, a Raspberry Pi installation pathway and an explicitly secondary AMD64 PC live demonstration. Books and historical versions remain accessible.

A final origin audit verified all 66 files listed in the deployment manifest against their reviewed SHA256 hashes. The public HTTPS homepage, Raspberry Pi/download pages, books link, archive and APT indexes were also checked. The original website is preserved under `/old/site/`.

The unchanged real-browser test suite passed against **https://daylightlinux.ch**: 128 page/width combinations at 320, 390, 768 and 1440 pixels, plus four checks with JavaScript disabled. It checked complete navigation, keyboard Escape/focus, images, horizontal overflow and JavaScript/CSP errors. An earlier attempt encountered `ERR_INTERNET_DISCONNECTED`; a complete rerun succeeded rather than treating that failure as a pass.

## Independent disposable-runner verification

GitHub Actions run **41432564540** completed successfully with three jobs:

- `website`: verified the exact published source tree, rebuilt assets and pages, passed structure/link and installer/site regression checks, and passed the browser suite.
- `public-installer (bookworm)`: installed RC2 through the actual public HTTPS bootstrap and signed APT archive, repeated repository configuration, simulated updates/removal and completed actual removal without autoremove.
- `public-installer (trixie)`: completed the same public RC2 lifecycle checks.

The installer jobs required both `DAYLIGHT_PUBLIC_INSTALLER_LIFECYCLE_OK` and the actual `Daylight GNU/Linux 5.0.0-rc.2` version output. Tests ran in disposable containers, not on the production Pi.

Retained artifacts and SHA256:

- `daylight-final-website-3`: `c7e301fc0cd2e0de1ee1a1bb19ca60fb39ba85e736c9efbe0fb6038181694540`.
- `daylight-final-client-bookworm-3`: `128c1e8d6466e24da5283fa14c2ad987667692ba74c0e1917753a3034d02dbee`.
- `daylight-final-client-trixie-3`: `37a63b60dac533d3b50ecd802792666b50aa614856d5485f835b624417c2b8a3`.

## Archive and native Pi checks

Each public architecture index contains seven RC2 package types and preserves the RC1 records. The existing restricted metadata-signing service completed successfully and its daily timer is active. The full archive key fingerprint remains `B0575F821A31DD20753DE07C50D21240F4BCB02E`.

On the Pi, the installed core and themes report Debian package version `5.0.0~rc2`; the CLI reports `5.0.0-rc.2`. A scoped APT refresh and upgrade simulation reported no further changes required. All 11 integration tests against the installed native executable passed as the normal user. Installed-file verification passed and telemetry remained disabled, with no collector endpoint configured. No desktop package was installed.

A final comparison with the private pre-deployment snapshot found identical Apache/cloudflared/Docker/WireGuard active states and main PIDs, identical Nextcloud status, and unchanged hashes of OS identity, SSH configuration and the Daylight Apache virtual host. No production reboot, network change or container restart was performed.

## Boundaries

The delivered software remains a release candidate. These checks do not certify physical iPhone/Safari behavior, all Raspberry Pi graphics/input configurations, physical PC Wi-Fi/audio, Secure Boot or ARM32. Browser demos do not run public guest VMs on the production Pi. DistroSea acceptance, Wikipedia publication and mailbox delivery are not asserted. The optional telemetry collector is not activated by this deployment.
