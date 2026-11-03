# Cloudflare Pages deployment

Developer: Hamdy Abou El Anein — info@daylightlinux.ch.

Production migration branch: publish/cloudflare-pages-20261103. Root directory: repository root. Framework: None. Build command: `python3 scripts/build-cloudflare-pages.py`. Output: `dist/cloudflare-pages`.

The live preview runs on the visitor device. Its original initrd is split into three blocks no larger than 16 MiB. The loader verifies each block, assembles in order, then verifies the complete original SHA256. Cancellation, bounded retries and no-relay behavior are preserved. No R2 or paid service is used. The archive of corresponding sources is separately distributed with GitHub Releases; the old URL redirects there.

The current static APT repository, public keys, media, translated pages and project-source downloads are included. Do not run the old Pi deploy scripts against Pages. Future package releases must regenerate the signed APT index. On the Pi, successful daylight-archive-refresh.service completion now triggers daylight-pages-publish.service. The publisher verifies the signature and expiry, dereferences generated symlinks into regular static files, and commits/pushes only website-src/apt to this Pages branch using a repository-specific SSH deploy key. The public site does not depend on the Pi at request time. Source files and public metadata were copied from the current Pi; logs, credentials and ACME directories were excluded.

First publish to pages.dev and test all pages, the actual guest keyboard, restart/stop, downloads, APT indexes and source archive redirect. Only then attach daylightlinux.ch and www.daylightlinux.ch. Preserve MX/TXT records and all other subdomains. Keep cloudflared for cloud.daylightlinux.ch and miner.daylightlinux.ch.

To refresh the runtime from a reviewed publication: `python3 scripts/split-pages-runtime.py --runtime /absolute/path/to/reviewed-runtime`. Commit the updated runtime and retain corresponding sources. Run `web-live/test-chunks.cjs` for controlled corruption, cancellation and retry tests.


## Pi maintenance after migration

The shared cloudflared tunnel remains required for MinerWatch and Nextcloud. The six root/www site routes were removed from its local ingress configuration after the custom domains became active on Pages. Five old Apache site configurations were disabled; the MinerWatch virtual host remains enabled. Former web roots, configuration snapshots and obsolete certificate-renewal definitions are archived under /var/backups/cloudflare-pages-migration on the Pi. Issued certificates were retained. The signed APT working directory and its signing key remain on the Pi. Do not remove the publisher deploy keys while the update jobs use them.

Publisher source: `server/pages-publish.py`. Service account: pages-publisher; state: /var/lib/pages-publisher; installed script: /usr/local/lib/pages-publisher/publish.py. Production branch remains publish/cloudflare-pages-20261103; coordinate the service configuration if changing branches. Publisher jobs refuse uncommitted or diverged work and never force-push.
