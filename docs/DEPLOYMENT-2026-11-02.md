# Verified deployment — 2 November 2026

Developer and founder: **Hamdy Abou El Anein**. Project contact: **info@daylightlinux.ch**.

## Published website and source

The Raspberry Pi-first website is deployed at **https://daylightlinux.ch/**, with French pages at **https://daylightlinux.ch/fr/**. The primary pathway is Raspberry Pi OS ARM64 installation. The AMD64 PC ISO is explicitly presented as a live environment for discovering and testing the desktop, not a Raspberry Pi boot image.

There are **16 pages in each of English and French, 32 total**, including a complete native HTML menu, Raspberry Pi guide, installation, downloads, discovery, actual screenshots, browser demo, wallpapers, news, FAQ, community, project information, books, media kit, Old and privacy. Native menu navigation works without JavaScript. CSS/JS filenames contain content hashes to avoid stale mobile assets. The author/books page uses the supplied Amazon author-store URL. The historical site remains under `/old/site/`.

The published website source tree is `54dc561f7cc56f1a51f4be1b89aacd35c97691a2`, published on master in commit `2de81327cc76a889f693997358a7952d32af4822`. It matches the previously reviewed local commit `06bf5a6ed2ab44cda729bfce4a3eec0bf6ce8d21` byte-for-byte at the Git tree level. The local GitHub credential was not needed for publication: workflow definitions were changed through the authorised repository integration, and the workflow token then published only non-workflow content by an ordinary fast-forward. No history was force-rewritten.

The public source snapshot is `/media/daylight-source-06bf5a6ed2ab.zip`, SHA256 `356f7501d5e0486891ace01af18d9c14f91fdbba762770a9ed93fa451925bb06`. It contains committed project files only, not credentials, signing keys, host data or workbench output.

### Website validation

- All **66 files in the generated deployment manifest** matched their hashes on the web host after deployment.
- Static checks covered 32 pages and **1,566 local links**, canonical/language links, sitemap, page metadata, exact CSP hashes and a media archive without font files.
- **128 real Chromium page/width combinations** passed against the actual public HTTPS website at 320, 390, 768 and 1440 pixels, plus **four no-JavaScript navigation checks**. The checks cover menu completeness, keyboard Escape/focus, horizontal overflow, broken images and JavaScript/CSP errors.
- The dedicated website workflow completed successfully: GitHub Actions run **41431798847**.
- This does not certify physical iPhone/Safari rendering or constitute a complete manual accessibility review.

The website remains static. No new web analytics, tracking SDK, persistent application server or public guest VM was added to the production Raspberry Pi. Sharing is visitor-initiated; RSS is a static feed.

## Public APT archive aligned to RC2

**https://daylightlinux.ch/apt/** now publishes the eight immutable package files from the already-tested **v5.0.0-rc.2** release. Each was verified against its published SHA256, size, internal Debian version and maintainer before import. The release packages were not rebuilt during deployment.

- Current candidate package version: **5.0.0~rc2**.
- Architectures: **arm64 and amd64**, with six architecture-independent companion packages.
- Each architecture index includes seven RC2 package types and retains the seven RC1 package types. Existing published package files were not overwritten.
- The archive's full signing-key fingerprint is **B0575F821A31DD20753DE07C50D21240F4BCB02E**.
- The signature was verified after publication. The restricted daily metadata-renewal timer is active; metadata expiry and APT authentication remain enabled.
- The public bootstrap is **https://daylightlinux.ch/daylight-install.sh**. Its default is a core-only plan; explicit application is required. It does not enable telemetry or start a display manager.

A new end-to-end verification against the **actual public HTTPS installer and archive** succeeded on disposable **Debian 12 Bookworm and Debian 13 Trixie** clients: GitHub Actions run **41431802078**. It exercised real installation, repeated repository configuration, update/removal simulation and actual removal without autoremove. Base OS identity remained unchanged.

## Production Raspberry Pi verification

After an APT simulation confirmed exactly two upgrades and zero new packages/removals, **daylight-core and daylight-themes were upgraded from RC1 to RC2** on the real Raspberry Pi 4. No desktop package was installed. The resulting `/usr/bin/daylight` reports **5.0.0-rc.2**.

All **11 integration tests passed against the installed native ARM64 executable**, as the normal user, including invalid-input handling, isolated temporary settings, calendar/conversion checks, CPU sampling, JSON output and disabled telemetry. Generated passwords were not logged. Installed package-file verification also passed.

Before/after checks confirmed:

- Apache, cloudflared, Docker and WireGuard retained their active states and main PIDs.
- Nextcloud's local status response was unchanged and maintenance mode was false.
- The hashes of OS identity, SSH configuration and the Daylight Apache virtual host were unchanged.
- The historical website remained available, and the archive renewal timer was active.

No reboot, network/SSH change, production-container restart, global distribution upgrade or public virtual-machine service was performed. Infrastructure snapshots and backup details are retained privately on the owner-controlled computers, not in this repository.

## Version and scope boundaries

The deliverable remains **5.0.0-rc.2**, a release candidate, not a claim of stable certification on all hardware. The exact software/image build and BIOS/UEFI/browser evidence are documented in `VALIDATION-RC2.md`; website-only changes did not require rebuilding the validated ISO.

Physical Pi desktop/input, physical PC Wi-Fi/audio, Secure Boot and ARM32 are not certified by this deployment. The browser trial uses the visitor's private QEMU/noVNC environment or their GitHub Codespace, not the production Pi; account allowances and possible hosting charges are explained on the site.

DistroSea inclusion and a Wikipedia article depend on external review and are not claimed. The address info@daylightlinux.ch is used as the project contact, but mail delivery is not certified by these software/deployment tests. The optional telemetry collector remains disabled and is not exposed as a production collection service. No unique-user count is inferred from boot events.
