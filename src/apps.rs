// Developer: Hamdy Abou El Anein
// Contact: contact@daylightlinux.ch
// Copyright (C) 2026 Hamdy Abou El Anein
// SPDX-License-Identifier: GPL-3.0-only
use crate::{entropy, Result};
use std::time::{SystemTime, UNIX_EPOCH};
pub const ALPHABET: &[u8] =
    b"ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789!@#$%^&*()-_=+";
pub fn password(length: usize) -> Result<String> {
    if !(8..=4096).contains(&length) {
        return Err("Password length must be between 8 and 4096".into());
    }
    let mut output = String::with_capacity(length);
    for _ in 0..length {
        output.push(ALPHABET[entropy::uniform(ALPHABET.len() as u32)? as usize] as char);
    }
    Ok(output)
}
pub fn temperature(value: f64, unit: &str) -> Result<(f64, f64, f64)> {
    if !value.is_finite() {
        return Err("Temperature must be finite".into());
    }
    let c = match unit.to_ascii_uppercase().as_str() {
        "C" => value,
        "F" => (value - 32.0) * 5.0 / 9.0,
        "K" => value - 273.15,
        _ => return Err("Unit must be C, F or K".into()),
    };
    if c < -273.150000001 {
        return Err("Temperature is below absolute zero".into());
    }
    Ok((c, c * 9.0 / 5.0 + 32.0, c + 273.15))
}
pub fn date_days(date: &str) -> Result<i64> {
    if date.len() != 10 || !date.is_ascii() || &date[4..5] != "-" || &date[7..8] != "-" {
        return Err("Use YYYY-MM-DD".into());
    }
    let y: i64 = date[..4].parse()?;
    let m: usize = date[5..7].parse()?;
    let d: i64 = date[8..].parse()?;
    if !(1..=9999).contains(&y) || !(1..=12).contains(&m) {
        return Err("Invalid year or month".into());
    }
    let leap = y % 4 == 0 && (y % 100 != 0 || y % 400 == 0);
    let months = [
        31,
        if leap { 29 } else { 28 },
        31,
        30,
        31,
        30,
        31,
        31,
        30,
        31,
        30,
        31,
    ];
    if d < 1 || d > months[m - 1] {
        return Err("Invalid calendar date".into());
    }
    let previous = y - 1;
    Ok(previous * 365 + previous / 4 - previous / 100
        + previous / 400
        + months[..m - 1].iter().sum::<i64>()
        + d
        - 1)
}
pub fn days_between(start: &str, end: Option<&str>) -> Result<i64> {
    let end_days = if let Some(end) = end {
        date_days(end)?
    } else {
        date_days("1970-01-01")?
            + (SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs() / 86400) as i64
    };
    Ok(end_days - date_days(start)?)
}
pub fn dice(sides: u32, count: u32) -> Result<Vec<u32>> {
    if !(2..=1_000_000).contains(&sides) || !(1..=100).contains(&count) {
        return Err("Sides: 2..1000000, count: 1..100".into());
    }
    (0..count)
        .map(|_| Ok(entropy::uniform(sides)? + 1))
        .collect()
}
pub fn draw_unique(max: u32, count: u32) -> Result<Vec<u32>> {
    if count > max || max > 1000 || max == 0 {
        return Err("Invalid draw size".into());
    }
    let mut pool: Vec<u32> = (1..=max).collect();
    for i in 0..count as usize {
        let j = i + entropy::uniform(max - i as u32)? as usize;
        pool.swap(i, j);
    }
    let mut out = pool[..count as usize].to_vec();
    out.sort();
    Ok(out)
}
pub fn rpsls(player: &str) -> Result<String> {
    let names = ["rock", "paper", "scissors", "lizard", "spock"];
    let player = names
        .iter()
        .position(|v| *v == player.to_ascii_lowercase())
        .ok_or("Choose rock, paper, scissors, lizard or spock")?;
    let computer = entropy::uniform(5)? as usize;
    let beats = [[2, 3], [0, 4], [1, 3], [1, 4], [0, 2]];
    let outcome = if player == computer {
        "draw"
    } else if beats[player].contains(&computer) {
        "you win"
    } else {
        "computer wins"
    };
    Ok(format!(
        "You: {} | Computer: {} | {outcome}",
        names[player], names[computer]
    ))
}
pub fn tournament(teams: &[String]) -> Result<String> {
    if teams.len() < 2 || teams.len() > 64 || !teams.len().is_power_of_two() {
        return Err("Provide 2, 4, 8, 16, 32 or 64 teams".into());
    }
    if teams
        .iter()
        .any(|s| s.is_empty() || s.len() > 80 || s.chars().any(char::is_control))
    {
        return Err("Invalid team name".into());
    }
    let mut round = teams.to_vec();
    let mut report = String::from("Entertainment simulation, not a prediction.\n");
    while round.len() > 1 {
        let mut next = Vec::new();
        for pair in round.chunks(2) {
            let win = entropy::uniform(2)? as usize;
            report.push_str(&format!("{} vs {} -> {}\n", pair[0], pair[1], pair[win]));
            next.push(pair[win].clone());
        }
        round = next;
    }
    report.push_str(&format!("Winner: {}\n", round[0]));
    Ok(report)
}
pub fn valid_host(host: &str) -> bool {
    !host.is_empty()
        && host.len() <= 253
        && host.as_bytes()[0].is_ascii_alphanumeric()
        && host
            .bytes()
            .all(|b| b.is_ascii_alphanumeric() || b".:-".contains(&b))
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn passwords() {
        let p = password(64).unwrap();
        assert_eq!(p.len(), 64);
        assert!(p.bytes().all(|b| ALPHABET.contains(&b)));
    }
    #[test]
    fn password_bounds() {
        assert!(password(0).is_err());
        assert!(password(7).is_err());
        assert!(password(4097).is_err());
    }
    #[test]
    fn celsius() {
        assert_eq!(temperature(100.0, "C").unwrap().1, 212.0);
    }
    #[test]
    fn fahrenheit() {
        assert!((temperature(32.0, "F").unwrap().0).abs() < 1e-8);
    }
    #[test]
    fn invalid_temperature() {
        assert!(temperature(-274.0, "C").is_err());
        assert!(temperature(f64::NAN, "C").is_err());
        assert!(temperature(10.0, "X").is_err());
    }
    #[test]
    fn leap_years() {
        assert!(date_days("2000-02-29").is_ok());
        assert!(date_days("1900-02-29").is_err());
        assert!(date_days("2024-02-29").is_ok());
    }
    #[test]
    fn date_validation() {
        for d in [
            "2025-02-29",
            "2026-13-01",
            "2026-01-00",
            "2026-04-31",
            "0000-01-01",
            "not a date",
        ] {
            assert!(date_days(d).is_err());
        }
    }
    #[test]
    fn day_difference() {
        assert_eq!(days_between("2024-02-28", Some("2024-03-01")).unwrap(), 2);
    }
    #[test]
    fn unicode_date_rejected() {
        assert!(date_days("ééééé").is_err());
    }
    #[test]
    fn unique_draw() {
        let r = draw_unique(50, 5).unwrap();
        assert_eq!(r.len(), 5);
        for w in r.windows(2) {
            assert!(w[0] < w[1]);
        }
    }
    #[test]
    fn dice_validation() {
        assert!(dice(1, 1).is_err());
        assert!(dice(6, 101).is_err());
    }
    #[test]
    fn safe_host() {
        assert!(valid_host("example.org"));
        assert!(valid_host("2001:db8::1"));
        for h in ["-f", "a;id", "a\nb", "a b", "$(id)", ""] {
            assert!(!valid_host(h));
        }
    }
}
