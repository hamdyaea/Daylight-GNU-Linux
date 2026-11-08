"""Small, atomic user preferences; no executable configuration.

SPDX-License-Identifier: GPL-3.0-only
"""
from __future__ import annotations

import json
import fcntl
import hashlib
import stat
import sys
import os
from pathlib import Path
import re
import shutil
import select
import signal
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
MANAGER_REVISION = "2026-11-conky-preservation-1"
MANAGER_REVISION_KEY = "DAYLIGHT_APPEARANCE_REVISION"
INSTALLED_GUI = "/usr/share/daylight/ui/daylight_gui.py"


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


def daylight_session(environ=None, uid=None) -> bool:
    """Session helpers never bootstrap from another desktop or as root."""
    environ = os.environ if environ is None else environ
    uid = os.geteuid() if uid is None else uid
    return (uid != 0 and environ.get("DAYLIGHT_SESSION") == "1"
            and bool(environ.get("DISPLAY") or environ.get("WAYLAND_DISPLAY")))


def session_kind(environ=None) -> str:
    environ = os.environ if environ is None else environ
    return "wayland" if environ.get("XDG_SESSION_TYPE") == "wayland" else "x11"


def session_lock_path(environ=None) -> Path:
    environ = os.environ if environ is None else environ
    runtime = Path(environ.get("XDG_RUNTIME_DIR", ""))
    try:
        info = runtime.stat()
        if not runtime.is_absolute() or info.st_uid != os.getuid() or info.st_mode & 0o022:
            raise OSError("Untrusted runtime directory")
    except OSError:
        runtime = directory() / "runtime"
        runtime.mkdir(mode=0o700, parents=True, exist_ok=True)
        info = runtime.stat()
        if info.st_uid != os.getuid() or info.st_mode & 0o022:
            raise OSError("Untrusted Daylight runtime directory")
    kind = session_kind(environ)
    display = environ.get("WAYLAND_DISPLAY" if kind == "wayland" else "DISPLAY", "")
    key = hashlib.sha256((kind + "\0" + display).encode()).hexdigest()[:20]
    return runtime / ("daylight-appearance-" + key + ".lock")


def acquire_session_lock(environ=None):
    """Return a held file descriptor, or None when this display is managed."""
    path = session_lock_path(environ)
    descriptor = os.open(path, os.O_CREAT | os.O_RDWR | os.O_CLOEXEC | os.O_NOFOLLOW, 0o600)
    try:
        info = os.fstat(descriptor)
        if info.st_uid != os.getuid() or not stat.S_ISREG(info.st_mode):
            raise OSError("Untrusted Daylight lock")
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return descriptor
    except BlockingIOError:
        os.close(descriptor)
        return None
    except BaseException:
        os.close(descriptor)
        raise


def ensure_session_manager(entry=None) -> bool:
    """Opening an RC4 UI also upgrades the behaviour of a running RC3 session."""
    if not daylight_session():
        return False
    try:
        descriptor = acquire_session_lock()
        if descriptor is None:
            # RC4's already-running helper cannot load the fixed source on
            # disk. Retire only a pinned, obsolete helper from this display.
            if not retire_stale_managers():
                return False
            descriptor = acquire_session_lock()
            if descriptor is None:
                return False
        # The child takes the authoritative lock before touching any process.
        # Concurrent UI launches can create short-lived candidates; only one
        # candidate can own the session, its Conky, or its background process.
        os.close(descriptor)
        entry = Path(entry) if entry is not None else Path(__file__).resolve().parent.parent / "daylight_gui.py"
        subprocess.Popen([sys.executable, str(entry), "--session-appearance"],
                         env=dict(os.environ, **{MANAGER_REVISION_KEY: MANAGER_REVISION}),
                         stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, start_new_session=True, close_fds=True)
        return True
    except OSError:
        return False


