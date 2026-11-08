// Developer: Hamdy Abou El Anein
// Contact: info@daylightlinux.ch
// Copyright (C) 2026 Hamdy Abou El Anein
// SPDX-License-Identifier: GPL-3.0-only
pub mod apps;
pub mod config;
pub mod entropy;
pub mod gui;
pub mod system;
pub const VERSION: &str = env!("CARGO_PKG_VERSION");
pub type Result<T> = std::result::Result<T, Box<dyn std::error::Error>>;
pub mod manage;
pub const PRIVACY: &str = "Daylight works offline. No network request is made by opening a terminal.\nBoot statistics are OFF by default and require the optional telemetry package plus explicit activation.\nThe optional event contains only event=boot, Daylight version and live/installed mode.\nThere is no installation ID, hostname, MAC address, serial number or user identifier.\nCloudflare processes transport metadata including the source IP; the collector stores daily aggregates only, so network anonymity is not promised.\nEvents count received boots, NOT unique users. No exact user count can be derived without linkability.\nDisable with: sudo daylight telemetry off\n";
