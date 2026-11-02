#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: contact@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Connect a real browser to the live guest's noVNC endpoint in disposable CI."""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import time
import urllib.request
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent.parent

def main():
    isos=sorted((ROOT/'dist').glob('daylight-live_*_amd64.iso'))
    if len(isos)!=1:raise RuntimeError('Exactly one candidate ISO is required')
    iso=isos[0];value=hashlib.sha256()
    with iso.open('rb') as stream:
        for block in iter(lambda:stream.read(4*1024*1024),b''):value.update(block)
    output=ROOT/'dist/browser-demo';output.mkdir(parents=True,exist_ok=True)
    browser=shutil.which('google-chrome') or shutil.which('chromium')
    if not browser:raise RuntimeError('A real Chromium browser is required; this test must not silently skip')
    with (output/'demo.log').open('w') as log:
        process=subprocess.Popen(['python3',str(ROOT/'demo/run.py'),'--iso',str(iso),'--sha256',value.hexdigest(),'--duration','300'],stdout=log,stderr=subprocess.STDOUT)
        try:
            for _ in range(100):
                if process.poll() is not None:raise RuntimeError('Demo exited before its HTTP frontend started')
                try:
                    with urllib.request.urlopen('http://127.0.0.1:6080/vnc.html',timeout=2) as response:
                        if response.status==200:break
                except OSError:time.sleep(.2)
            else:raise RuntimeError('noVNC HTTP frontend did not start')
            with sync_playwright() as engine:
                instance=engine.chromium.launch(executable_path=browser,headless=True,args=['--disable-dev-shm-usage'])
                page=instance.new_page(viewport={'width':1366,'height':900})
                page.goto('http://127.0.0.1:6080/vnc.html?autoconnect=true&resize=scale',wait_until='domcontentloaded')
                page.wait_for_function("document.documentElement.classList.contains('noVNC_connected')",timeout=60000)
                time.sleep(45)
                page.screenshot(path=str(output/'browser.png'),full_page=True)
                page.context.close();instance.close()
            (output/'result.txt').write_text('PASS: real Chromium connected through noVNC/WebSocket to the actual candidate ISO guest. BIOS/UEFI desktop readiness is separately checked by the boot tests.\n')
        finally:
            process.terminate()
            try:process.wait(timeout=20)
            except subprocess.TimeoutExpired:process.kill();process.wait()

if __name__=='__main__':main()
