#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Regression checks for the terminal-first browser guest; no host execution of init."""
from pathlib import Path
import re
import subprocess
import unittest
ROOT = Path(__file__).resolve().parent.parent
class Startup(unittest.TestCase):
    def test_shell_syntax(self):
        for name in ('init', 'daylight-terminal', 'daylight-shell'):
            subprocess.run(['sh', '-n', str(ROOT/'web-live'/name)], check=True)
    def test_terminal_is_the_only_startup_app(self):
        text=(ROOT/'web-live/init').read_text()
        self.assertEqual(text.count('/usr/local/bin/daylight-terminal >'), 1)
        self.assertNotRegex(text, r'(?m)^\s*(?:xcalc|xmessage)\b')
    def test_explicit_daylight_title(self):
        text=(ROOT/'web-live/daylight-terminal').read_text()
        self.assertIn("-title 'Daylight Start'", text)
        self.assertIn("-n 'Daylight Start'", text)
        self.assertIn('-e /usr/local/bin/daylight-shell', text)
    def test_readiness_requires_window_focus(self):
        text=(ROOT/'web-live/init').read_text()
        marker=text.index('DAYLIGHT_WEB_DESKTOP_READY')
        self.assertLess(text.index('xdotool search --all --onlyvisible'), marker)
        self.assertLess(text.index('[ -f /run/daylight-shell-ready ]'), marker)
        self.assertLess(text.index('[ "$active" = "$window" ]'), marker)
        self.assertNotIn('DAYLIGHT_WEB_DESKTOP_READY',(ROOT/'web-live/daylight-shell').read_text())
    def test_consistent_menu_and_keyboard_launcher(self):
        text=(ROOT/'web-live/prepare-root.py').read_text()
        self.assertIn('(Daylight Start - Terminal) {/usr/local/bin/daylight-terminal}', text)
        self.assertIn('Mod4 Return :Exec /usr/local/bin/daylight-terminal', text)
        self.assertNotIn(':Exec xterm -e /usr/local/bin/daylight-shell', text)
    def test_browser_brand_and_upstream_disclosure(self):
        text=(ROOT/'web-live/index.html').read_text()
        self.assertIn('id="start" type="button">Démarrer', text)
        self.assertEqual(re.findall(r'<button id="([^"]+)"',text), ['start','reset','stop'])
        self.assertIn('Alpine Linux x86', text)
        self.assertIn('Daylight Start — opening your terminal',(ROOT/'web-live/demo.js').read_text())
    def test_corresponding_sources_include_helpers(self):
        text=(ROOT/'web-live/package.py').read_text()
        self.assertIn("('init','daylight-terminal','daylight-shell')", text)
if __name__=='__main__': unittest.main(verbosity=2)
