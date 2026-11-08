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

// Exact RC4 stock bytes are retained for migration to the restored dashboard.
// A shared header or a filename alone must never classify user content as ours.
const RC4_BALANCED: &str = include_str!("conky-balanced-rc4.conf");

fn matches_conky_template(content: &str, template: &str) -> bool {
    let Some((prefix, _)) = template.split_once("@@INTERFACE@@") else {
        return content == template;
    };
    let Some(rest) = content.strip_prefix(prefix) else {
        return false;
    };
    let interface: String = rest
        .chars()
        .take_while(|c| c.is_ascii_alphanumeric() || "_.:-".contains(*c))
        .take(64)
        .collect();
    !interface.is_empty() && template.replace("@@INTERFACE@@", &interface) == content
}

fn prepare_conky(
    directory: &Path,
    templates: &Path,
    profile: &str,
    interface: &str,
) -> Result<bool> {
    let path = directory.join("conky.conf");
    let generated = directory.join(".conky-generated");
    let balanced = fs::read_to_string(templates.join("balanced.conf"))?;
    let minimal = fs::read_to_string(templates.join("minimal.conf"))?;
    let selected = if profile == "minimal" {
        &minimal
    } else {
        &balanced
    };
    let desired = selected.replace("@@INTERFACE@@", interface);
    let current = match fs::symlink_metadata(&path) {
        // Links and nonregular files belong to the user, even if their target
        // happens to contain stock bytes. Never replace the user's link.
        Ok(info) if !info.is_file() || info.file_type().is_symlink() => return Ok(false),
        Ok(_) => Some(fs::read(&path)?),
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => None,
        Err(error) => return Err(error.into()),
    };
    if let Some(bytes) = current.as_deref() {
        let managed = fs::read(&generated).is_ok_and(|previous| previous == bytes)
            || std::str::from_utf8(bytes).is_ok_and(|text| {
                [&balanced[..], &minimal[..], RC4_BALANCED]
                    .iter()
                    .any(|template| matches_conky_template(text, template))
            });
        if !managed {
            return Ok(false);
        }
    }
    if current.as_deref() != Some(desired.as_bytes()) {
        atomic_write(&path, desired.as_bytes())?;
    }
    if fs::read(&generated).ok().as_deref() != Some(desired.as_bytes()) {
        atomic_write(&generated, desired.as_bytes())?;
    }
    Ok(true)
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
    let mut interface = crate::system::snapshot().interface;
    if !interface
        .bytes()
        .all(|b| b.is_ascii_alphanumeric() || b"_.:-".contains(&b))
        || interface.is_empty()
    {
        interface = "lo".into();
    }
    // Session startup and ordinary app opening are not permission to replace a
    // customised dashboard. Profile transitions update only verified stock.
    prepare_conky(
        &dir,
        &Path::new(base).join("conky"),
        &settings["profile"],
        &interface,
    )?;
    println!("{}", dir.display());
    Ok(())
}
#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::atomic::{AtomicUsize, Ordering};

    struct ConkyFixture(PathBuf);
    impl ConkyFixture {
        fn new() -> Self {
            static NEXT: AtomicUsize = AtomicUsize::new(0);
            let path = env::temp_dir().join(format!(
                "daylight-conky-{}-{}",
                std::process::id(),
                NEXT.fetch_add(1, Ordering::Relaxed)
            ));
            fs::create_dir_all(path.join("templates")).unwrap();
            fs::write(
                path.join("templates/balanced.conf"),
                include_str!("../config/conky/balanced.conf"),
            )
            .unwrap();
            fs::write(
                path.join("templates/minimal.conf"),
                include_str!("../config/conky/minimal.conf"),
            )
            .unwrap();
            Self(path)
        }
        fn prepare(&self, profile: &str, interface: &str) -> bool {
            prepare_conky(&self.0, &self.0.join("templates"), profile, interface).unwrap()
        }
        fn text(&self) -> String {
            fs::read_to_string(self.0.join("conky.conf")).unwrap()
        }
    }
    impl Drop for ConkyFixture {
        fn drop(&mut self) {
            let _ = fs::remove_dir_all(&self.0);
        }
    }
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

    #[test]
    fn missing_conky_gets_full_dashboard_and_setup_is_idempotent() {
        let fixture = ConkyFixture::new();
        assert!(fixture.prepare("balanced", "wlan0"));
        let path = fixture.0.join("conky.conf");
        let initial = fs::metadata(&path).unwrap().modified().unwrap();
        let text = fixture.text();
        for required in [
            "${cpugraph",
            "${downspeedgraph wlan0",
            "${upspeedgraph wlan0",
            "Top CPU",
            "Top memory",
            "/^unavailable$/d",
        ] {
            assert!(text.contains(required), "missing {required}");
        }
        assert!(!text.contains("@@INTERFACE@@"));
        assert!(fixture.prepare("balanced", "wlan0"));
        assert_eq!(fs::metadata(&path).unwrap().modified().unwrap(), initial);
    }

    #[test]
    fn exact_rc4_basic_profile_migrates_to_full_dashboard() {
        let fixture = ConkyFixture::new();
        fs::write(
            fixture.0.join("conky.conf"),
            RC4_BALANCED.replace("@@INTERFACE@@", "wlan0"),
        )
        .unwrap();
        assert!(fixture.prepare("balanced", "eth0"));
        assert!(fixture.text().contains("${downspeedgraph eth0"));
        assert!(fixture.text().contains("Top memory"));
    }

    #[test]
    fn custom_dashboard_is_preserved_including_profile_changes() {
        let fixture = ConkyFixture::new();
        let custom = RC4_BALANCED
            .replace("@@INTERFACE@@", "wlan0")
            .replace("DAYLIGHT", "MY DASHBOARD");
        fs::write(fixture.0.join("conky.conf"), &custom).unwrap();
        assert!(!fixture.prepare("balanced", "eth0"));
        assert!(!fixture.prepare("minimal", "eth0"));
        assert_eq!(fixture.text(), custom);
        assert!(!fixture.0.join(".conky-generated").exists());
    }

    #[test]
    fn edits_to_last_generated_dashboard_are_never_overwritten() {
        let fixture = ConkyFixture::new();
        assert!(fixture.prepare("balanced", "eth0"));
        let custom = fixture.text() + "\n-- User-selected dashboard layout\n";
        fs::write(fixture.0.join("conky.conf"), &custom).unwrap();
        assert!(!fixture.prepare("minimal", "eth0"));
        assert_eq!(fixture.text(), custom);
    }

    #[test]
    fn verified_managed_profiles_switch_in_both_directions() {
        let fixture = ConkyFixture::new();
        assert!(fixture.prepare("balanced", "wlan0"));
        assert!(fixture.prepare("minimal", "eth0"));
        assert_eq!(fixture.text(), include_str!("../config/conky/minimal.conf"));
        assert!(fixture.prepare("balanced", "eth0"));
        assert!(fixture.text().contains("${downspeedgraph eth0"));
    }

    #[test]
    fn legacy_recognition_requires_one_consistent_safe_interface() {
        assert!(matches_conky_template(
            &RC4_BALANCED.replace("@@INTERFACE@@", "enp1s0.2"),
            RC4_BALANCED
        ));
        assert!(!matches_conky_template(
            &RC4_BALANCED
                .replacen("@@INTERFACE@@", "wlan0", 1)
                .replace("@@INTERFACE@@", "eth0"),
            RC4_BALANCED
        ));
        assert!(!matches_conky_template(
            &RC4_BALANCED.replace("@@INTERFACE@@", "wlan0;touch /tmp/x"),
            RC4_BALANCED
        ));
    }

    #[test]
    fn custom_conky_symlink_is_preserved() {
        let fixture = ConkyFixture::new();
        let target = fixture.0.join("personal.conf");
        fs::write(&target, include_str!("../config/conky/minimal.conf")).unwrap();
        std::os::unix::fs::symlink(&target, fixture.0.join("conky.conf")).unwrap();
        assert!(!fixture.prepare("balanced", "eth0"));
        assert!(fs::symlink_metadata(fixture.0.join("conky.conf"))
            .unwrap()
            .file_type()
            .is_symlink());
        assert_eq!(
            fs::read_to_string(target).unwrap(),
            include_str!("../config/conky/minimal.conf")
        );
    }
}