def mark_manager_revision(entry):
    """An exec makes the revision visible in /proc's initial environment."""
    if daylight_session() and os.environ.get(MANAGER_REVISION_KEY) != MANAGER_REVISION:
        environment = dict(os.environ, **{MANAGER_REVISION_KEY: MANAGER_REVISION})
        os.execve(sys.executable, [sys.executable, str(entry), "--session-appearance"], environment)


def start_conky(wayland=False):
    """Launch the renderer wrapper with a separate generated main configuration.

    The installed Wayland Lua wrapper reads DAYLIGHT_CONKY_CONFIG with dofile.
    Pointing that variable at the wrapper itself would recurse indefinitely.
    """
    main_config = directory() / "conky.conf"
    launch_config = Path("/usr/share/daylight/ui/conky-wayland.lua") if wayland else main_config
    environment = dict(os.environ, DAYLIGHT_CONKY_CONFIG=str(main_config))
    return subprocess.Popen(["conky", "-c", str(launch_config)], env=environment,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def x11_display_alive() -> bool:
    """A successful xprop invocation alone does not prove a WM is present."""
    executable = shutil.which("xprop")
    if not executable:
        return False
    try:
        result = subprocess.run([executable, "-root", "_NET_SUPPORTING_WM_CHECK"],
                                capture_output=True, text=True, timeout=3)
        if result.returncode:
            return False
        match = re.search(r"^_NET_SUPPORTING_WM_CHECK\(WINDOW\):\s*window id\s*#\s*(0x[0-9a-fA-F]+|[0-9]+)\s*$",
                          result.stdout, re.MULTILINE)
        if not match:
            return False
        value = match.group(1)
        return int(value, 16 if value.startswith("0x") else 10) != 0
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return False


def process_snapshot(path: Path, uid=None):
    """Read just enough /proc identity to qualify a legacy session child."""
    uid = os.getuid() if uid is None else uid
    try:
        if path.stat().st_uid != uid:
            return None
        status = (path / "status").read_text()
        ids = next(line.split()[1:] for line in status.splitlines() if line.startswith("Uid:"))
        if not ids or any(int(value) != uid for value in ids):
            return None
        stat_text = (path / "stat").read_text()
        started = int(stat_text.rsplit(")", 1)[1].split()[19])
        args = [os.fsdecode(value) for value in (path / "cmdline").read_bytes().split(b"\0") if value]
        environment = {}
        for field in (path / "environ").read_bytes().split(b"\0"):
            if b"=" in field:
                key, value = field.split(b"=", 1)
                environment[os.fsdecode(key)] = os.fsdecode(value)
        return {"pid": int(path.name), "uid": uid, "started": started,
                "args": args, "environment": environment}
    except (OSError, ValueError, StopIteration, IndexError):
        return None


def same_daylight_session(snapshot, environ=None, uid=None) -> bool:
    environ = os.environ if environ is None else environ
    uid = os.getuid() if uid is None else uid
    if not snapshot or snapshot.get("uid") != uid:
        return False
    previous = snapshot.get("environment", {})
    if previous.get("DAYLIGHT_SESSION") != "1" or session_kind(previous) != session_kind(environ):
        return False
    kind = session_kind(environ)
    display_key = "WAYLAND_DISPLAY" if kind == "wayland" else "DISPLAY"
    if not environ.get(display_key) or previous.get(display_key) != environ.get(display_key):
        return False
    if kind == "wayland" and previous.get("XDG_RUNTIME_DIR") != environ.get("XDG_RUNTIME_DIR"):
        return False
    if environ.get("XDG_SESSION_ID") and previous.get("XDG_SESSION_ID") != environ.get("XDG_SESSION_ID"):
        return False
    return True


def stale_manager(snapshot, environ=None, uid=None) -> bool:
    """Only the exact installed helper is eligible for an upgrade handoff."""
    if not same_daylight_session(snapshot, environ, uid):
        return False
    args = snapshot.get("args", [])
    if (len(args) != 3 or args[0] not in (sys.executable, "/usr/bin/python3")
            or args[1:] != [INSTALLED_GUI, "--session-appearance"]):
        return False
    # Published RC4 helpers had no revision marker. Unknown markers may belong
    # to a newer release; an older UI must never retire that newer manager.
    return MANAGER_REVISION_KEY not in snapshot.get("environment", {})


def retire_stale_managers(environ=None, proc_root=Path("/proc")) -> bool:
    """Release an obsolete owner's lock without touching any application."""
    if not daylight_session(environ):
        return False
    retired = False
    try:
        for path in proc_root.iterdir():
            if not path.name.isdigit() or int(path.name) == os.getpid():
                continue
            snapshot = process_snapshot(path)
            if stale_manager(snapshot, environ):
                # The helper gracefully stops two owned children (up to three
                # seconds each), then releases its display lock.
                if not terminate_legacy(snapshot, proc_root, timeout=8):
                    return False
                retired = True
    except OSError:
        return False
    return retired


def legacy_process_kind(snapshot, environ=None, uid=None):
    """Recognise only exact old Daylight Conky/background commands in this session."""
    environ = os.environ if environ is None else environ
    if not same_daylight_session(snapshot, environ, uid):
        return None
    kind = session_kind(environ)
    args = snapshot.get("args", [])
    if not args:
        return None
    executable = Path(args[0]).name
    if executable == "conky":
        if args.count("-c") != 1 or any(arg.startswith("--config") or (arg.startswith("-c") and arg != "-c") for arg in args[1:]):
            return None
        index = args.index("-c") + 1
        allowed = {str(directory() / "conky.conf"), "/usr/share/daylight/labwc/conky.lua",
                   "/usr/share/daylight/ui/conky-wayland.lua"}
        if index < len(args) and args[index] in allowed:
            return "conky"
    if executable == "swaybg" and kind == "wayland":
        if args.count("-i") != 1 or any(arg.startswith("--image") or (arg.startswith("-i") and arg != "-i") for arg in args[1:]):
            return None
        index = args.index("-i") + 1
        allowed = {"/usr/share/backgrounds/daylight/" + name for name in WALLPAPERS}
        if index < len(args) and args[index] in allowed:
            return "wallpaper"
    return None


def terminate_legacy(snapshot, proc_root=Path("/proc"), timeout=2) -> bool:
    """SIGTERM a pinned, rechecked legacy process. Never kill an ambiguous PID."""
    if not hasattr(os, "pidfd_open") or not hasattr(signal, "pidfd_send_signal"):
        return False
    descriptor = None
    try:
        descriptor = os.pidfd_open(snapshot["pid"], 0)
        current = process_snapshot(proc_root / str(snapshot["pid"]), snapshot["uid"])
        if (not current or current["started"] != snapshot["started"]
                or current["args"] != snapshot["args"]
                or current["environment"] != snapshot["environment"]):
            return False
        signal.pidfd_send_signal(descriptor, signal.SIGTERM)
        ready, _, _ = select.select([descriptor], [], [], timeout)
        return bool(ready)
    except ProcessLookupError:
        return True
    except (OSError, ValueError):
        return False
    finally:
        if descriptor is not None:
            os.close(descriptor)


def handoff_legacy(environ=None, proc_root=Path("/proc")) -> dict:
    """Retire verified RC3 children before a singleton RC4 manager replaces them."""
    result = {"conky": True, "wallpaper": True}
    if not daylight_session(environ):
        return {"conky": False, "wallpaper": False}
    try:
        processes = list(proc_root.iterdir())
    except OSError:
        return {"conky": False, "wallpaper": False}
    for path in processes:
        if not path.name.isdigit() or int(path.name) == os.getpid():
            continue
        snapshot = process_snapshot(path)
        kind = legacy_process_kind(snapshot, environ)
        if kind:
            result[kind] = terminate_legacy(snapshot, proc_root) and result[kind]
    return result


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
