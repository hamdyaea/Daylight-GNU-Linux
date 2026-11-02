#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Prepare only a disposable Alpine x86 tree under this project's dist directory."""
import argparse
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parent.parent
HEADER='# Developer: Hamdy Abou El Anein\n# Contact: info@daylightlinux.ch\n# SPDX-License-Identifier: GPL-3.0-only\n'

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
 args=p.parse_args();base=args.root.resolve();out=args.output.resolve()
 if ROOT/'dist' not in base.parents or not (base/'lib/apk/db/installed').is_file():p.error('Disposable project dist Alpine root required')
 out.mkdir(parents=True,exist_ok=True)
 packages=[]
 for block in (base/'lib/apk/db/installed').read_text().split('\n\n'):
  fields=dict(line.split(':',1) for line in block.splitlines() if ':' in line and not line.startswith(('F:','R:','Z:','a:')))
  if 'P' in fields:packages.append({k:fields.get(k) for k in ('P','V','A','L','o','c','U')})
 (out/'packages.json').write_text(json.dumps(packages,indent=2)+'\n')
 kernel=base/'boot/vmlinuz-virt'
 if kernel.is_file():shutil.copyfile(kernel,out/'vmlinuz.bin')
 elif not (out/'vmlinuz.bin').is_file():raise SystemExit('Kernel missing')
 # Remove unused software-rendering/DRI payloads; this guest uses framebuffer X11 only.
 for rel in ['usr/lib/gallium-pipe','usr/lib/dri','usr/share/doc','usr/share/man','usr/share/locale','boot']:
  path=base/rel
  if path.is_dir() and not path.is_symlink():shutil.rmtree(path)
 for pattern in ('libLLVM*','libgallium*'):
  for path in (base/'usr/lib').glob(pattern):
   if path.is_file() or path.is_symlink():path.unlink()
 # Keep only the transitive kernel modules required by the emulated display/input.
 for modules in (base/'lib/modules').iterdir():
  dependency_file=modules/'modules.dep'
  if not dependency_file.is_file():continue
  dependencies={}
  for line in dependency_file.read_text().splitlines():
   name,values=line.split(':',1);dependencies[name]=values.split()
  wanted=[name for name in dependencies if name.endswith(('/bochs.ko.gz','/evdev.ko.gz','/psmouse.ko.gz'))]
  if len(wanted)!=3:raise ValueError('Expected display, keyboard and mouse modules are missing')
  keep=set()
  while wanted:
   name=wanted.pop()
   if name in keep:continue
   keep.add(name);wanted.extend(dependencies.get(name,[]))
  for name in keep:
   if not (modules/name).is_file():raise ValueError('Required module missing: '+name)
  for path in modules.rglob('*.ko*'):
   if path.is_file() and str(path.relative_to(modules)) not in keep:path.unlink()
  (out/'kernel-modules.json').write_text(json.dumps(sorted(keep),indent=2)+'\n')
 def write(name,data,mode=0o644):
  path=base/name;path.parent.mkdir(parents=True,exist_ok=True)
  if base not in path.parent.resolve().parents:raise ValueError('Guest path escapes disposable root')
  if path.is_symlink():path.unlink()
  if path.exists():path.chmod(mode)
  path.write_text(data);path.chmod(mode)
 shutil.copyfile(ROOT/'web-live/init',base/'init');(base/'init').chmod(0o755)
 write('root/.fluxbox/init',HEADER+'session.screen0.toolbar.tools: workspacename, prevwindow, nextwindow, iconbar, systemtray, clock\nsession.screen0.toolbar.widthPercent: 100\nsession.screen0.toolbar.placement: BottomCenter\nsession.screen0.workspaces: 2\nsession.menuFile: /root/.fluxbox/menu\nsession.keyFile: /root/.fluxbox/keys\nsession.styleFile: /usr/share/fluxbox/styles/Black\n')
 write('root/.fluxbox/menu',HEADER+'[begin] (Daylight Linux - Web)\n[exec] (Terminal) {xterm -bg "#10191f" -fg "#f5eddb" -fa "DejaVu Sans Mono" -fs 11 -e /usr/local/bin/daylight-shell}\n[exec] (System monitor) {xterm -title "System monitor" -e top}\n[exec] (About this preview) {xterm -hold -e cat /etc/daylight-preview}\n[workspaces] (Workspaces)\n[reconfig] (Reload Fluxbox)\n[end]\n')
 write('root/.fluxbox/keys',HEADER+'OnDesktop Mouse3 :RootMenu\nMod1 F4 :Close\nMod4 Return :Exec xterm -e /usr/local/bin/daylight-shell\n')
 write('etc/daylight-preview','Daylight Web Preview\nDeveloper: Hamdy Abou El Anein\nContact: info@daylightlinux.ch\n\nExperimental Alpine x86 / Fluxbox inside v86 WebAssembly.\nThe main Daylight release remains Debian/Raspberry Pi OS.\nThis preview is not the complete installable distribution.\nTemporary files, no external guest network, no host disks.\nClosing or resetting the tab discards your session.\n\nDaylight glue: GPL-3.0-only. Upstream licenses are retained.\n')
 write('etc/resolv.conf','# No external guest network.\n')
 write('usr/local/bin/daylight-shell','#!/bin/sh\n'+HEADER+'''export HOME=/root TERM=xterm-256color PS1='daylight:~$ '
clear
printf '\\033[1;33m   /\\\\    DAYLIGHT LINUX\\n__/  \\\\__ WEB PREVIEW\\033[0m\\n\\n'
cat /etc/daylight-preview
printf '\\nTry: uname -a | free -m | top | ls | vi\\nRight-click the desktop for its menu.\\n\\n'
printf '\\nDAYLIGHT_WEB_DESKTOP_READY\\n' >/dev/ttyS0
exec /bin/sh
''',0o755)
 target=base/'usr/share/daylight/wallpaper.jpg';target.parent.mkdir(parents=True,exist_ok=True)
 shutil.copyfile(ROOT/'assets/wallpapers/daylight-mountains.jpg',target)
 print('Prepared framebuffer-only Alpine guest. Unused OpenGL payloads removed.')

if __name__=='__main__':main()
