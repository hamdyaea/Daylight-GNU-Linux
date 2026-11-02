# Daylight website — Raspberry Pi first

Developer: Hamdy Abou El Anein — info@daylightlinux.ch.

## Product hierarchy

Raspberry Pi is the primary use case. The main action leads to the Raspberry Pi guide and Debian package installation. The AMD64 ISO is explicitly a PC live environment for discovering and testing the desktop, not a Raspberry Pi SD-card image. The current release is read from release/current.json; the APT archive is deployed separately and must remain aligned with the intended published candidate.

## Navigation and discoverability

Sixteen pages in each of English and French share a complete native HTML details/summary menu and footer directory. Every page remains reachable without JavaScript. Escape and outside/focus dismissal enhance keyboard use. The page set includes Raspberry Pi, installation, downloads, discovery, screenshots, browser demo, wallpapers, news, FAQ, community, project information, books, a media kit, Old and privacy.

CSS and JavaScript filenames include their content hashes to avoid stale mobile styling. The site is static, with no new service, web font, analytics SDK, account system or guest VM on the Raspberry Pi. Share actions run only after a visitor clicks; RSS is static and account-free.

Titles and descriptions are page-specific, with canonical and language-alternate links, a complete sitemap, Open Graph/social preview metadata and truthful JSON-LD. The inline JSON-LD has an exact CSP hash; unsafe-inline is not enabled. There are no fabricated ratings, users or speed claims.

Reference design guidance: https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/examples/disclosure-navigation/ and https://developers.google.com/search/docs/fundamentals/seo-starter-guide . These changes help visitors and crawlers understand the site; they do not guarantee ranking or popularity.

## Build and check

Run scripts/render-assets.sh first when the rendered assets are missing. Python 3 and Pillow are required for the site builder.

```sh
python3 website/build.py --output dist/site
python3 tests/test_website.py --site dist/site
```

Verified screenshots can be supplied with --evidence DIR. Otherwise the builder looks for dist/site-evidence/<release tag>. Screenshots must belong to the published version and be checked against its release-asset hashes. Missing screenshots produce an honest link to the original release instead of a fabricated preview.

For the real-browser suite, serve dist/site locally on 127.0.0.1:34402 and run tests/test_website_browser.cjs with DAYLIGHT_PLAYWRIGHT pointing to an installed Playwright module and DAYLIGHT_BROWSER pointing to Chromium. The dedicated website workflow does this in a disposable runner; website-only changes no longer rebuild a full Linux ISO.

The media ZIP includes project artwork, credits, its GPL notice and available verified screenshots, never standalone font files.

## Deployment boundaries

server/deploy-site.py copies the generated static site, backs up the current site and preserves old/site and apt. It does not restart Apache, Docker or Nextcloud. Run it only against the reviewed generated directory. Check the public HTML, hashed resources, RSS, sitemap, books link and archive after publication; compare production service/Nextcloud state before and after. Infrastructure snapshots remain private under dist, not in Git.
