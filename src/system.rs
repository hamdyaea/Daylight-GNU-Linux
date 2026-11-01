// Developer: Hamdy Abou El Anein
// Contact: contact@daylightlinux.ch
// Copyright (C) 2026 Hamdy Abou El Anein
// SPDX-License-Identifier: GPL-3.0-only
use std::{fs, path::Path};
#[derive(Debug, Default)]
pub struct Snapshot {
    pub base: String,
    pub kernel: String,
    pub model: String,
    pub arch: String,
    pub memory_used_kib: u64,
    pub memory_total_kib: u64,
    pub uptime_secs: u64,
    pub interface: String,
    pub temperature_c: Option<f64>,
    pub cpu: String,
}
pub fn read(path: &str) -> String {
    fs::read_to_string(path)
        .unwrap_or_default()
        .trim_matches('\0')
        .trim()
        .to_owned()
}
pub fn os_name(text: &str) -> String {
    text.lines()
        .find_map(|l| l.strip_prefix("PRETTY_NAME="))
        .unwrap_or("Linux")
        .trim_matches('"')
        .trim_matches('\'')
        .to_owned()
}
pub fn memory(text: &str) -> (u64, u64) {
    let get = |key: &str| {
        text.lines()
            .find_map(|line| line.strip_prefix(key))
            .and_then(|s| s.split_whitespace().next())
            .and_then(|s| s.parse::<u64>().ok())
            .unwrap_or(0)
    };
    let total = get("MemTotal:");
    let available = if text.lines().any(|l| l.starts_with("MemAvailable:")) {
        get("MemAvailable:")
    } else {
        get("MemFree:")
            .saturating_add(get("Buffers:"))
            .saturating_add(get("Cached:"))
    };
    (total.saturating_sub(available.min(total)), total)
}
pub fn default_interface(routes: &str) -> String {
    let mut candidates: Vec<(u32, &str)> = routes
        .lines()
        .skip(1)
        .filter_map(|l| {
            let f: Vec<&str> = l.split_whitespace().collect();
            if f.len() > 7
                && f[1] == "00000000"
                && u32::from_str_radix(f[3], 16).unwrap_or(0) & 1 != 0
            {
                Some((f[6].parse().unwrap_or(u32::MAX), f[0]))
            } else {
                None
            }
        })
        .collect();
    candidates.sort_by_key(|v| v.0);
    candidates
        .first()
        .map(|v| v.1.to_string())
        .unwrap_or_default()
}
pub fn cpu_times(text: &str) -> Option<(u64, u64)> {
    let mut lines = text.lines();
    let mut fields = lines.next()?.split_whitespace();
    if fields.next()? != "cpu" {
        return None;
    }
    let numbers: Vec<u64> = fields.take(8).filter_map(|s| s.parse().ok()).collect();
    if numbers.len() < 4 {
        return None;
    }
    Some((
        numbers.iter().sum(),
        numbers[3] + numbers.get(4).copied().unwrap_or(0),
    ))
}
pub fn usage(before: (u64, u64), after: (u64, u64)) -> f64 {
    let total = after.0.saturating_sub(before.0);
    let idle = after.1.saturating_sub(before.1).min(total);
    if total == 0 {
        0.0
    } else {
        100.0 * (total - idle) as f64 / total as f64
    }
}
pub fn snapshot() -> Snapshot {
    let (memory_used_kib, memory_total_kib) = memory(&read("/proc/meminfo"));
    let mut model = read("/proc/device-tree/model");
    if model.is_empty() {
        model = read("/sys/class/dmi/id/product_name");
    }
    if model.is_empty() {
        model = "Generic Linux computer".to_owned();
    }
    let cpuinfo = read("/proc/cpuinfo");
    let cpu = cpuinfo
        .lines()
        .find_map(|l| {
            l.strip_prefix("model name")
                .or_else(|| l.strip_prefix("Hardware"))
        })
        .map(|v| v.trim_start_matches([' ', '\t', ':']).to_owned())
        .unwrap_or_else(|| std::env::consts::ARCH.to_owned());
    let mut interface = default_interface(&read("/proc/net/route"));
    if interface.is_empty() {
        if let Ok(entries) = fs::read_dir("/sys/class/net") {
            let mut names: Vec<String> = entries
                .flatten()
                .map(|p| p.file_name().to_string_lossy().into_owned())
                .filter(|n| {
                    n != "lo"
                        && !n.starts_with("veth")
                        && !n.starts_with("docker")
                        && !n.starts_with("br-")
                        && read(&format!("/sys/class/net/{n}/operstate")) == "up"
                })
                .collect();
            names.sort();
            interface = names.into_iter().next().unwrap_or_default();
        }
    }
    let temperature_c = fs::read_dir("/sys/class/thermal").ok().and_then(|entries| {
        entries
            .flatten()
            .filter(|p| p.file_name().to_string_lossy().starts_with("thermal_zone"))
            .find_map(|p| {
                fs::read_to_string(p.path().join("temp"))
                    .ok()?
                    .trim()
                    .parse::<f64>()
                    .ok()
                    .map(|n| n / 1000.0)
            })
    });
    Snapshot {
        base: os_name(&read("/etc/os-release")),
        kernel: read("/proc/sys/kernel/osrelease"),
        model,
        arch: std::env::consts::ARCH.to_owned(),
        memory_used_kib,
        memory_total_kib,
        uptime_secs: read("/proc/uptime")
            .split_whitespace()
            .next()
            .and_then(|n| n.parse::<f64>().ok())
            .unwrap_or(0.0) as u64,
        interface,
        temperature_c,
        cpu,
    }
}
pub fn json_string(s: &str) -> String {
    let mut out = String::from("\"");
    for c in s.chars() {
        match c {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            c if c < ' ' => out.push_str(&format!("\\u{:04x}", c as u32)),
            c => out.push(c),
        }
    }
    out.push('"');
    out
}
impl Snapshot {
    pub fn json(&self) -> String {
        format!("{{\"daylight_version\":{},\"base\":{},\"kernel\":{},\"architecture\":{},\"model\":{},\"memory_used_kib\":{},\"memory_total_kib\":{},\"uptime_seconds\":{},\"interface\":{},\"temperature_c\":{},\"mode\":{}}}",
        json_string(crate::VERSION),json_string(&self.base),json_string(&self.kernel),json_string(&self.arch),json_string(&self.model),
        self.memory_used_kib,self.memory_total_kib,self.uptime_secs,json_string(&self.interface),
        self.temperature_c.map(|v| format!("{v:.1}")).unwrap_or_else(|| "null".into()),json_string(mode()))
    }
    pub fn text(&self) -> String {
        format!("Daylight GNU/Linux {}\nBase: {}\nArchitecture: {}\nModel: {}\nKernel: {}\nCPU: {}\nMemory: {} / {} MiB\nUptime: {}h {}m\nInterface: {}\nTemperature: {}\nMode: {}\n",crate::VERSION,self.base,self.arch,self.model,self.kernel,self.cpu,self.memory_used_kib/1024,self.memory_total_kib/1024,self.uptime_secs/3600,(self.uptime_secs/60)%60,if self.interface.is_empty(){"not detected"}else{&self.interface},self.temperature_c.map(|v|format!("{v:.1} C")).unwrap_or_else(||"unavailable".into()),mode())
    }
}
pub fn mode() -> &'static str {
    if Path::new("/run/live/medium").exists() {
        "live"
    } else {
        "installed"
    }
}
pub fn local_network() -> String {
    let mut result =
        String::from("Local interface information only. No external request was made.\n");
    if let Ok(entries) = fs::read_dir("/sys/class/net") {
        let mut paths: Vec<_> = entries.flatten().map(|p| p.path()).collect();
        paths.sort();
        for path in paths {
            let name = path.file_name().unwrap_or_default().to_string_lossy();
            let state = fs::read_to_string(path.join("operstate")).unwrap_or_default();
            let rx = fs::read_to_string(path.join("statistics/rx_bytes")).unwrap_or_default();
            let tx = fs::read_to_string(path.join("statistics/tx_bytes")).unwrap_or_default();
            result.push_str(&format!(
                "{name}: {} | received {} bytes | sent {} bytes\n",
                state.trim(),
                rx.trim(),
                tx.trim()
            ));
        }
    }
    result
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn mem_available_not_cached_guess() {
        assert_eq!(
            memory("MemTotal: 1000 kB\nMemAvailable: 400 kB\nMemFree: 20 kB"),
            (600, 1000)
        );
    }
    #[test]
    fn mem_clamps() {
        assert_eq!(memory("MemTotal: 10 kB\nMemAvailable: 20 kB"), (0, 10));
    }
    #[test]
    fn fallback_mem() {
        assert_eq!(
            memory("MemTotal: 1000 kB\nMemFree: 10 kB\nBuffers: 20 kB\nCached: 30 kB"),
            (940, 1000)
        );
    }
    #[test]
    fn quotes() {
        assert_eq!(os_name("PRETTY_NAME=\"Debian 12\"\n"), "Debian 12");
    }
    #[test]
    fn json_escaping() {
        assert_eq!(json_string("a\n\"\\"), "\"a\\n\\\"\\\\\"");
    }
    #[test]
    fn excludes_guest_double_counting() {
        assert_eq!(cpu_times("cpu 10 0 20 40 5 3 2 0 10 0"), Some((80, 45)));
    }
    #[test]
    fn cpu_math() {
        assert_eq!(usage((100, 50), (200, 75)), 75.0);
        assert_eq!(usage((100, 50), (100, 50)), 0.0);
    }
    #[test]
    fn lowest_metric() {
        assert_eq!(default_interface("Iface Destination Gateway Flags RefCnt Use Metric Mask\nwlan0 00000000 a 0003 0 0 600 0\neth0 00000000 a 0003 0 0 100 0"),"eth0");
    }
}
