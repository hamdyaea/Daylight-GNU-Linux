"""Small, atomic user preferences; no executable configuration.

SPDX-License-Identifier: GPL-3.0-only
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

DEFAULTS = {
    "language": "en", "appearance": "light", "text_scale": 1.0,
    "welcome_completed": False, "custom_wallpaper": "", "wallpaper_mode": "fixed",
    "latitude": 46.8065, "longitude": 7.1619, "timezone": "Europe/Zurich",
    "location_name": "Fribourg", "favorites": [],
    "keyboard_layout": "", "keyboard_variant": "",
}
CORE_DEFAULTS = {"monitor": "on", "fetch": "on", "profile": "balanced",
                 "wallpaper": "daylight-mountains.jpg"}
WALLPAPERS = ("daylight-mountains.jpg", "daylight-night.jpg", "daylight-sunrise.jpg",
              "daylight-himalaya.jpg", "daylight-original.png")
KEYBOARDS = (("", ""), ("ch", "fr"), ("ch", ""), ("fr", ""), ("us", ""))


def valid_keyboard(layout, variant) -> bool:
    return (layout, variant) in KEYBOARDS


def apply_keyboard(values: dict) -> bool:
    """Apply only an explicit supported choice to the current X11 session."""
    layout, variant = values.get("keyboard_layout", ""), values.get("keyboard_variant", "")
    if not layout or not valid_keyboard(layout, variant):
        return False
    executable = shutil.which("setxkbmap")
    if not executable:
        return False
    try:
        result = subprocess.run([executable, "-layout", layout, "-variant", variant],
                                capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def directory() -> Path:
    path = Path(os.environ.get("XDG_CONFIG_HOME", ""))
    if not path.is_absolute():
        path = Path.home() / ".config"
    return path / "daylight"


def atomic(path: Path, content: str) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".daylight-ui-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def load_ui() -> dict:
    values = dict(DEFAULTS)
    try:
        content = json.loads((directory() / "ui.json").read_text(encoding="utf-8"))
        if isinstance(content, dict):
            values.update({key: value for key, value in content.items() if key in DEFAULTS})
    except (OSError, ValueError, TypeError):
        pass
    if values["language"] not in ("en", "fr", "de"):
        values["language"] = "en"
    if values["appearance"] not in ("light", "dark", "automatic"):
        values["appearance"] = "light"
    if values["wallpaper_mode"] not in ("fixed", "daylight"):
        values["wallpaper_mode"] = "fixed"
    try:
        values["text_scale"] = min(1.5, max(.85, float(values["text_scale"])))
    except (ValueError, TypeError):
        values["text_scale"] = 1.0
    if not isinstance(values["favorites"], list):
        values["favorites"] = []
    values["favorites"] = [entry for entry in values["favorites"][:1000] if isinstance(entry, str)]
    values["welcome_completed"] = values["welcome_completed"] is True
    if not isinstance(values["custom_wallpaper"], str):
        values["custom_wallpaper"] = ""
    if not valid_keyboard(values["keyboard_layout"], values["keyboard_variant"]):
        values["keyboard_layout"], values["keyboard_variant"] = "", ""
    return values


def save_ui(changes: dict) -> dict:
    values = load_ui()
    values.update({key: value for key, value in changes.items() if key in DEFAULTS})
    if not valid_keyboard(values["keyboard_layout"], values["keyboard_variant"]):
        raise ValueError("Unsupported keyboard layout or variant")
    atomic(directory() / "ui.json", json.dumps(values, ensure_ascii=False, indent=2) + "\n")
    return values


def read_core() -> dict:
    values = dict(CORE_DEFAULTS)
    try:
        for line in (directory() / "settings.conf").read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                key, value = (x.strip() for x in line.split("=", 1))
                if key in values:
                    values[key] = value
    except OSError:
        pass
    return values


def save_core(changes: dict) -> dict:
    allowed = {"monitor": ("on", "off"), "fetch": ("on", "off"),
               "profile": ("minimal", "balanced"), "wallpaper": WALLPAPERS}
    if any(key not in allowed or value not in allowed[key] for key, value in changes.items()):
        raise ValueError("Unsupported Daylight preference")
    # Preserve valid unknown keys written by a newer Daylight release.
    path = directory() / "settings.conf"
    try:
        original = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        original = []
    lines, written = [], set()
    for line in original:
        key = line.split("=", 1)[0].strip() if "=" in line else ""
        if key in changes:
            if key not in written:
                lines.append(f"{key}={changes[key]}")
                written.add(key)
        else:
            lines.append(line)
    for key, value in changes.items():
        if key not in written:
            lines.append(f"{key}={value}")
    atomic(path, "\n".join(lines) + "\n")
    return read_core()
