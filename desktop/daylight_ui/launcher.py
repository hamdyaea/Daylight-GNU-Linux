"""Freedesktop application discovery and shell-free launching.

SPDX-License-Identifier: GPL-3.0-only
"""
from __future__ import annotations
from dataclasses import dataclass
import configparser
import os
from pathlib import Path
import shlex
import shutil
import subprocess


@dataclass(frozen=True)
class Application:
    identifier: str
    name: str
    description: str
    argv: tuple[str, ...]
    terminal: bool = False
    directory: str = ""
    icon: str = ""


def exec_arguments(value: str, name: str, icon: str, desktop_file: str) -> tuple[str, ...]:
    result = []
    for token in shlex.split(value, posix=True):
        if token == "%i":
            if icon:
                result.extend(("--icon", icon))
            continue
        if token in ("%f", "%F", "%u", "%U", "%d", "%D", "%n", "%N", "%v", "%m"):
            continue
        output, index = "", 0
        while index < len(token):
            if token[index] != "%":
                output += token[index]
                index += 1
                continue
            index += 1
            if index >= len(token):
                raise ValueError("Trailing field code")
            code = token[index]
            if code == "%": output += "%"
            elif code == "c": output += name
            elif code == "k": output += desktop_file
            else: raise ValueError("Unsupported embedded field code")
            index += 1
        result.append(output)
    if not result or not result[0]:
        raise ValueError("Missing executable")
    return tuple(result)


def application_directories() -> list[Path]:
    own = Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local/share")))
    roots = [own, *(Path(p) for p in os.environ.get("XDG_DATA_DIRS", "/usr/local/share:/usr/share").split(":"))]
    return [root / "applications" for root in roots if root.is_absolute()]


def discover(directories=None, language="en", desktop=None) -> list[Application]:
    paths = application_directories() if directories is None else [Path(p) for p in directories]
    desktops = set((os.environ.get("XDG_CURRENT_DESKTOP", "Daylight:Fluxbox") if desktop is None else desktop).split(":"))
    seen, result = set(), []
    for directory in paths:
        for path in sorted(directory.rglob("*.desktop")) if directory.is_dir() else []:
            identifier = path.relative_to(directory).as_posix().replace("/", "-")
            if identifier in seen:
                continue
            seen.add(identifier)
            parser = configparser.ConfigParser(interpolation=None, strict=False)
            try:
                parser.read_string(path.read_text(encoding="utf-8"))
                entry = parser["Desktop Entry"]
                if entry.get("Type", "Application") != "Application": continue
                if entry.getboolean("Hidden", fallback=False) or entry.getboolean("NoDisplay", fallback=False): continue
                only = set(filter(None, entry.get("OnlyShowIn", "").split(";")))
                excluded = set(filter(None, entry.get("NotShowIn", "").split(";")))
                if only and not only.intersection(desktops): continue
                if excluded.intersection(desktops): continue
                attempt = entry.get("TryExec", "")
                if attempt and not shutil.which(attempt): continue
                name = entry.get(f"Name[{language}]", entry.get("Name", "")).strip()
                if not name: continue
                icon = entry.get("Icon", "")
                argv = exec_arguments(entry.get("Exec", ""), name, icon, str(path))
                if not shutil.which(argv[0]): continue
                workdir = entry.get("Path", "")
                if workdir and (not Path(workdir).is_absolute() or not Path(workdir).is_dir()): workdir = ""
                result.append(Application(identifier, name, entry.get(f"Comment[{language}]", entry.get("Comment", "")),
                                          argv, entry.getboolean("Terminal", fallback=False), workdir, icon))
            except (ValueError, KeyError, OSError, configparser.Error):
                continue
    return sorted(result, key=lambda item: item.name.casefold())


def launch(application: Application):
    command = list(application.argv)
    if application.terminal:
        terminal = shutil.which("x-terminal-emulator") or shutil.which("xterm")
        if not terminal:
            raise RuntimeError("Install a terminal to open this application")
        command = [terminal, "-e", *command]
    return subprocess.Popen(command, cwd=application.directory or None,
                            stdin=subprocess.DEVNULL, start_new_session=True)
