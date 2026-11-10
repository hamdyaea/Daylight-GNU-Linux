# Daylight GNU/Linux community APT mirrors

Daylight's official signed APT repository is https://daylightlinux.ch/apt/. Hosting a mirror is voluntary. A mirror operator supplies their own HTTPS hosting, storage and bandwidth; Daylight does not charge a registration fee.

## Installation

1. Prepare a public HTTPS virtual host pointing at /srv/daylight-mirror.
2. Obtain the **official archive signing key** from a separately trusted channel and check its full fingerprint: `B0575F821A31DD20753DE07C50D21240F4BCB02E`. Do not trust a key downloaded from the same unverified source you are mirroring.
3. Install Python 3, GnuPG (`gpgv`), and download both `scripts/daylight-mirror-sync.py` and `scripts/daylight-mirror-install.sh` from the official repository. Review both scripts.
4. Configure the mirror service and timer (replace the hostname):

```bash
sudo MIRROR_HOST=mirror.example.org TRUSTED_KEYRING=/etc/daylight/archive-keyring.gpg bash daylight-mirror-install.sh
sudo systemctl start daylight-mirror-sync.service
sudo systemctl status daylight-mirror-sync.service
```

The installer does not configure or expose your web server automatically. Point an existing HTTPS virtual host at `/srv/daylight-mirror`.

5. The installer creates an unprivileged systemd service and a timer with `OnCalendar=*:0/15`, `Persistent=true` and `RandomizedDelaySec=120`.
6. Test that `https://YOUR-HOST/dists/daylight/InRelease` is publicly reachable.

The synchronizer verifies the pinned GPG key, expiry, signed package indexes, and SHA256 for referenced packages. The official signed metadata is installed after the packages.

## Registration and removal

Use the [GitHub mirror registration form](https://github.com/hamdyaea/Daylight-GNU-Linux/issues/new?template=community_mirror.yml), or email info@daylightlinux.ch with your HTTPS mirror URL, country, optional public name, and an operator contact address. This is a manual, opt-in registration until the authenticated submission endpoint is deployed. The contact address is private.

The central checker `scripts/daylight-mirror-health.py` uses a private JSON registry and exports a public JSON file. A mirror must remain healthy for 24 consecutive hours before it appears publicly. A failed check hides it from the public list until another 24-hour healthy period. The original registry record is retained so a mirror can recover without re-registering. Ask by email to remove your registration.

**Security and deployment:** Before enabling automatic public registrations, implement domain ownership proof, HTTPS and DNS/IP validation to block SSRF, authenticated operator controls, rate limiting, and an abuse policy. Do not redirect APT clients automatically to unverified community mirrors.

## Free binary distribution

GitHub Releases can host release assets. SourceForge file hosting is another free open-source option subject to project approval and service terms. Do not introduce paid object storage or require a paid subscription.