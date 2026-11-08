// Developer: Hamdy Abou El Anein
// Contact: info@daylightlinux.ch
// Copyright (C) 2026 Hamdy Abou El Anein
// SPDX-License-Identifier: GPL-3.0-only
//! The Rust command line launches the native, on-demand Tk desktop suite.
//! The graphical layer uses the same offline vector design as Shardturn.
use crate::{config, Result};
use std::{path::Path, process::Command};

const GUI: &str = "/usr/share/daylight/ui/daylight_gui.py";

pub fn valid_application(name: &str) -> bool {
    matches!(
        name,
        "home"
            | "info"
            | "welcome"
            | "password"
            | "temperature"
            | "days"
            | "connect"
            | "dice"
            | "coin"
            | "lottery"
            | "rpsls"
            | "cards"
            | "tournament"
            | "basketball"
            | "memory"
            | "slots"
            | "guess"
            | "speech"
            | "alarm"
            | "settings"
            | "privacy"
            | "telemetry"
            | "monitor"
            | "doctor"
            | "sky"
            | "launcher"
            | "shardturn"
    )
}

pub fn center() -> Result<()> {
    application("home")
}

pub fn application(name: &str) -> Result<()> {
    if !valid_application(name) {
        return Err("Unknown application. Run daylight --help for application names".into());
    }
    if config::effective_uid() == Some(0) {
        return Err("Do not run desktop applications as root".into());
    }
    if !Path::new(GUI).is_file() || !Path::new("/usr/bin/python3").is_file() {
        return Err("Install daylight-desktop for native graphical applications; the Rust CLI works independently".into());
    }
    let status = Command::new("/usr/bin/python3")
        .args([GUI, name])
        .status()?;
    if !status.success() {
        return Err("The Daylight desktop application did not complete successfully".into());
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn known_applications_only() {
        for name in ["home", "cards", "shardturn", "sky", "launcher", "telemetry"] {
            assert!(valid_application(name));
        }
        for name in ["", "../shardturn", "$(id)", "settings;id", "does-not-exist"] {
            assert!(!valid_application(name));
        }
    }
}
