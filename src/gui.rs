// Developer: Hamdy Abou El Anein
// Contact: info@daylightlinux.ch
// Copyright (C) 2026 Hamdy Abou El Anein
// SPDX-License-Identifier: GPL-3.0-only
//! Application logic is Rust; YAD provides native GTK dialogs on demand.
//! There is no webview, resident GUI process, or shell command evaluation.
use crate::{apps, config, entropy, system, Result};
use std::{
    io::Write,
    path::Path,
    process::{Command, Stdio},
};
fn dialog(args: &[&str]) -> Result<Option<String>> {
    let result = Command::new("/usr/bin/yad")
        .args([
            "--title=Daylight GNU/Linux",
            "--window-icon=daylight",
            "--center",
        ])
        .args(args)
        .output()?;
    if result.status.success() {
        Ok(Some(
            String::from_utf8(result.stdout)?
                .trim()
                .trim_end_matches('|')
                .to_string(),
        ))
    } else {
        Ok(None)
    }
}
fn ask(title: &str, default: &str) -> Result<Option<String>> {
    dialog(&[
        "--entry",
        "--width=540",
        "--text",
        title,
        "--entry-text",
        default,
    ])
}
pub fn show(title: &str, text: &str) -> Result<()> {
    let mut child = Command::new("/usr/bin/yad")
        .args([
            "--title",
            title,
            "--window-icon=daylight",
            "--text-info",
            "--wrap",
            "--width=720",
            "--height=420",
            "--button=Close:0",
        ])
        .stdin(Stdio::piped())
        .spawn()?;
    if let Some(mut stdin) = child.stdin.take() {
        let _ = stdin.write_all(text.as_bytes());
    }
    child.wait()?;
    Ok(())
}
fn require_desktop() -> Result<()> {
    if config::effective_uid() == Some(0) {
        return Err("Do not run desktop applications as root".into());
    }
    if !Path::new("/usr/bin/yad").exists() {
        return Err(
            "Install daylight-desktop for native graphical dialogs; CLI tools need no GUI".into(),
        );
    }
    Ok(())
}
pub fn center() -> Result<()> {
    require_desktop()?;
    loop {
        let selected = dialog(&[
            "--list",
            "--width=620",
            "--height=580",
            "--column=Application",
            "--print-column=1",
            "--separator=",
            "--button=Open:0",
            "--button=Close:1",
            "System information",
            "Passwords",
            "Temperature",
            "Days calculator",
            "Connections",
            "Dice",
            "Coin flip",
            "Lottery simulator",
            "Rock paper scissors lizard Spock",
            "Battle cards",
            "Tournament",
            "Basketball",
            "Memory",
            "Slot simulator",
            "Guess the number",
            "Speech",
            "Alarm",
            "Settings",
            "Privacy",
        ])?;
        match selected {
            None => return Ok(()),
            Some(ref s) if s.is_empty() => return Ok(()),
            Some(s) => {
                let result = match s.as_str() {
                    "System information" => application("info"),
                    "Passwords" => application("password"),
                    "Temperature" => application("temperature"),
                    "Days calculator" => application("days"),
                    "Connections" => application("connect"),
                    "Dice" => application("dice"),
                    "Coin flip" => application("coin"),
                    "Lottery simulator" => application("lottery"),
                    "Rock paper scissors lizard Spock" => application("rpsls"),
                    "Battle cards" => application("cards"),
                    "Tournament" => application("tournament"),
                    "Basketball" => application("basketball"),
                    "Memory" => application("memory"),
                    "Slot simulator" => application("slots"),
                    "Guess the number" => application("guess"),
                    "Speech" => application("speech"),
                    "Alarm" => application("alarm"),
                    "Settings" => settings(),
                    "Privacy" => show("Daylight privacy", crate::PRIVACY),
                    _ => Ok(()),
                };
                if let Err(e) = result {
                    show("Daylight - action not completed", &e.to_string())?;
                }
            }
        }
    }
}
pub fn application(name: &str) -> Result<()> {
    require_desktop()?;
    match name {
        "info" | "welcome" => show("Daylight GNU/Linux", &system::snapshot().text())?,
        "password" => {
            if let Some(n) = ask(
                "Password length (8..4096). Generated locally using the kernel CSPRNG.",
                "24",
            )? {
                let value = apps::password(n.parse()?)?;
                // The generated password goes through stdin, never command-line arguments or a temporary file.
                show("Daylight Password Generator", &value)?;
            }
        }
        "temperature" => {
            if let Some(input) = ask("Temperature and unit, for example: 20 C", "20 C")? {
                let fields: Vec<_> = input.split_whitespace().collect();
                if fields.len() != 2 {
                    return Err("Enter a number followed by C, F or K".into());
                }
                let (c, f, k) = apps::temperature(fields[0].parse()?, fields[1])?;
                show(
                    "Daylight Temperature",
                    &format!("{c:.2} C\n{f:.2} F\n{k:.2} K"),
                )?;
            }
        }
        "days" => {
            if let Some(date) = ask(
                "Start date YYYY-MM-DD. Difference to today's UTC date.",
                "2000-01-01",
            )? {
                show(
                    "Daylight Days Calculator",
                    &format!("{} days", apps::days_between(&date, None)?),
                )?;
            }
        }
        "connect" => show(
            "Daylight Connect - local information",
            &system::local_network(),
        )?,
        "dice" | "coin" | "memory" | "slots" | "basketball" | "rpsls" => {
            let script = Path::new("/usr/share/daylight/games")
                .join(name)
                .join("game.py");
            if !Command::new("/usr/bin/python3")
                .arg(script)
                .status()?
                .success()
            {
                show("Daylight Games", "The game could not start.")?;
            }
        }
        "lottery" => show(
            "Daylight Lottery Simulator",
            &format!(
                "Entertainment only; no prediction or money.\n\nNumbers: {:?}\nStars: {:?}",
                apps::draw_unique(50, 5)?,
                apps::draw_unique(12, 2)?
            ),
        )?,
        "cards" => {
            let mut cards = apps::draw_unique(52, 2)?;
            // draw_unique sorts its result; randomly assign the two cards to players.
            if entropy::uniform(2)? == 1 {
                cards.swap(0, 1);
            }
            let a = (cards[0] - 1) % 13 + 2;
            let b = (cards[1] - 1) % 13 + 2;
            show(
                "Daylight Battle Cards",
                &format!(
                    "Your rank: {a}\nComputer rank: {b}\n{}",
                    if a > b {
                        "You win"
                    } else if a < b {
                        "Computer wins"
                    } else {
                        "Draw"
                    }
                ),
            )?;
        }
        "tournament" => {
            if let Some(input) = ask(
                "2, 4, 8, 16, 32 or 64 teams separated by commas. Fictional simulation.",
                "Team A,Team B,Team C,Team D",
            )? {
                let teams: Vec<String> = input.split(',').map(|s| s.trim().to_string()).collect();
                show("Daylight Tournament", &apps::tournament(&teams)?)?;
            }
        }
        "guess" => {
            let target = 1 + entropy::uniform(100)?;
            let mut hint = "Guess a number from 1 to 100".to_string();
            while let Some(s) = ask(&hint, "50")? {
                let n: u32 = match s.parse() {
                    Ok(n) if (1..=100).contains(&n) => n,
                    _ => {
                        hint = "Enter an integer from 1 to 100".into();
                        continue;
                    }
                };
                if n == target {
                    show("Daylight Guess", "Correct!")?;
                    break;
                }
                hint = if n < target { "Higher" } else { "Lower" }.into();
            }
        }
        "speech" => {
            let helper = Path::new("/usr/lib/daylight/speech");
            if !helper.exists() {
                return show(
                    "Daylight Text to Speech",
                    "Install the daylight-apps package to use Text to Speech.",
                );
            }
            if !Command::new(helper).status()?.success() {
                show(
                    "Daylight Text to Speech",
                    "The speech window could not start.",
                )?;
            }
        }
        "alarm" => {
            if let Some(input) = ask(
                "Alarm delay in seconds (1..86400). Keep the countdown open; Cancel stops it.",
                "300",
            )? {
                let seconds: u64 = input.parse()?;
                if !(1..=86400).contains(&seconds) {
                    return Err("Delay must be 1..86400 seconds".into());
                }
                let status = Command::new("/usr/bin/yad")
                    .args([
                        "--title=Daylight Alarm",
                        "--window-icon=daylight",
                        "--center",
                        "--width=480",
                        "--text=Your local timer is running. Keep this session open.",
                        "--timeout",
                        &seconds.to_string(),
                        "--timeout-indicator=top",
                        "--button=Cancel:1",
                    ])
                    .status()?;
                // YAD returns 70 on timeout. Closing or cancelling must not ring.
                if status.code() == Some(70) {
                    show("Daylight Alarm", "Your timer has finished.")?;
                }
            }
        }
        _ => return Err("Unknown application".into()),
    }
    Ok(())
}
fn settings() -> Result<()> {
    let values = config::load()?;
    let text=format!("Monitor: {} | Terminal information: {} | Profile: {}\nChanges affect this user's Daylight session only.",values["monitor"],values["fetch"],values["profile"]);
    if let Some(choice) = dialog(&[
        "--list",
        "--text",
        &text,
        "--column=Setting",
        "--print-column=1",
        "--separator=",
        "--width=650",
        "--height=420",
        "--button=Apply:0",
        "--button=Cancel:1",
        "Monitor on",
        "Monitor off",
        "Terminal information on",
        "Terminal information off",
        "Minimal profile",
        "Balanced profile",
        "Mountains wallpaper",
        "Dark photographic wallpaper",
        "Sunrise wallpaper",
        "Himalayan wallpaper",
        "Original wallpaper",
    ])? {
        let (key, value) = match choice.as_str() {
            "Monitor on" => ("monitor", "on"),
            "Monitor off" => ("monitor", "off"),
            "Terminal information on" => ("fetch", "on"),
            "Terminal information off" => ("fetch", "off"),
            "Minimal profile" => ("profile", "minimal"),
            "Balanced profile" => ("profile", "balanced"),
            "Mountains wallpaper" => ("wallpaper", "daylight-mountains.jpg"),
            "Dark photographic wallpaper" => ("wallpaper", "daylight-night.jpg"),
            "Sunrise wallpaper" => ("wallpaper", "daylight-sunrise.jpg"),
            "Himalayan wallpaper" => ("wallpaper", "daylight-himalaya.jpg"),
            "Original wallpaper" => ("wallpaper", "daylight-original.png"),
            _ => return Ok(()),
        };
        config::set(key, value)?;
        if key == "wallpaper" {
            let path = format!("/usr/share/backgrounds/daylight/{value}");
            Command::new("/usr/bin/feh")
                .args(["--no-fehbg", "--bg-max", &path])
                .status()?;
        }
        show("Daylight Settings","Saved. Profile and monitor changes apply when the Daylight session is restarted; no services were restarted.")?;
    }
    Ok(())
}
