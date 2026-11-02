#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: contact@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""One-time, reviewable RC1-to-RC2 source migration; never modifies the host OS."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent

def replace(path,old,new):
    file=ROOT/path;text=file.read_text()
    if old in text:file.write_text(text.replace(old,new))
    elif new not in text:raise RuntimeError('Source does not match either reviewed state: '+path)

def main():
    for name in ['Cargo.toml','Cargo.lock','scripts/build-debs.py','scripts/test-packages.sh','scripts/build-live.sh','tests/test_integration.py','packaging/daylight.1']:
        file=ROOT/name
        if file.exists():file.write_text(file.read_text().replace('5.0.0-rc.1','5.0.0-rc.2').replace('5.0.0~rc1','5.0.0~rc2'))
    replace('src/config.rs','"daylight-alpine.jpg"\n                | "daylight-coast.jpg"\n                | "daylight-forest.jpg"','"daylight-sunrise.jpg"')
    replace('src/gui.rs','"Night wallpaper",','"Dark photographic wallpaper",\n        "Sunrise wallpaper",')
    replace('src/gui.rs','"Night wallpaper" => ("wallpaper", "daylight-night.jpg"),','"Dark photographic wallpaper" => ("wallpaper", "daylight-night.jpg"),\n            "Sunrise wallpaper" => ("wallpaper", "daylight-sunrise.jpg"),')
    replace('scripts/render-assets.sh','for name in daylight-mountains daylight-night; do\n "$renderer" "assets/wallpapers/$name.svg" -quality 88 "assets/wallpapers/$name.jpg"\ndone\n"$renderer" assets/wallpapers/daylight-night.jpg -fill \'#080d15\' -colorize 58 assets/wallpapers/daylight-terminal.jpg','python3 scripts/render-photography.py')
    replace('scripts/build-debs.py','        finish("daylight-themes","all","mountain and sunrise identity, backgrounds and icons")','        copy(themes,"assets/wallpapers/CREDITS.txt","usr/share/doc/daylight-themes/CREDITS.txt")\n        finish("daylight-themes","all","photographic mountain and sunrise identity, backgrounds and icons")')
    replace('scripts/build-debs.py','            size = sum(p.stat().st_size for p in base.rglob("*") if p.is_file()) // 1024 + 1','            if package == "daylight-themes":\n                with (doc / "copyright").open("a") as notice:\n                    notice.write("\\nFiles: usr/share/backgrounds/daylight/daylight-mountains.jpg usr/share/backgrounds/daylight/daylight-sunrise.jpg usr/share/backgrounds/daylight/daylight-night.jpg usr/share/backgrounds/daylight/daylight-terminal.jpg\\nCopyright: Ali Sabbagh; Alice Donovan Rouse\\nLicense: CC0-1.0\\n Photographs are public-domain dedications; see CREDITS.txt for original sources and checksums.\\n https://creativecommons.org/publicdomain/zero/1.0/\\n")\n            size = sum(p.stat().st_size for p in base.rglob("*") if p.is_file()) // 1024 + 1')
    file=ROOT/'server/install-apt-server.sh';text=file.read_text()
    text=text.replace('(cd "$packages" && sha256sum -c PACKAGE-SHA256SUMS)\n# Validate manifest paths','# Validate manifest paths')
    marker='PY\nfingerprint=$(gpg'
    if marker in text:text=text.replace(marker,'PY\n(cd "$packages" && sha256sum -c PACKAGE-SHA256SUMS)\nfingerprint=$(gpg')
    file.write_text(text)
    print('RC2 migration applied. Commit these source changes before running candidate validation.')

if __name__=='__main__':main()
