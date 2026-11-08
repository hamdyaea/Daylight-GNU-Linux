#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Regression checks for installer scope, wallpaper integrity and website structure."""
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from PIL import Image

ROOT=Path(__file__).resolve().parent.parent

class Links(HTMLParser):
    def __init__(self):
        super().__init__();self.refs=[];self.h1=0;self.lang=None
    def handle_starttag(self,tag,attrs):
        values=dict(attrs)
        if tag=='h1':self.h1+=1
        if tag=='html':self.lang=values.get('lang')
        for key in ('href','src'):
            if key in values:self.refs.append(values[key])

class ReleaseTools(unittest.TestCase):
    def script(self,*args):
        return subprocess.run(['sh',str(ROOT/'scripts/install-daylight.sh'),*args],capture_output=True,text=True,timeout=10)
    def test_installer_help(self):
        result=self.script('--help');self.assertEqual(result.returncode,0);self.assertIn('plan',result.stdout)
    def test_installer_rejects_unknown(self):
        self.assertEqual(self.script('--unsafe').returncode,2)
    def test_games_require_desktop(self):
        self.assertEqual(self.script('--games').returncode,2)
    def test_all_includes_telemetry_but_leaves_it_off(self):
        installer=(ROOT/'scripts/install-daylight.sh').read_text()
        config=(ROOT/'packaging/telemetry.conf').read_text()
        postinst=(ROOT/'packaging/postinst').read_text()
        self.assertIn('--all',installer)
        self.assertIn("daylight-linux daylight-games daylight-telemetry",installer)
        self.assertIn('enabled=no',config)
        self.assertIn('No service is enabled, started, or restarted',postinst)
        self.assertNotIn('systemctl enable --now daylight-telemetry.timer',installer+postinst)
    def test_default_does_not_apply(self):
        result=self.script()
        if Path('/etc/debian_version').exists():
            self.assertEqual(result.returncode,0,result.stderr);self.assertIn('Plan only',result.stdout)
        else:
            self.assertEqual(result.returncode,2);self.assertIn('No Debian base',result.stderr)
    def test_signed_by_is_scoped(self):
        source=(ROOT/'scripts/install-daylight.sh').read_text()
        self.assertIn('Signed-By:',source)
        self.assertIn('Pin-Priority: -1',source)
        self.assertNotIn('--allow-unauthenticated',source)
        self.assertNotIn('trusted=yes',source)
        self.assertIn('B0575F821A31DD20753DE07C50D21240F4BCB02E',source)
    def test_photograph_sources_are_pinned_and_licensed(self):
        entries=json.loads((ROOT/'assets/photography.json').read_text())
        self.assertGreaterEqual(len(entries),2)
        for item in entries:
            self.assertEqual(item['license'],'CC0-1.0')
            self.assertRegex(item['sha256'],r'^[a-f0-9]{64}$')
            self.assertTrue(item['source'].startswith('https://commons.wikimedia.org/'))
    def test_wallpaper_dimensions(self):
        for name in ('daylight-mountains','daylight-sunrise','daylight-night'):
            with Image.open(ROOT/'assets/wallpapers'/f'{name}.jpg') as image:
                self.assertEqual(image.size,(3840,2160) if name == 'daylight-sunrise' else (1672,941));self.assertFalse(image.getexif())
    def test_settings_match_shipped_wallpapers(self):
        values=re.findall(r'"(daylight-[a-z-]+\.(?:jpg|png))"',(ROOT/'src/config.rs').read_text())
        self.assertGreaterEqual(len(values),4)
        for value in values:self.assertTrue((ROOT/'assets/wallpapers'/value).is_file(),value)
    def test_demo_is_bounded_and_offline(self):
        source=(ROOT/'demo/run.py').read_text()
        self.assertIn("'-nic','none'",source)
        self.assertIn("'-monitor','none'",source)
        self.assertIn('deadline=time.monotonic()+args.duration',source)
        self.assertNotIn("'-virtfs'",source)
        self.assertNotIn('/dev/sda',source)
    def test_static_site(self):
        with tempfile.TemporaryDirectory(prefix='daylight-site-test-') as temporary:
            root=Path(temporary)
            subprocess.run(['python3',str(ROOT/'website/build.py'),'--output',str(root)],check=True,timeout=90,capture_output=True)
            for language,prefix in [('en',''),('fr','fr/')]:
                for page in ('index.html','download.html','install.html','try-online.html','wallpapers.html','books.html','old/index.html','privacy.html'):
                    parser=Links();parser.feed((root/(prefix+page)).read_text())
                    self.assertEqual(parser.lang,language);self.assertEqual(parser.h1,1)
                    for ref in parser.refs:
                        if ref.startswith('/') and not ref.startswith(('/apt/','/old/site/')):
                            self.assertTrue((root/unquote(urlsplit(ref).path).lstrip('/')).exists(),ref)
            self.assertTrue((root/'install.sh').is_file())
            self.assertIn('https://www.amazon.fr/stores/author/B0BM89T88X',(root/'books.html').read_text())
            self.assertIn('info@daylightlinux.ch',(root/'fr/books.html').read_text())
            self.assertIn('url=/books.html',(root/'linux-book.html').read_text())
            self.assertNotIn('fonts.googleapis.com',(root/'index.html').read_text())
            self.assertNotIn('google-analytics',(root/'assets/v5/main.js').read_text())

if __name__=='__main__':unittest.main(verbosity=2)