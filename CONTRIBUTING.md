# Contributing to Daylight GNU/Linux

Developer and maintainer: Hamdy Abou El Anein — info@daylightlinux.ch.
Daylight's main audience is Raspberry Pi users. The PC live edition helps people explore the desktop.

## Useful first contributions

Improve one installation instruction, correct a French/English translation, report a reproducible issue, or test the ARM64 core on your Pi. Use the hardware report template to record exactly what you tested; do not infer broad compatibility from one test. The website's Community page links to all templates.

## A focused change

Open an issue describing the problem, check for duplicates, then submit a small pull request. Avoid unrelated formatting or generated binary changes. Keep existing attribution and third-party notices. New Daylight source files use GNU GPL v3, the project's developer/contact header and the language-appropriate comment syntax. Do not label someone else's code as your own.

## Validation

For Rust changes, run the formatting, Clippy and test commands in docs/BUILD.md. For website changes, run `python3 website/build.py`, `python3 tests/test_website.py --site dist/site` and the browser checks in `tests/test_website_browser.cjs`. The browser checker uses Playwright; it does not install packages globally. Retain screenshots and results locally, not in the source tree.

Never run package-removal or image-build tests on a production host. Use the disposable CI lifecycle checks described in docs/BUILD.md. Record the exact tested revision and do not replace immutable published release files.

## Privacy and respectful collaboration

Issues are public. Remove passwords, tokens, hostname/user details, MAC/IP addresses and serial numbers from logs and screenshots. Ask before publishing another person's information. Keep discussions technical and constructive. No fabricated benchmarks, user counts, reviews, mass promotional messages or automatic telemetry activation.

## Artwork and communication

Artwork provenance is in docs/ARTWORK.md. Share the website's media kit with its credits, and identify the 5.0.0-rc series as a release candidate. Real live screenshots are PC/VM evidence, not Pi performance figures. The founder and lead developer is Hamdy Abou El Anein.
