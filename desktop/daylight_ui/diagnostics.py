"""Local, read-only Linux measurements for the Daylight desktop.

No hostname, certificate, personal file or remote endpoint is queried. All optional
commands have a short timeout and are launched as an argument vector, never a shell.
Copyright (C) 2026 Hamdy Abou El Anein. SPDX-License-Identifier: GPL-3.0-only
"""
from __future__ import annotations

import json
import math
import platform
from pathlib import Path
import re
import shutil
import subprocess


def read_text(path):
    try:
        with Path(path).open(errors="replace") as stream:
            return stream.read(131072).strip().strip("\x00")
    except (OSError, ValueError):
        return ""


def command(arguments, timeout=1.5):
    """Return a bounded local command result, or None when unsupported."""
    executable = shutil.which(arguments[0])
    if not executable:
        return None
    try:
        result = subprocess.run([executable, *arguments[1:]], capture_output=True,
                                text=True, timeout=timeout, check=False)
        return result.stdout[:131072].strip() if result.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def memory_values(content):
    values = {}
    for line in content.splitlines():
        try:
            key, rest = line.split(":", 1)
            values[key] = max(0, int(rest.split()[0])) * 1024
        except (ValueError, IndexError):
            continue
    total = values.get("MemTotal", 0)
    available = values.get("MemAvailable", values.get("MemFree", 0) +
                           values.get("Buffers", 0) + values.get("Cached", 0))
    return total, total - min(total, available)


def cpu_times(content):
    fields = content.splitlines()[0].split() if content else []
    if not fields or fields[0] != "cpu" or len(fields) < 5:
        return None
    try:
        # Guest times are already included in user/nice; do not count them twice.
        counters = [int(value) for value in fields[1:9]]
        if any(value < 0 for value in counters):
            return None
        return sum(counters), counters[3] + (counters[4] if len(counters) > 4 else 0)
    except ValueError:
        return None


def cpu_percent(before, after):
    if before is None or after is None or after[0] <= before[0]:
        return None
    total = after[0] - before[0]
    idle = max(0, min(total, after[1] - before[1]))
    return 100.0 * (total - idle) / total


def throttle_status(content):
    """Decode Raspberry Pi firmware current bits separately from sticky history."""
    match = re.fullmatch(r"\s*throttled=(0x[0-9a-fA-F]+)\s*", content or "")
    if not match:
        return None
    value = int(match.group(1), 16)
    names = ("Undervoltage", "Frequency capped", "Thermal/power throttling", "Soft temperature limit")
    return {"raw": value,
            "current": [name for bit, name in enumerate(names) if value & (1 << bit)],
            "history": [name for bit, name in enumerate(names) if value & (1 << (bit + 16))]}


def thermal_reading(root=Path("/sys/class/thermal")):
    measurements = []
    for zone in sorted(root.glob("thermal_zone*")):
        try:
            value = float(read_text(zone / "temp")) / 1000
            kind = read_text(zone / "type")
            if math.isfinite(value) and -40 <= value <= 150:
                measurements.append((kind, value))
        except ValueError:
            continue
    preferred = next((value for kind, value in measurements
                      if any(token in kind.lower() for token in ("cpu", "soc", "package"))), None)
    return preferred if preferred is not None else (measurements[0][1] if measurements else None)


def network_info():
    """Read addresses/routes from iproute2, with sysfs-only fallback."""
    interfaces = []
    raw = command(["ip", "-j", "address", "show"])
    try:
        entries = json.loads(raw) if raw else []
        for item in entries:
            interfaces.append({"name": item.get("ifname", "?"),
                               "state": item.get("operstate", "UNKNOWN"),
                               "addresses": [f"{a['local']}/{a.get('prefixlen', '')}"
                                             for a in item.get("addr_info", []) if "local" in a]})
    except (ValueError, TypeError, KeyError):
        interfaces = []
    if not interfaces:
        for path in sorted(Path("/sys/class/net").glob("*")):
            interfaces.append({"name": path.name, "state": read_text(path / "operstate").upper(),
                               "addresses": []})
    gateways = []
    for family in ("-4", "-6"):
        raw = command(["ip", family, "-j", "route", "show", "default"])
        try:
            for item in json.loads(raw) if raw else []:
                gateways.append({"gateway": item.get("gateway", "on-link"), "dev": item.get("dev", "?")})
        except (ValueError, TypeError):
            pass
    return {"interfaces": interfaces, "gateways": gateways,
            "addresses_supported": bool(shutil.which("ip"))}


def snapshot():
    total, used = memory_values(read_text("/proc/meminfo"))
    model = (read_text("/proc/device-tree/model") or read_text("/sys/class/dmi/id/product_name")
             or "Linux computer")
    is_pi = "raspberry pi" in model.lower()
    try:
        disk = shutil.disk_usage("/")
        storage = {"total": disk.total, "used": disk.used, "free": disk.free}
    except OSError:
        storage = None
    try:
        uptime = max(0, int(float(read_text("/proc/uptime").split()[0])))
    except (ValueError, IndexError, OverflowError):
        uptime = 0
    os_name = platform.system()
    for line in read_text("/etc/os-release").splitlines():
        if line.startswith("PRETTY_NAME="):
            os_name = line.split("=", 1)[1].strip('"\'')
    return {"model": model, "is_pi": is_pi, "system": os_name,
            "kernel": platform.release(), "architecture": platform.machine(),
            "memory_total": total, "memory_used": used, "cpu_times": cpu_times(read_text("/proc/stat")),
            "temperature": thermal_reading(), "storage": storage, "uptime": uptime,
            "power": throttle_status(command(["vcgencmd", "get_throttled"])) if is_pi else None}


def doctor_checks():
    checks = []
    for title, executable, help_text in [
        ("Desktop session", "fluxbox", "Install daylight-desktop for the Daylight session."),
        ("Desktop monitor", "conky", "Install the Conky package provided by your distribution."),
        ("Text to speech", "espeak-ng", "Install espeak-ng to use local speech."),
        ("Network addresses", "ip", "Install iproute2 to display addresses and gateways."),
        ("File manager", "pcmanfm", "Install PCManFM or choose an installed file manager."),
    ]:
        available = bool(shutil.which(executable))
        checks.append({"name": title, "ok": available,
                       "detail": "Available" if available else help_text})
    data = snapshot()
    if data["storage"]:
        disk = data["storage"]
        ok = disk["free"] / max(1, disk["total"]) >= 0.05
        checks.append({"name": "Root filesystem", "ok": ok,
                       "detail": f"{disk['free'] / 2**30:.1f} GiB free" +
                       ("" if ok else " · Less than 5% free. Review large files before installing updates.")})
    if data["is_pi"]:
        power = data["power"]
        checks.append({"name": "Raspberry Pi power and temperature", "ok": power is not None and not power["current"],
                       "detail": ("; ".join(power["current"]) if power and power["current"] else
                                  "No current firmware warning" if power is not None else
                                  "Firmware reading unavailable. Check vcgencmd installation and permissions.")})
    return checks
