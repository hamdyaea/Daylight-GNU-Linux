// Developer: Hamdy Abou El Anein
// Contact: info@daylightlinux.ch
// Copyright (C) 2026 Hamdy Abou El Anein
// SPDX-License-Identifier: GPL-3.0-only
use crate::Result;
use std::{
    collections::BTreeMap,
    env,
    fs::{self, OpenOptions},
    io::Write,
    os::unix::fs::{OpenOptionsExt, PermissionsExt},
    path::{Path, PathBuf},
};
pub fn root() -> Result<PathBuf> {
    if let Some(p) = env::var_os("XDG_CONFIG_HOME") {
        let p = PathBuf::from(p);
        if p.is_absolute() {
            return Ok(p.join("daylight"));
        }
    }
    let home = PathBuf::from(env::var_os("HOME").ok_or("HOME is not set")?);
    if !home.is_absolute() {
        return Err("HOME must be absolute".into());
    }
    Ok(home.join(".config/daylight"))
}
pub fn load() -> Result<BTreeMap<String, String>> {
    let mut result = BTreeMap::from([
        ("monitor".into(), "on".into()),
        ("fetch".into(), "on".into()),
        ("profile".into(), "balanced".into()),
        ("wallpaper".into(), "daylight-mountains.jpg".into()),
    ]);
    let path = root()?.join("settings.conf");
    match fs::read_to_string(path) {
        Ok(content) => {
            for line in content.lines() {
                if let Some((k, v)) = line.split_once('=') {
                    if valid(k.trim(), v.trim()) {
                        result.insert(k.trim().to_string(), v.trim().to_string());
                    }
                }
            }
        }
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => (),
        Err(e) => return Err(e.into()),
    };
    Ok(result)
}
pub fn valid(key: &str, value: &str) -> bool {
    match key {
        "monitor" | "fetch" => matches!(value, "on" | "off"),
        "profile" => matches!(value, "minimal" | "balanced"),
        "wallpaper" => matches!(
            value,
            "daylight-mountains.jpg"
                | "daylight-night.jpg"
                | "daylight-original.png"
                | "daylight-sunrise.jpg"
                | "daylight-himalaya.jpg"
        ),
        _ => false,
    }
}
pub fn atomic_write(path: &Path, content: &[u8]) -> Result<()> {
    let parent = path.parent().ok_or("Missing parent")?;
    fs::create_dir_all(parent)?;
    let temporary = parent.join(format!(".daylight-{}.tmp", std::process::id()));
    let mut file = OpenOptions::new()
        .write(true)
        .create_new(true)
        .mode(0o600)
        .open(&temporary)?;
    let result = (|| -> Result<()> {
        file.write_all(content)?;
        file.sync_all()?;
        fs::rename(&temporary, path)?;
        Ok(())
    })();
    if result.is_err() {
        let _ = fs::remove_file(&temporary);
    }
    result
}
pub fn set(key: &str, value: &str) -> Result<()> {
    if !valid(key, value) {
        return Err("Invalid setting or value".into());
    }
    if effective_uid() == Some(0) {
        return Err("Run desktop settings as the desktop user, not root".into());
    }
    let mut data = load()?;
    data.insert(key.to_string(), value.to_string());
    let directory = root()?;
    fs::create_dir_all(&directory)?;
    fs::set_permissions(&directory, fs::Permissions::from_mode(0o700))?;
    let mut content = String::from("# Developer: Hamdy Abou El Anein\n# Contact: info@daylightlinux.ch\n# SPDX-License-Identifier: GPL-3.0-only\n# Daylight user settings; no shell code is evaluated.\n");
    for (k, v) in data {
        content.push_str(&format!("{k}={v}\n"));
    }
    atomic_write(&directory.join("settings.conf"), content.as_bytes())
}
pub fn effective_uid() -> Option<u32> {
    fs::read_to_string("/proc/self/status")
        .ok()?
        .lines()
        .find_map(|l| l.strip_prefix("Uid:"))?
        .split_whitespace()
        .nth(1)?
        .parse()
        .ok()
}
pub fn setup_session() -> Result<()> {
    if effective_uid() == Some(0) {
        return Err("Do not run the graphical session as root".into());
    }
    let dir = root()?;
    fs::create_dir_all(dir.join("fluxbox"))?;
    let base = "/usr/share/daylight";
    let init = dir.join("fluxbox/init");
    if !init.exists() {
        let template = fs::read_to_string(format!("{base}/fluxbox/init"))?;
        atomic_write(
            &init,
            template
                .replace("@@CONFIG@@", &dir.to_string_lossy())
                .as_bytes(),
        )?;
    }
    let settings = load()?;
    let template = if settings["profile"] == "minimal" {
        "minimal.conf"
    } else {
        "balanced.conf"
    };
    let mut interface = crate::system::snapshot().interface;
    if !interface
        .bytes()
        .all(|b| b.is_ascii_alphanumeric() || b"_.:-".contains(&b))
        || interface.is_empty()
    {
        interface = "lo".into();
    }
    let text = fs::read_to_string(format!("{base}/conky/{template}"))?
        .replace("@@INTERFACE@@", &interface);
    atomic_write(&dir.join("conky.conf"), text.as_bytes())?;
    println!("{}", dir.display());
    Ok(())
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn rejects_injection_and_unknown() {
        assert!(!valid("wallpaper", "../../etc/passwd"));
        assert!(!valid("monitor", "on;id"));
        assert!(!valid("unknown", "on"));
    }
    #[test]
    fn supports_profiles() {
        assert!(valid("profile", "minimal"));
        assert!(valid("fetch", "off"));
    }
}
