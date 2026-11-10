# Daylight GNU/Linux community APT mirrors

Daylight's official signed APT repository is https://daylightlinux.ch/apt/. Hosting a mirror is voluntary. A mirror operator supplies their own HTTPS hosting, storage and bandwidth; Daylight does not charge a registration fee.

## Installation

1. Prepare a public HTTPS virtual host pointing at /srv/daylight-mirror.
2. Obtain the **official archive signing key** from a separately trusted channel and check its full fingerprint: `B0575F821A31DD20753DE07C50D21240F4BCB02E`. Do not trust a key downloaded from the same unverified source you are mirroring.
3. Install Python 3, GnuPG (`gpgv`), and download `scripts/daylight-mirror-sync.py` from the official repository. Review the script.
4. Run:

```bash
python3 daylight-mirror-sync.py --trusted-keyring /etc/daylight/archive-keyring.gpg --dest /srv/daylight-mirror
```

5. Configure a systemd oneshot service running the same command under an unprivileged account and a systemd timer with `OnCalendar=*:0/15`, `Persistent=true` and `RandomizedDelaySec=120`. Do not run it as root.
6. Test that `https://YOUR-HOST/dists/daylight/InRelease` is publicly reachable.

The synchronizer verifies the pinned GPG key, expiry, signed package indexes, and SHA256 for referenced packages. The official signed metadata is installed after the packages.

## Registration and removal

Email info@daylightlinux.ch with your HTTPS mirror URL, country, optional public name, and an operator contact address. This is a manual, opt-in registration until the authenticated submission endpoint is deployed. The contact address is private.

The central checker `scripts/daylight-mirror-health.py` uses a private JSON registry and exports a public JSON file. A mirror must remain healthy for 24 consecutive hours before it appears publicly. A failed check hides it from the public list until another 24-hour healthy period. The original registry record is retained so a mirror can recover without re-registering. Ask by email to remove your registration.

**Security and deployment:** Before enabling automatic public registrations, implement domain ownership proof, HTTPS and DNS/IP validation to block SSRF, authenticated operator controls, rate limiting, and an abuse policy. Do not redirect APT clients automatically to unverified community mirrors.

## Free binary distribution

GitHub Releases can host release assets. SourceForge file hosting is another free open-source option subject to project approval and service terms. Do not introduce paid object storage or require a paid subscription.