#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Verify real Chromium/noVNC transport AND a running, visibly rendered live desktop."""
import hashlib
from pathlib import Path
import shutil
import subprocess
import time
import urllib.request
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent.parent


def main():
    isos=sorted((ROOT/'dist').glob('daylight-live_*_amd64.iso'))
    if len(isos)!=1:
        raise RuntimeError('Exactly one candidate ISO is required')
    iso=isos[0]
    value=hashlib.sha256()
    with iso.open('rb') as stream:
        for block in iter(lambda:stream.read(4*1024*1024),b''):
            value.update(block)
    output=ROOT/'dist/browser-demo'
    output.mkdir(parents=True,exist_ok=True)
    browser=shutil.which('google-chrome') or shutil.which('chromium')
    if not browser:
        raise RuntimeError('A real Chromium browser is required; do not silently skip')
    with (output/'demo.log').open('w') as log:
        process=subprocess.Popen(['python3',str(ROOT/'demo/run.py'),'--iso',str(iso),'--sha256',value.hexdigest(),'--duration','900'],stdout=log,stderr=subprocess.STDOUT)
        try:
            for _ in range(100):
                if process.poll() is not None:
                    raise RuntimeError('Demo exited before its HTTP frontend started')
                try:
                    with urllib.request.urlopen('http://127.0.0.1:6080/vnc.html',timeout=2) as response:
                        if response.status==200:
                            break
                except OSError:
                    time.sleep(.2)
            else:
                raise RuntimeError('noVNC HTTP frontend did not start')
            with sync_playwright() as engine:
                instance=engine.chromium.launch(executable_path=browser,headless=True,args=['--disable-dev-shm-usage'])
                page=instance.new_page(viewport={'width':1366,'height':900})
                try:
                    page.goto('http://127.0.0.1:6080/vnc.html?autoconnect=true&resize=scale',wait_until='domcontentloaded')
                    page.wait_for_function("document.documentElement.classList.contains('noVNC_connected')",timeout=60000)
                    deadline=time.monotonic()+600
                    while time.monotonic()<deadline:
                        if process.poll() is not None:
                            raise RuntimeError('Demo exited before desktop readiness')
                        if 'DAYLIGHT_DESKTOP_READY:' in (output/'demo.log').read_text(errors='replace'):
                            break
                        time.sleep(2)
                    else:
                        raise RuntimeError('VNC connected but the real live desktop never became ready')
                    # A positive guest readiness signal alone is not a rendered browser frame.
                    page.wait_for_function("""() => {
                        const canvas=document.querySelector('canvas');
                        if(!canvas || canvas.width<640 || canvas.height<480) return false;
                        const pixels=canvas.getContext('2d').getImageData(0,0,canvas.width,canvas.height).data;
                        const colors=new Set();
                        const stride=Math.max(4,Math.floor(pixels.length/12000/4)*4);
                        for(let i=0;i<pixels.length;i+=stride) colors.add((pixels[i]<<16)|(pixels[i+1]<<8)|pixels[i+2]);
                        return colors.size>128;
                    }""",timeout=30000)
                    page.wait_for_timeout(2000)
                    page.screenshot(path=str(output/'browser.png'),full_page=True)
                except Exception:
                    page.screenshot(path=str(output/'browser-failed.png'),full_page=True)
                    raise
                finally:
                    page.context.close()
                    instance.close()
            (output/'result.txt').write_text('PASS: real Chromium connected through noVNC/WebSocket, waited for the actual live user/Fluxbox/Conky readiness report, and rendered a nonblank desktop frame from the candidate ISO.\nISO SHA256: '+value.hexdigest()+'\n')
        finally:
            process.terminate()
            try:
                process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


if __name__=='__main__':
    main()
