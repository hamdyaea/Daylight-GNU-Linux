#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Keep complete branded artwork visible and expose the additional credited wallpaper."""
from pathlib import Path
for name in ('scripts/daylight-session', 'src/gui.rs'):
    path=Path(name)
    text=path.read_text()
    if '--bg-fill' not in text and '--bg-max' not in text:
        raise SystemExit('Unexpected wallpaper command in '+name)
    text=text.replace('--bg-fill','--bg-max')
    if name=='src/gui.rs' and 'Himalayan wallpaper' not in text:
        text=text.replace('        "Sunrise wallpaper",','        "Sunrise wallpaper",\n        "Himalayan wallpaper",')
        text=text.replace('            "Sunrise wallpaper" => ("wallpaper", "daylight-sunrise.jpg"),','            "Sunrise wallpaper" => ("wallpaper", "daylight-sunrise.jpg"),\n            "Himalayan wallpaper" => ("wallpaper", "daylight-himalaya.jpg"),')
    path.write_text(text)
print('Complete wallpaper aspect ratio preserved; all shipped landscapes selectable.')
