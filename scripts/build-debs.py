#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# Copyright (C) 2026 Hamdy Abou El Anein
# SPDX-License-Identifier: GPL-3.0-only
"""Build self-contained Daylight binary packages without changing the host OS."""
import argparse
import gzip
import hashlib
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
VERSION = "5.0.0~rc2-2"
MAINTAINER = "Hamdy Abou El Anein <info@daylightlinux.ch>"
HEADER = "# Developer: Hamdy Abou El Anein\n# Contact: info@daylightlinux.ch\n# SPDX-License-Identifier: GPL-3.0-only\n"

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arch", choices=("amd64", "arm64"), required=True)
    parser.add_argument("--binary", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    triple = {"amd64": "x86_64-unknown-linux-musl", "arm64": "aarch64-unknown-linux-musl"}[args.arch]
    binary = args.binary or ROOT / "target" / triple / "release/daylight"
    data = binary.read_bytes()
    expected = {"amd64": 62, "arm64": 183}[args.arch]
    if data[:4] != b"\x7fELF" or struct.unpack_from("<H", data, 18)[0] != expected:
        raise SystemExit("Wrong executable architecture")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if not epoch:
        epoch = subprocess.check_output(["git", "-C", str(ROOT), "log", "-1", "--format=%ct"], text=True).strip()
    env = dict(os.environ, SOURCE_DATE_EPOCH=epoch)
    built = []
    with tempfile.TemporaryDirectory(prefix="daylight-packages-") as temporary:
        work = Path(temporary)
        def write(base, name, content, mode=0o644):
            path = base / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            path.chmod(mode)
        def copy(base, source, dest, mode=0o644):
            path = base / dest
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / source, path)
            path.chmod(mode)
        def finish(package, architecture, description, depends="", recommends="", extra=None):
            base = work / package
            doc = base / "usr/share/doc" / package
            doc.mkdir(parents=True, exist_ok=True)
            (doc / "copyright").write_text("Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/\nUpstream-Name: Daylight GNU/Linux\nSource: https://github.com/hamdyaea/Daylight-GNU-Linux\n\nFiles: *\nCopyright: 2026 Hamdy Abou El Anein\nLicense: GPL-3.0-only\n See /usr/share/common-licenses/GPL-3 for the complete license.\n")
            if package == "daylight-core":
                for license_file in (ROOT / "licenses").glob("*") if (ROOT / "licenses").exists() else []:
                    shutil.copyfile(license_file, doc / license_file.name)
                (doc / "copyright").write_text((doc / "copyright").read_text()+"\nFiles: usr/bin/daylight\nCopyright: 2026 Hamdy Abou El Anein; the Rust project contributors; musl contributors\nLicense: GPL-3.0-only and MIT and Apache-2.0\n The statically linked Rust standard library and musl retain their notices.\n See bundled third-party license files and THIRD_PARTY.md.\n")
                if (ROOT / "docs/THIRD_PARTY.md").exists(): shutil.copyfile(ROOT / "docs/THIRD_PARTY.md", doc / "THIRD_PARTY.md")
            if package == "daylight-themes":
                with (doc / "copyright").open("a") as notice:
                    notice.write("\nFiles: usr/share/backgrounds/daylight/daylight-sunrise.jpg usr/share/backgrounds/daylight/daylight-himalaya.jpg\nCopyright: Ali Sabbagh; Alice Donovan Rouse\nLicense: CC0-1.0\n Photographs are public-domain dedications; see CREDITS.txt for original sources and checksums.\n https://creativecommons.org/publicdomain/zero/1.0/\n")
            size = sum(p.stat().st_size for p in base.rglob("*") if p.is_file()) // 1024 + 1
            control = f"Package: {package}\nVersion: {VERSION}\nArchitecture: {architecture}\nMaintainer: {MAINTAINER}\nSection: {'x11' if package == 'daylight-desktop' else 'utils'}\nPriority: optional\nInstalled-Size: {size}\nHomepage: https://daylightlinux.ch\n"
            if depends: control += f"Depends: {depends}\n"
            if package == "daylight-desktop": control += "Breaks: daylight-session-defaults (<< 1.2-1)\n"
            if recommends: control += f"Recommends: {recommends}\n"
            control += f"Description: {description}\n Lightweight, opt-in components of Daylight GNU/Linux.\n Does not replace the base distribution, kernel or existing desktop configuration.\n"
            write(base, "DEBIAN/control", control)
            if extra: extra(base)
            checks = []
            for p in sorted(base.rglob("*")):
                if p.is_file() and "DEBIAN" not in p.relative_to(base).parts:
                    checks.append(hashlib.md5(p.read_bytes()).hexdigest() + "  " + str(p.relative_to(base)))
            write(base, "DEBIAN/md5sums", "\n".join(checks) + "\n")
            for p in sorted(base.rglob("*"), reverse=True): os.utime(p, (int(epoch), int(epoch)), follow_symlinks=False)
            deb = output / f"{package}_{VERSION}_{architecture}.deb"
            subprocess.run(["dpkg-deb", "--root-owner-group", "--build", str(base), str(deb)], check=True, env=env)
            built.append(deb)
        core = work / "daylight-core"
        copy(core, binary, "usr/bin/daylight", 0o755)
        copy(core, "config/fastfetch/config.jsonc", "usr/share/daylight/fastfetch/config.jsonc")
        copy(core, "config/fastfetch/logo.txt", "usr/share/daylight/fastfetch/logo.txt")
        if (ROOT / "packaging/daylight.1").exists():
            path=core / "usr/share/man/man1/daylight.1.gz";path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(gzip.compress((ROOT / "packaging/daylight.1").read_bytes(),mtime=0))
        finish("daylight-core",args.arch,"local management and privacy-respecting Rust utilities")
        themes = work / "daylight-themes"
        for p in sorted((ROOT / "assets/wallpapers").glob("*")):
            if p.suffix in (".jpg", ".png"): copy(themes,p,"usr/share/backgrounds/daylight/"+p.name)
        copy(themes,"assets/branding/daylight.svg","usr/share/icons/hicolor/scalable/apps/daylight.svg")
        copy(themes,"assets/branding/daylight.png","usr/share/icons/hicolor/512x512/apps/daylight.png")
        copy(themes,"assets/wallpapers/CREDITS.txt","usr/share/doc/daylight-themes/CREDITS.txt")
        finish("daylight-themes","all","photographic mountain and sunrise identity, backgrounds and icons")
        desktop = work / "daylight-desktop"
        for name in ("daylight-session","daylight-terminal"): copy(desktop,"scripts/"+name,"usr/bin/"+name,0o755)
        copy(desktop,"scripts/interactive-shell","usr/lib/daylight/interactive-shell",0o755)
        for folder in ("fluxbox","conky","shell"):
            for p in sorted((ROOT / "config" / folder).glob("*")): copy(desktop,p,f"usr/share/daylight/{folder}/{p.name}")
        for source,dest in [("daylight.desktop","usr/share/xsessions/daylight.desktop"),("control-center.desktop","usr/share/applications/daylight-control-center.desktop"),("terminal.desktop","usr/share/applications/daylight-terminal.desktop")]: copy(desktop,"packaging/"+source,dest)
        finish("daylight-desktop","all","isolated Fluxbox desktop session",f"daylight-core (= {VERSION}), daylight-themes (= {VERSION}), fluxbox, conky-std | conky-all, xterm, feh, yad, pcmanfm, fonts-dejavu-core, xserver-xorg-core, xserver-xorg-input-libinput, xinit, x11-xserver-utils, x11-utils", "")
        applications={"password":"Password Generator","temperature":"Temperature Converter","days":"Days Calculator","connect":"Local Network Information","alarm":"Alarm","speech":"Text to Speech"}
        games={"dice":"Dice Simulator","coin":"Coin Flip","lottery":"Lottery Simulator","rpsls":"Rock Paper Scissors Lizard Spock","cards":"Battle Cards","tournament":"Tournament Simulator","basketball":"Basketball Simulator","memory":"Memory Game","slots":"Slot Simulator","guess":"Guess the Number"}
        for package,entries,category in [("daylight-apps",applications,"Utility;"),("daylight-games",games,"Game;")]:
            base = work / package
            for name,title in entries.items():
                write(base,f"usr/share/applications/daylight-{name}.desktop",HEADER+f"[Desktop Entry]\nName=Daylight {title}\nExec=/usr/bin/daylight app {name}\nIcon=daylight\nTerminal=false\nType=Application\nCategories={category}\n")
            if package == "daylight-apps": copy(base,"scripts/daylight-speech","usr/lib/daylight/speech",0o755)
            deps=f"daylight-desktop (= {VERSION})"+(" , espeak-ng, libnotify-bin, python3-gi, gir1.2-gtk-3.0" if package=="daylight-apps" else "")
            finish(package,"all","optional native application launchers" if package=="daylight-apps" else "optional offline games without wagers",deps)
        telemetry=work / "daylight-telemetry"
        copy(telemetry,"packaging/telemetry.conf","etc/daylight/telemetry.conf")
        for name in ("daylight-telemetry.service","daylight-telemetry.timer"): copy(telemetry,"packaging/"+name,"usr/lib/systemd/system/"+name)
        def telemetry_scripts(base):
            write(base,"DEBIAN/conffiles","/etc/daylight/telemetry.conf\n")
            for name in ("postinst","prerm","postrm"): copy(base,"packaging/"+name,"DEBIAN/"+name,0o755)
        finish("daylight-telemetry","all","optional boot counter, disabled until explicit consent",f"daylight-core (= {VERSION}), curl, ca-certificates, systemd",extra=telemetry_scripts)
        finish("daylight-linux","all","lightweight Daylight environment metapackage",f"daylight-desktop (= {VERSION}), daylight-apps (= {VERSION})")
    print("\nPackages created in",output)
    for p in built: print(hashlib.sha256(p.read_bytes()).hexdigest(),p.name)

if __name__ == "__main__":
    main()
