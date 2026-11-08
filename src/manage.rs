// Developer: Hamdy Abou El Anein
// Contact: info@daylightlinux.ch
// Copyright (C) 2026 Hamdy Abou El Anein
// SPDX-License-Identifier: GPL-3.0-only
use crate::{config, system, Result};
use std::{
    fs,
    io::Write,
    os::unix::fs::PermissionsExt,
    path::Path,
    process::{Command, Stdio},
};
pub const PACKAGES: &[&str] = &[
    "daylight-linux",
    "daylight-desktop",
    "daylight-apps",
    "daylight-games",
    "daylight-telemetry",
    "daylight-themes",
    "daylight-core",
];
fn installed() -> Result<Vec<String>> {
    let out = Command::new("/usr/bin/dpkg-query")
        .args([
            "-W",
            "-f=${binary:Package}\t${db:Status-Status}\n",
            "daylight-*",
        ])
        .output()?;
    let text = String::from_utf8(out.stdout)?;
    Ok(text
        .lines()
        .filter_map(|l| {
            let (name, state) = l.split_once('\t')?;
            let name = name.split(':').next()?;
            if state == "installed" && PACKAGES.contains(&name) {
                Some(name.to_owned())
            } else {
                None
            }
        })
        .collect())
}
pub fn packages(action: &str, dry_run: bool) -> Result<()> {
    let packages = installed()?;
    if packages.is_empty() {
        return Err("No installed Daylight packages were found; this operation is for Debian-based installations".into());
    }
    if !dry_run && config::effective_uid() != Some(0) {
        return Err(
            format!("Run sudo daylight {action}, or use daylight {action} --dry-run").into(),
        );
    }
    if action == "update" && !dry_run {
        let status = Command::new("/usr/bin/apt-get")
            .args(["-o", "APT::Update::Error-Mode=any", "update"])
            .status()?;
        if !status.success() {
            return Err("APT index refresh failed; no upgrade was attempted".into());
        }
    }
    let mut cmd = Command::new("/usr/bin/apt-get");
    if dry_run {
        cmd.arg("--simulate");
    }
    match action {
        "update" => {
            cmd.args([
                "install",
                "--only-upgrade",
                "--no-remove",
                "--no-install-recommends",
            ]);
        }
        "remove" => {
            cmd.args(["remove", "--no-auto-remove"]);
        }
        _ => return Err("Unsupported package operation".into()),
    }
    cmd.args(packages);
    eprintln!("Only installed Daylight packages are requested. APT may propose dependency changes; review its confirmation. No autoremove or full system upgrade is run.");
    if !cmd.status()?.success() {
        return Err("APT did not complete the requested operation".into());
    }
    Ok(())
}
pub fn doctor() -> Result<()> {
    println!(
        "Daylight GNU/Linux {} diagnostics (local, read-only)",
        crate::VERSION
    );
    println!("Base: {}", system::snapshot().base);
    for (name, path) in [
        ("Daylight resources", "/usr/share/daylight"),
        ("Fluxbox", "/usr/bin/fluxbox"),
        ("Conky", "/usr/bin/conky"),
        ("Native dialogs", "/usr/bin/yad"),
        ("Fastfetch (optional)", "/usr/bin/fastfetch"),
        ("Terminology (optional)", "/usr/bin/terminology"),
    ] {
        println!(
            "{name}: {}",
            if Path::new(path).exists() {
                "available"
            } else {
                "not installed (may be intentional on a server)"
            }
        );
    }
    println!(
        "Desktop configuration is isolated under ~/.config/daylight. No repair was performed."
    );
    telemetry("status")?;
    Ok(())
}
fn telemetry_config() -> (bool, String) {
    let content = fs::read_to_string("/etc/daylight/telemetry.conf").unwrap_or_default();
    let mut enabled = false;
    let mut endpoint = String::new();
    for line in content.lines() {
        if let Some((k, v)) = line.split_once('=') {
            match k.trim() {
                "enabled" => enabled = v.trim() == "yes",
                "endpoint" => endpoint = v.trim().to_owned(),
                _ => (),
            }
        }
    }
    (enabled, endpoint)
}
pub fn valid_endpoint(url: &str) -> bool {
    url.starts_with("https://")
        && url.len() > 8
        && url.len() < 2048
        && !url.chars().any(|c| c.is_control() || c.is_whitespace())
        && !url[8..].contains('@')
}
pub fn telemetry(action: &str) -> Result<()> {
    let (enabled, endpoint) = telemetry_config();
    match action {
        "status" => {
            println!(
                "Boot statistics: {}. Endpoint: {}.",
                if enabled { "enabled" } else { "disabled" },
                if endpoint.is_empty() {
                    "not configured"
                } else {
                    "configured"
                }
            );
        }
        "privacy" => print!("{}", crate::PRIVACY),
        "on" | "off" => {
            if config::effective_uid() != Some(0) {
                return Err("Use sudo daylight telemetry on|off".into());
            }
            if !Path::new("/etc/daylight/telemetry.conf").is_file() {
                return Err("The optional daylight-telemetry package is not installed".into());
            }
            if action == "on" && !valid_endpoint(&endpoint) {
                return Err("A deployed, privacy-reviewed HTTPS collector endpoint must be configured first; nothing was enabled".into());
            }
            let content=format!("# Developer: Hamdy Abou El Anein\n# Contact: info@daylightlinux.ch\n# SPDX-License-Identifier: GPL-3.0-only\n# Explicit opt-in; review the privacy documentation before enabling.\nenabled={}\nendpoint={}\n",if action=="on"{"yes"}else{"no"},endpoint);
            config::atomic_write(
                Path::new("/etc/daylight/telemetry.conf"),
                content.as_bytes(),
            )?;
            fs::set_permissions(
                "/etc/daylight/telemetry.conf",
                fs::Permissions::from_mode(0o644),
            )?;
            let status = Command::new("/usr/bin/systemctl")
                .args([
                    if action == "on" { "enable" } else { "disable" },
                    "--now",
                    "daylight-telemetry.timer",
                ])
                .status()?;
            if !status.success() {
                return Err(
                    "Configuration saved, but systemd could not change the Daylight timer".into(),
                );
            }
            if action == "off" {
                let _ = Command::new("/usr/bin/systemctl")
                    .args(["stop", "daylight-telemetry.service"])
                    .status();
            }
            println!(
                "Boot statistics {}",
                if action == "on" {
                    "enabled"
                } else {
                    "disabled"
                }
            );
        }
        "send" => {
            if !enabled {
                return Ok(());
            }
            if !valid_endpoint(&endpoint) {
                return Err("Invalid telemetry endpoint".into());
            }
            let body = format!(
                "{{\"event\":\"boot\",\"version\":\"{}\",\"mode\":\"{}\"}}",
                crate::VERSION,
                system::mode()
            );
            let mut child = Command::new("/usr/bin/curl")
                .args([
                    "--disable",
                    "--silent",
                    "--show-error",
                    "--fail",
                    "--proto",
                    "=https",
                    "--tlsv1.2",
                    "--connect-timeout",
                    "2",
                    "--max-time",
                    "5",
                    "--max-redirs",
                    "0",
                    "--write-out",
                    "%{http_code}",
                    "--user-agent",
                    "Daylight-Boot-Counter",
                    "--header",
                    "Content-Type: application/json",
                    "--data-binary",
                    "@-",
                    "--output",
                    "/dev/null",
                    "--url",
                    &endpoint,
                ])
                .stdin(Stdio::piped())
                .stdout(Stdio::piped())
                .spawn()?;
            if let Some(mut stdin) = child.stdin.take() {
                stdin.write_all(body.as_bytes())?;
            }
            let output = child.wait_with_output()?;
            if !output.status.success() || output.stdout != b"204" {
                return Err(
                    "Boot event was not confirmed with HTTP 204; no persistent queue or retry was created".into(),
                );
            }
        }
        _ => return Err("Use telemetry status|privacy|on|off|send".into()),
    }
    Ok(())
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn endpoints() {
        assert!(valid_endpoint("https://example.org/boot"));
        for url in [
            "http://example.org",
            "https://",
            "https://user:pass@example.org",
            "https://example.org\n--insecure",
        ] {
            assert!(!valid_endpoint(url));
        }
    }
}
