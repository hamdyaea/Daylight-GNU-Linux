// Developer: Hamdy Abou El Anein
// Contact: contact@daylightlinux.ch
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
        "dice" => {
            if let Some(input) = ask("Number of sides and rolls, for example: 6 2", "6 2")? {
                let f: Vec<_> = input.split_whitespace().collect();
                if f.len() != 2 {
                    return Err("Enter SIDES COUNT".into());
                }
                show(
                    "Daylight Dice",
                    &format!("{:?}", apps::dice(f[0].parse()?, f[1].parse()?)?),
                )?;
            }
        }
        "coin" => show(
            "Daylight Coin",
            if entropy::uniform(2)? == 0 {
                "Heads"
            } else {
                "Tails"
            },
        )?,
        "lottery" => show(
            "Daylight Lottery Simulator",
            &format!(
                "Entertainment only; no prediction or money.\n\nNumbers: {:?}\nStars: {:?}",
                apps::draw_unique(50, 5)?,
                apps::draw_unique(12, 2)?
            ),
        )?,
        "rpsls" => {
            if let Some(choice) = ask("Choose rock, paper, scissors, lizard or spock", "rock")? {
                show("Daylight RPSLS", &apps::rpsls(&choice)?)?;
            }
        }
        "cards" => {
            let cards = apps::draw_unique(52, 2)?;
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
        "basketball" => {
            let a = 70 + entropy::uniform(71)?;
            let mut b = 70 + entropy::uniform(71)?;
            while a == b {
                b = 70 + entropy::uniform(71)?;
            }
            show(
                "Daylight Basketball",
                &format!("Fictional match, not a prediction.\nTeam A: {a}\nTeam B: {b}"),
            )?;
        }
        "slots" => {
            let symbols = ["SUN", "MOUNTAIN", "STAR", "MOON"];
            let a = entropy::uniform(4)? as usize;
            let b = entropy::uniform(4)? as usize;
            let c = entropy::uniform(4)? as usize;
            show(
                "Daylight Slot Simulator",
                &format!(
                    "No bets, no money.\n\n{} | {} | {}\n\n{}",
                    symbols[a],
                    symbols[b],
                    symbols[c],
                    if a == b && b == c {
                        "Three matching symbols!"
                    } else {
                        "Try again from the menu."
                    }
                ),
            )?;
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
        "memory" => {
            let mut deck = [1u32, 1, 2, 2, 3, 3, 4, 4];
            for i in (1..deck.len()).rev() {
                let j = entropy::uniform((i + 1) as u32)? as usize;
                deck.swap(i, j);
            }
            let mut solved = [false; 8];
            let mut attempts = 0;
            while solved.iter().any(|s| !*s) {
                let board = (0..8)
                    .map(|i| {
                        format!(
                            "{}:[{}]",
                            i + 1,
                            if solved[i] {
                                deck[i].to_string()
                            } else {
                                "?".into()
                            }
                        )
                    })
                    .collect::<Vec<_>>()
                    .join("  ");
                let Some(input) = ask(
                    &format!("{board}\nChoose two hidden positions, for example 1 2"),
                    "1 2",
                )?
                else {
                    break;
                };
                let nums: Vec<_> = input
                    .split_whitespace()
                    .filter_map(|n| n.parse::<usize>().ok())
                    .collect();
                if nums.len() != 2
                    || nums[0] == nums[1]
                    || nums.iter().any(|n| !(1..=8).contains(n) || solved[n - 1])
                {
                    continue;
                }
                let (a, b) = (nums[0] - 1, nums[1] - 1);
                attempts += 1;
                if deck[a] == deck[b] {
                    solved[a] = true;
                    solved[b] = true;
                }
                show(
                    "Daylight Memory",
                    &format!(
                        "Position {}: {}\nPosition {}: {}\n{}",
                        a + 1,
                        deck[a],
                        b + 1,
                        deck[b],
                        if deck[a] == deck[b] {
                            "Match!"
                        } else {
                            "Different cards"
                        }
                    ),
                )?;
            }
            if solved.iter().all(|s| *s) {
                show(
                    "Daylight Memory",
                    &format!("Completed in {attempts} attempts"),
                )?;
            }
        }
        "speech" => {
            if let Some(text) = ask("Text to read locally with eSpeak NG", "")? {
                if text.len() > 4000 {
                    return Err("Text is limited to 4000 bytes".into());
                }
                let mut child = Command::new("/usr/bin/espeak-ng")
                    .arg("--stdin")
                    .stdin(Stdio::piped())
                    .spawn()?;
                if let Some(mut stdin) = child.stdin.take() {
                    stdin.write_all(text.as_bytes())?;
                }
                child.wait()?;
            }
        }
        "alarm" => {
            if let Some(input) = ask(
                "Alarm delay in seconds (1..86400). Local notification; no browser.",
                "300",
            )? {
                let seconds: u64 = input.parse()?;
                if !(1..=86400).contains(&seconds) {
                    return Err("Delay must be 1..86400 seconds".into());
                }
                Command::new(std::env::current_exe()?)
                    .args(["alarm", &seconds.to_string(), "--notify"])
                    .stdin(Stdio::null())
                    .stdout(Stdio::null())
                    .stderr(Stdio::null())
                    .spawn()?;
                show("Daylight Alarm",&format!("Alarm set for {seconds} seconds from now. It requires this session to stay running."))?;
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
        "Night wallpaper",
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
            "Night wallpaper" => ("wallpaper", "daylight-night.jpg"),
            "Original wallpaper" => ("wallpaper", "daylight-original.png"),
            _ => return Ok(()),
        };
        config::set(key, value)?;
        if key == "wallpaper" {
            let path = format!("/usr/share/backgrounds/daylight/{value}");
            Command::new("/usr/bin/feh")
                .args(["--no-fehbg", "--bg-fill", &path])
                .status()?;
        }
        show("Daylight Settings","Saved. Profile and monitor changes apply when the Daylight session is restarted; no services were restarted.")?;
    }
    Ok(())
}
