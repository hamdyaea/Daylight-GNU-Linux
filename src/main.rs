// Developer: Hamdy Abou El Anein
// Contact: info@daylightlinux.ch
// Copyright (C) 2026 Hamdy Abou El Anein
// SPDX-License-Identifier: GPL-3.0-only
use daylight::{apps, config, entropy, gui, manage, system, Result};
use std::{
    env,
    io::{self, IsTerminal, Write},
    path::Path,
    process::Command,
    thread,
    time::{Duration, Instant},
};
fn help() {
    println!(
        r#"Daylight GNU/Linux {version} - Hamdy Abou El Anein

  daylight info                         ASCII identity + local system information
  daylight status [--json]              Read-only local status
  daylight doctor                       Read-only checks; no repair/restarts
  daylight monitor [--watch] [--json] [--interval SECONDS] [--count N]
  daylight control-center               Native desktop applications (YAD)
  daylight app NAME                     Open an individual graphical application
  daylight password [LENGTH] [COUNT]     Kernel CSPRNG; no storage/network
  daylight temperature VALUE C|F|K       Convert a temperature
  daylight days YYYY-MM-DD [YYYY-MM-DD]  Date difference (today uses UTC)
  daylight connect [--check HOST]        Local interfaces; remote test only on request
  daylight games dice [SIDES] [COUNT]
  daylight games coin|lottery|rpsls [CHOICE]
  daylight games tournament TEAM,TEAM,...
  daylight alarm SECONDS [--notify]     Local, foreground alarm
  daylight settings [get KEY|set KEY VALUE]
  daylight setup-session                Prepare only ~/.config/daylight
  daylight update [--dry-run]            Upgrade only installed Daylight packages
  daylight remove [--dry-run]            Remove Daylight; never autoremove dependencies
  daylight telemetry status|privacy|on|off
  daylight privacy                      Read the boot-counter privacy policy
  daylight sensor                       Local thermal reading
  daylight --version

Desktop applications: info, welcome, password, temperature, days, connect,
dice, coin, lottery, rpsls, cards, tournament, basketball, memory, slots,
guess, speech, alarm. Changes to APT and telemetry require explicit sudo.
Licence: GPL-3.0-only. Contact: info@daylightlinux.ch (activation pending).
"#,
        version = daylight::VERSION
    )
}
fn arg<'a>(args: &'a [String], i: usize, msg: &str) -> Result<&'a str> {
    args.get(i).map(|s| s.as_str()).ok_or_else(|| msg.into())
}
fn info() -> Result<()> {
    if Path::new("/usr/bin/fastfetch").exists()
        && Path::new("/usr/share/daylight/fastfetch/config.jsonc").exists()
        && Command::new("/usr/bin/fastfetch")
            .args(["--config", "/usr/share/daylight/fastfetch/config.jsonc"])
            .status()?
            .success()
    {
        return Ok(());
    }
    let logo = [
        "       \\ | /        ",
        "      -- O --       ",
        "         /\\         ",
        "    /\\  /  \\  /\\    ",
        "   /  \\/    \\/  \\   ",
        "  /______________\\  ",
        "                    ",
        " D A Y L I G H T     ",
    ];
    let snapshot = system::snapshot();
    let text = snapshot.text();
    let lines: Vec<_> = text.lines().collect();
    for i in 0..lines.len().max(logo.len()) {
        println!(
            "{}  {}",
            logo.get(i).unwrap_or(&"                    "),
            lines.get(i).unwrap_or(&"")
        );
    }
    Ok(())
}
fn monitor(args: &[String]) -> Result<()> {
    let mut watch = false;
    let mut json = false;
    let mut interval = 2.0f64;
    let mut count = None;
    let mut i = 0;
    while i < args.len() {
        match args[i].as_str() {
            "--watch" => watch = true,
            "--once" => watch = false,
            "--json" => json = true,
            "--interval" => {
                i += 1;
                interval = arg(args, i, "Missing interval")?.parse()?;
            }
            "--count" => {
                i += 1;
                count = Some(arg(args, i, "Missing count")?.parse::<u32>()?);
            }
            _ => return Err("Unknown monitor option".into()),
        }
        i += 1;
    }
    if !interval.is_finite() || !(0.2..=3600.0).contains(&interval) {
        return Err("Interval must be 0.2..3600 seconds".into());
    }
    if count == Some(0) {
        return Err("Count must be positive".into());
    }
    let mut previous = None;
    let mut iteration = 0;
    loop {
        let start = Instant::now();
        let current = system::cpu_times(&system::read("/proc/stat"));
        let cpu = previous.zip(current).map(|(b, a)| system::usage(b, a));
        previous = current;
        let snapshot = system::snapshot();
        if json {
            let s = snapshot.json();
            println!(
                "{},\"cpu_percent\":{}}}",
                &s[..s.len() - 1],
                cpu.map(|p| format!("{p:.2}"))
                    .unwrap_or_else(|| "null".into())
            );
        } else {
            if watch && io::stdout().is_terminal() {
                print!("\x1b[2J\x1b[H");
            }
            print!("{}", snapshot.text());
            println!(
                "CPU usage: {}",
                cpu.map(|v| format!("{v:.1}%"))
                    .unwrap_or_else(|| "sampling".into())
            );
            io::stdout().flush()?;
        }
        iteration += 1;
        if !watch || count.is_some_and(|c| iteration >= c) {
            break;
        }
        thread::sleep(Duration::from_secs_f64(interval).saturating_sub(start.elapsed()));
    }
    Ok(())
}
fn execute() -> Result<()> {
    let args: Vec<String> = env::args().skip(1).collect();
    let command = args.first().map(|s| s.as_str()).unwrap_or("help");
    let a = &args[1.min(args.len())..];
    match command {
        "help" | "--help" | "-h" => help(),
        "version" | "--version" | "-V" => println!("Daylight GNU/Linux {}", daylight::VERSION),
        "status" => {
            if a.iter().any(|s| s == "--json") {
                println!("{}", system::snapshot().json());
            } else {
                print!("{}", system::snapshot().text());
            }
        }
        "info" => info()?,
        "doctor" => manage::doctor()?,
        "monitor" => monitor(a)?,
        "control-center" => gui::center()?,
        "app" => gui::application(arg(a, 0, "Application name required")?)?,
        "password" => {
            let n = if a.is_empty() { 24 } else { a[0].parse()? };
            let count = if a.len() > 1 { a[1].parse::<u32>()? } else { 1 };
            if !(1..=100).contains(&count) {
                return Err("Count must be 1..100".into());
            }
            for _ in 0..count {
                println!("{}", apps::password(n)?);
            }
        }
        "temperature" => {
            let (c, f, k) = apps::temperature(
                arg(a, 0, "Temperature required")?.parse()?,
                arg(a, 1, "Unit required")?,
            )?;
            println!("{c:.2} C | {f:.2} F | {k:.2} K");
        }
        "days" => println!(
            "{}",
            apps::days_between(
                arg(a, 0, "Start date required")?,
                a.get(1).map(|s| s.as_str())
            )?
        ),
        "connect" => {
            print!("{}", system::local_network());
            if !a.is_empty() {
                if a.first().map(|s| s.as_str()) != Some("--check") {
                    return Err("Use connect --check HOST for an explicit remote test".into());
                }
                let host = arg(a, 1, "Host required")?;
                if !apps::valid_host(host) {
                    return Err("Invalid host".into());
                }
                println!("Explicit network test to {host}");
                if !Command::new("/usr/bin/ping")
                    .args(["-c", "1", "-W", "2", "--", host])
                    .status()?
                    .success()
                {
                    return Err("Host did not answer ICMP (this does not necessarily mean the network is offline)".into());
                }
            }
        }
        "games" => match arg(a, 0, "Choose a game")? {
            "dice" => println!(
                "{:?}",
                apps::dice(
                    a.get(1).map_or(Ok(6), |s| s.parse())?,
                    a.get(2).map_or(Ok(1), |s| s.parse())?
                )?
            ),
            "coin" => println!(
                "{}",
                if entropy::uniform(2)? == 0 {
                    "Heads"
                } else {
                    "Tails"
                }
            ),
            "lottery" => println!(
                "Simulation only. Numbers: {:?}; stars: {:?}",
                apps::draw_unique(50, 5)?,
                apps::draw_unique(12, 2)?
            ),
            "rpsls" => println!(
                "{}",
                apps::rpsls(arg(a, 1, "Choose rock, paper, scissors, lizard or spock")?)?
            ),
            "tournament" => {
                let teams: Vec<_> = arg(a, 1, "Comma-separated teams required")?
                    .split(',')
                    .map(|s| s.trim().to_owned())
                    .collect();
                print!("{}", apps::tournament(&teams)?);
            }
            _ => return Err("Unknown game; use daylight app NAME for the graphical games".into()),
        },
        "alarm" => {
            let s: u64 = arg(a, 0, "Delay in seconds required")?.parse()?;
            if !(1..=86400).contains(&s) {
                return Err("Alarm delay must be 1..86400".into());
            }
            println!("Alarm in {s} seconds. Ctrl+C cancels this foreground alarm.");
            thread::sleep(Duration::from_secs(s));
            println!("\x07Daylight alarm");
            if a.iter().any(|s| s == "--notify") {
                let _ = Command::new("/usr/bin/notify-send")
                    .args(["Daylight Alarm", "Your timer has finished."])
                    .status();
            }
        }
        "settings" => match a.first().map(|s| s.as_str()) {
            None => {
                for (k, v) in config::load()? {
                    println!("{k}={v}");
                }
            }
            Some("get") => {
                let data = config::load()?;
                let k = arg(a, 1, "Setting required")?;
                println!("{}", data.get(k).ok_or("Unknown setting")?);
            }
            Some("set") => {
                config::set(arg(a, 1, "Setting required")?, arg(a, 2, "Value required")?)?
            }
            _ => return Err("Use settings [get KEY|set KEY VALUE]".into()),
        },
        "setup-session" => config::setup_session()?,
        "update" | "remove" => {
            if a.iter().any(|s| s != "--dry-run") {
                return Err(
                    "Only --dry-run is supported; APT confirmation is never bypassed".into(),
                );
            }
            manage::packages(command, a.iter().any(|s| s == "--dry-run"))?;
        }
        "telemetry" => manage::telemetry(a.first().map(|s| s.as_str()).unwrap_or("status"))?,
        "privacy" => print!("{}", daylight::PRIVACY),
        "sensor" => {
            if let Some(t) = system::snapshot().temperature_c {
                println!("{t:.1} C");
            } else {
                println!("unavailable");
            }
        }
        _ => return Err(format!("Unknown command: {command}. Run daylight --help").into()),
    }
    Ok(())
}
fn main() {
    if let Err(e) = execute() {
        eprintln!("daylight: {e}");
        std::process::exit(2);
    }
}
