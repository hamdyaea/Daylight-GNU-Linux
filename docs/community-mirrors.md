# Hosting a Daylight GNU/Linux community APT mirror

Thank you for helping distribute Daylight GNU/Linux.

## Requirements

- A publicly reachable HTTPS server with a valid TLS certificate.
- Sufficient storage and bandwidth for the complete published APT repository.
- Regular synchronization from the official repository at `https://daylightlinux.ch/apt/`.
- Preserve all files, including `dists/`, `pool/`, signatures and repository metadata, without modifying or re-signing them.
- A reachable `dists/daylight/InRelease` endpoint.

## Example synchronization

Use a temporary staging directory and publish only complete successful syncs. The following command downloads a copy for initial testing:

```bash
mkdir -p daylight-apt
wget --mirror --no-parent --no-host-directories --cut-dirs=1 \
  --reject 'index.html*' --directory-prefix=daylight-apt \
  https://daylightlinux.ch/apt/
```

Check the resulting directory layout before making it public; the published URL must contain `dists/daylight/InRelease`. Do not expose partial synchronization results. Check signatures using the official Daylight APT keyring before publishing.

## Registration

Submit the [community mirror registration form](https://github.com/hamdyaea/Daylight-GNU-Linux/issues/new?template=community_mirror.yml) with your public HTTPS URL, country code and optional display name. Do not include passwords, tokens or private email addresses.

After approval, monitoring checks the mirror periodically. Public listing requires 24 consecutive hours of successful checks. Unhealthy mirrors can be hidden from the public directory.

Official site: https://daylightlinux.ch/mirrors.html
