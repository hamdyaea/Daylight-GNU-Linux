# Cloudflare Pages deployment

Developer: Hamdy Abou El Anein — info@daylightlinux.ch.

Production migration branch: publish/cloudflare-pages-20261103. Root directory: repository root. Framework: None. Build command: `python3 scripts/build-cloudflare-pages.py`. Output: `dist/cloudflare-pages`.

The live preview runs on the visitor device. Its original initrd is split into three blocks no larger than 16 MiB. The loader verifies each block, assembles in order, then verifies the complete original SHA256. Cancellation, bounded retries and no-relay behavior are preserved. No R2 or paid service is used. The archive of corresponding sources is separately distributed with GitHub Releases; the old URL redirects there.

The current static APT repository, public keys, media, translated pages and project-source downloads are included. Do not run the old Pi deploy scripts against Pages. Future package releases must regenerate the signed APT index and republish its reviewed files. Source files and public metadata were copied from the current Pi; logs, credentials and ACME directories were excluded.

First publish to pages.dev and test all pages, the actual guest keyboard, restart/stop, downloads, APT indexes and source archive redirect. Only then attach daylightlinux.ch and www.daylightlinux.ch. Preserve MX/TXT records and all other subdomains. Keep cloudflared for cloud.daylightlinux.ch and miner.daylightlinux.ch.

To refresh the runtime from a reviewed publication: `python3 scripts/split-pages-runtime.py --runtime /absolute/path/to/reviewed-runtime`. Commit the updated runtime and retain corresponding sources. Run `web-live/test-chunks.cjs` for controlled corruption, cancellation and retry tests.
