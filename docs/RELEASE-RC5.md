# Daylight GNU/Linux 5.0.0 RC5

This candidate incorporates the verified desktop usability improvements merged in PR #10.

- Terminator terminal with Daylight theme, xterm fallback and normal copy/paste.
- Clear Web browser launcher.
- Fluxbox restart and shutdown actions with confirmation.
- A short random fortune on new Daylight Terminal sessions.
- Optional WhyDown diagnostic launcher, with explicit opt-in installation instructions.
- Debian 12/13 AMD64 and ARM64 packages and Live ISO subject to full candidate validation.
- Telemetry remains opt-in and disabled on fresh installations.

The AUR CLI-only PKGBUILD is source material and is not a published Arch desktop package. The keyboard `~` popup and the `reboot` command require further manual regression testing.

Only use artifacts from a successful complete GitHub Actions run for the exact released commit. Verify SHA256SUMS before installing.
