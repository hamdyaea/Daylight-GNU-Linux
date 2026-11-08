# Changelog

## 5.0.0~rc4-1 — 2026-11-08

- Restore the full balanced Conky dashboard and preserve custom monitor configurations through updates and profile changes.
- Prepare Tk wrappers before mapping on Wayland, fixing native clicks sent to an older overlapping Tk application; keep Shardturn source unchanged.
- Upgrade a running RC4 appearance helper when an ordinary updated application opens, without restarting the desktop session.
- Validate actual native Wayland input with Conky and an authentic old RC4 window, including Shardturn's in-window help panel and Timer start/cancel.

## 5.0.0-rc.4 — 2026-11-08

- Publish the RC4 native desktop refresh: Shardturn, ten illustrated games, redesigned utilities, application search, first steps, live settings, Sun & Moon and Raspberry Pi health.
- Preserve the RC3 telemetry integration and explicit opt-in; the full install includes its disabled package.

- Upgrade existing RC3 installations through `sudo daylight update`, with automatic GUI dependencies and first-open session handoff.
- Add the optional telemetry package to the public installer’s `--all` plan while keeping it disabled until explicit opt-in.

## 5.0.0-rc.3

Publishes the opt-in boot telemetry endpoint and privacy description. Telemetry remains disabled by default; users must install the optional package and explicitly enable it. This package-only candidate updates the APT packages; the validated RC2 live ISO is unchanged.

## 5.0.0-rc.1

Modular AMD64/ARM64 Debian packages, local Rust tools, isolated Fluxbox session, modern Conky profiles, Fastfetch with ASCII fallback, optional applications, disabled opt-in boot counter and Debian Live build/test recipes. See docs/VALIDATION.md for actual test results and remaining release gates.