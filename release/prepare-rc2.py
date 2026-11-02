#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: contact@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""One-time, reviewable RC1-to-RC2 source migration; never modifies the host OS."""
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent

def replace(path,old,new):
    file=ROOT/path;text=file.read_text()
    if old in text:
        text=text.replace(old,new);file.write_text(text)
    elif new not in text:
        raise RuntimeError('Source does not match either reviewed state: '+path)


def main():
    for name in ['Cargo.toml','Cargo.lock','scripts/build-debs.py','scripts/test-packages.sh','scripts/build-live.sh','tests/test_integration.py','packaging/daylight.1','.github/workflows/daylight-build.yml','.github/workflows/daylight-release.yml']:
        file=ROOT/name
        if file.exists():
            text=file.read_text().replace('5.0.0-rc.1','5.0.0-rc.2').replace('5.0.0~rc1','5.0.0~rc2')
            file.write_text(text)
    replace('src/config.rs','"daylight-alpine.jpg"\n                | "daylight-coast.jpg"\n                | "daylight-forest.jpg"','"daylight-sunrise.jpg"')
    replace('src/gui.rs','"Night wallpaper",','"Dark photographic wallpaper",\n        "Sunrise wallpaper",')
    replace('src/gui.rs','"Night wallpaper" => ("wallpaper", "daylight-night.jpg"),','"Dark photographic wallpaper" => ("wallpaper", "daylight-night.jpg"),\n            "Sunrise wallpaper" => ("wallpaper", "daylight-sunrise.jpg"),')
    replace('scripts/render-assets.sh','for name in daylight-mountains daylight-night; do\n "$renderer" "assets/wallpapers/$name.svg" -quality 88 "assets/wallpapers/$name.jpg"\ndone\n"$renderer" assets/wallpapers/daylight-night.jpg -fill \'#080d15\' -colorize 58 assets/wallpapers/daylight-terminal.jpg','python3 scripts/render-photography.py')
    replace('scripts/build-debs.py','        finish("daylight-themes","all","mountain and sunrise identity, backgrounds and icons")','        copy(themes,"assets/wallpapers/CREDITS.txt","usr/share/doc/daylight-themes/CREDITS.txt")\n        finish("daylight-themes","all","photographic mountain and sunrise identity, backgrounds and icons")')
    replace('scripts/build-debs.py','            size = sum(p.stat().st_size for p in base.rglob("*") if p.is_file()) // 1024 + 1','            if package == "daylight-themes":\n                with (doc / "copyright").open("a") as notice:\n                    notice.write("\\nFiles: usr/share/backgrounds/daylight/daylight-mountains.jpg usr/share/backgrounds/daylight/daylight-sunrise.jpg usr/share/backgrounds/daylight/daylight-night.jpg usr/share/backgrounds/daylight/daylight-terminal.jpg\\nCopyright: Ali Sabbagh; Alice Donovan Rouse\\nLicense: CC0-1.0\\n Photographs are public-domain dedications; see CREDITS.txt for original sources and checksums.\\n https://creativecommons.org/publicdomain/zero/1.0/\\n")\n            size = sum(p.stat().st_size for p in base.rglob("*") if p.is_file()) // 1024 + 1')
    # Validate checksum-manifest paths before a privileged hash reader touches them.
    file=ROOT/'server/install-apt-server.sh';text=file.read_text()
    text=text.replace('(cd "$packages" && sha256sum -c PACKAGE-SHA256SUMS)\n# Validate manifest paths','# Validate manifest paths')
    marker='PY\nfingerprint=$(gpg'
    if marker in text:text=text.replace(marker,'PY\n(cd "$packages" && sha256sum -c PACKAGE-SHA256SUMS)\nfingerprint=$(gpg')
    file.write_text(text)
    workflow=ROOT/'.github/workflows/daylight-build.yml';text=workflow.read_text()
    text=text.replace('branches: [master, build/daylight-v5]','branches: [master, build/daylight-v5, build/daylight-v5-rc2]')
    text=text.replace('python3 curl gnupg\n','python3 python3-pil python3-venv curl gnupg\n')
    text=text.replace('python3 -m py_compile scripts/*.py tests/*.py telemetry/*.py','python3 -m py_compile scripts/*.py tests/*.py telemetry/*.py server/*.py demo/*.py website/*.py\n          for file in scripts/*.sh server/*.sh demo/*.sh; do sh -n "$file"; done')
    old='          python3 tests/test_repository.py 2>&1 | tee dist/validation/repository-tests.log\n'
    if 'tests/test_release_tools.py' not in text:
        text=text.replace(old,old+'          python3 tests/test_release_tools.py 2>&1 | tee dist/validation/release-tools-tests.log\n')
    text=text.replace('qemu-system-x86 xorriso\n','qemu-system-x86 xorriso ovmf novnc websockify\n')
    marker='      - name: Make disposable-container test evidence readable\n'
    extra='''      - name: Real BIOS and UEFI ISO bootloader tests
        if: github.event_name != 'pull_request'
        shell: bash
        run: |
          set -euo pipefail
          iso=dist/daylight-live_5.0.0-rc.2_amd64.iso
          for firmware in bios uefi; do
            python3 scripts/test-boot.py "$iso" --firmware "$firmware" --timeout 600
            convert "dist/boot-$firmware/desktop.ppm" "dist/boot-$firmware/desktop.png"
          done
      - name: Real browser connection to the candidate live guest
        if: github.event_name != 'pull_request'
        shell: bash
        run: |
          set -euo pipefail
          python3 -m venv dist/browser-venv
          dist/browser-venv/bin/pip install playwright==1.55.0
          dist/browser-venv/bin/python tests/test_browser_demo.py
'''
    if 'Real BIOS and UEFI ISO bootloader tests' not in text:text=text.replace(marker,extra+marker)
    text=text.replace('            dist/live-test/\n','            dist/live-test/\n            dist/boot-bios/\n            dist/boot-uefi/\n            dist/browser-demo/\n')
    workflow.write_text(text)
    publisher=ROOT/'.github/workflows/daylight-release.yml';text=publisher.read_text()
    text=text.replace("('master','build/daylight-v5')","('master','build/daylight-v5','build/daylight-v5-rc2')")
    old="          if not (root/'live-test/result.txt').read_text().startswith('PASS:'):\n              raise SystemExit('Missing live boot evidence')\n"
    new=old+"          for mode in ('boot-bios','boot-uefi','browser-demo'):\n              if not (root/mode/'result.txt').read_text().startswith('PASS:'):\n                  raise SystemExit('Missing validation gate: '+mode)\n"
    if 'Missing validation gate:' not in text:text=text.replace(old,new)
    # A draft is retrieved through gh release view, which works before the public tag endpoint exists.
    old="          release=json.loads(subprocess.check_output(['gh','api','repos/'+os.environ['GH_REPO']+'/releases/tags/'+os.environ['TAG']]))\n"
    new="          metadata=json.loads(subprocess.check_output(['gh','release','view',os.environ['TAG'],'--json','databaseId']))\n          release=json.loads(subprocess.check_output(['gh','api','repos/'+os.environ['GH_REPO']+'/releases/'+str(metadata['databaseId'])]))\n"
    text=text.replace(old,new)
    publisher.write_text(text)
    print('RC2 migration applied. Commit these source changes before running candidate validation.')


if __name__=='__main__':main()
