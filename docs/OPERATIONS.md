# Maintaining the Daylight release infrastructure

Developer: Hamdy Abou El Anein — info@daylightlinux.ch

## Release order

1. Build and test the exact committed source revision with `daylight-build.yml`.
2. Require successful unit/integration checks, both Debian desktop lifecycles, live-filesystem boot, real BIOS/UEFI ISO boot and the browser connection test.
3. Put that run ID, exact commit and matching version tag in `release/READY.json`. Publish through the guarded release workflow. Published packages and ISO are retrieved from the successful run, not rebuilt.
4. Retrieve the published assets and verify SHA256SUMS. Import only the eight matching architecture/data `.deb` files into the signed archive.
5. Test the public archive, then build the static site from the published `release/current.json` and deploy it with a backup.

Never point the download page at a build that has not been published. Never overwrite the bytes of an already-published release to repair a bug; publish a new version.

## Signed archive installer

The server installer is `server/install-apt-server.sh`; it requires a full source checkout because its reviewed Python helpers and systemd units are adjacent. It is distinct from the public client bootstrap `scripts/daylight-install.sh`, served as `/daylight-install.sh`.

Prepare a directory containing only verified release `.deb` files plus `PACKAGE-SHA256SUMS` covering exactly those files. Maintain the dedicated signing key in a private directory outside the web root. Check the script's `--help` and plan before applying:

```sh
sudo sh server/install-apt-server.sh \
  --packages /path/to/verified-packages \
  --key-home /path/to/private-archive-key \
  --apply
```

The existing deployment uses a dedicated archive account, an immutable package pool, by-hash indexes, an atomic metadata switch, a separately stored private key and a daily restricted signing service. There is no resident APT application server: the HTTP server serves static files.

The public key fingerprint is `B0575F821A31DD20753DE07C50D21240F4BCB02E`. Its valid primary identity is `Daylight GNU/Linux Archive <info@daylightlinux.ch>`. The previous contact UID was revoked without changing the key fingerprint. The private key is never committed or placed under the HTTP document root.

## Health checks

```sh
systemctl status daylight-archive-refresh.timer
systemctl status daylight-archive-refresh.service
curl --fail https://daylightlinux.ch/apt/status.json
```

The timer must remain enabled. Release metadata expires after 30 days, even if no new package version is published. A failed signature renewal must be repaired; disabling APT's expiration or signature checks is not an acceptable workaround.

On an ordinary Debian user account, the public verification tool uses entirely temporary APT state and installs no host packages:

```sh
python3 release/check-public-apt.py --arch arm64
python3 release/check-public-apt.py --arch amd64
```

Add `--expected-version 5.0.0~rc2` when validating that particular version. The tool pins the signing key, verifies InRelease, makes genuine APT downloads, checks package architecture/version and confirms that host APT configuration and OS identity are unchanged.

Monitor the archive key's expiration independently of metadata expiration. Its current two-year validity requires a planned renewal/rotation before November 2028. Back up the private key securely outside the serving host; this repository contains no private-key backup.

## Website deployment

```sh
python3 website/build.py --output dist/site
sudo python3 server/deploy-site.py --source dist/site --apply
```

The deployment helper is scoped to the Daylight document root, refuses unexpected/symlink targets, preserves the previous website under `old/site`, retains a timestamped backup and replaces its own files. It does not change unrelated virtual hosts, DNS, TLS configuration or containers, and does not restart Apache. Keep the `apt` directory and signing state out of any generic website cleanup.

The site has English/French pages, local styles/scripts/images, an explicit archive route, a books page linking to the author's supplied Amazon store, and a compatibility redirect from `linux-book.html`. The public installer is copied from its reviewed source. Photography credits and original checksums are preserved. AI-generated artwork is identified as such; native dimensions are not inflated into a 4K claim.

## Browser demonstration

`demo/` provides a private QEMU/noVNC environment and `.devcontainer/demo/` integrates it with Codespaces. The guest is offline, ephemeral and time-limited. No VM runs on the production web server. A Codespace is created only when its user explicitly opens one and is subject to that account's quota/billing. Stop/delete the Codespace separately after the guest ends.

This is not an anonymous public multi-tenant VM service. DistroSea listing requires its operator and is not claimed merely because a browser demo works. See `demo/README.md` for the security boundary and costs.

## Recovery limits

Package removal preserves shared dependencies and personal settings and never runs autoremove. Website backups restore website files, not the full machine. Archive metadata can be switched back to retained release state, but expired signatures must be renewed. None of these operations is equivalent to a disk snapshot, database restore or full-machine disaster-recovery backup.
