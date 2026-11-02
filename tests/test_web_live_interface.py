#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Regression tests for CDN-versioned resources, without making network requests."""
import importlib.util
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('public_access', ROOT/'web-live/test-public-access.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class Interface(unittest.TestCase):
    def setUp(self):
        self.hashes={'demo.js':'a'*64,'demo.css':'b'*64}
        self.page=b'<script src="demo.js?v=aaaaaaaaaaaa"></script><link rel="stylesheet" href="demo.css?v=bbbbbbbbbbbb">'
    def test_exact_version(self):
        self.assertEqual(module.interface_paths(self.page,self.hashes)['demo.js'],'/live/demo.js?v=aaaaaaaaaaaa')
    def test_same_origin_absolute(self):
        page=self.page.replace(b'demo.js?',b'https://daylightlinux.ch/live/demo.js?')
        self.assertEqual(len(module.interface_paths(page,self.hashes)),2)
    def test_old_unversioned_url(self):
        with self.assertRaises(RuntimeError):module.interface_paths(self.page.replace(b'?v=aaaaaaaaaaaa',b''),self.hashes)
    def test_wrong_version(self):
        with self.assertRaises(RuntimeError):module.interface_paths(self.page.replace(b'aaaaaaaaaaaa',b'cccccccccccc'),self.hashes)
    def test_external_url(self):
        with self.assertRaises(RuntimeError):module.interface_paths(self.page.replace(b'demo.js?',b'https://example.invalid/demo.js?'),self.hashes)
    def test_duplicate_script(self):
        with self.assertRaises(RuntimeError):module.interface_paths(self.page+b'<script src="demo.js?v=aaaaaaaaaaaa"></script>',self.hashes)
    def test_missing_stylesheet(self):
        with self.assertRaises(RuntimeError):module.interface_paths(self.page.split(b'<link')[0],self.hashes)
if __name__=='__main__':unittest.main(verbosity=2)
