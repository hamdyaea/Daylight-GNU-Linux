#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: contact@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Render local 4K wallpapers from pinned, credited CC0 photographs. No hotlinking."""
import hashlib
import json
from pathlib import Path
import time
import urllib.error
import urllib.request
from PIL import Image, ImageEnhance, ImageOps

ROOT = Path(__file__).resolve().parent.parent
Image.MAX_IMAGE_PIXELS = 50000000


def obtain(item, cache):
    path = cache / (item['name'] + '.jpg')
    def matches():
        return path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256']
    if matches():
        return path
    urls = [item['url'], 'https://daylightlinux.ch/media/source/' + path.name]
    errors = []
    for url in urls:
        for attempt in range(3):
            try:
                request = urllib.request.Request(url, headers={'User-Agent': 'DaylightLinux/5 (open-source wallpaper packaging)'})
                with urllib.request.urlopen(request, timeout=45) as response:
                    data = response.read(25000001)
                if len(data) > 25000000 or hashlib.sha256(data).hexdigest() != item['sha256']:
                    raise ValueError('Source photograph checksum/size mismatch')
                temporary = path.with_suffix('.partial')
                temporary.write_bytes(data)
                temporary.replace(path)
                return path
            except (OSError, ValueError) as error:
                errors.append(f'{url}: {error}')
                if isinstance(error, urllib.error.HTTPError) and error.code in (403, 404):
                    break
                time.sleep(2 ** attempt)
    raise RuntimeError('Cannot obtain the exact licensed photograph: ' + '; '.join(errors))


def main():
    cache = ROOT / 'dist/photography-source'
    cache.mkdir(parents=True, exist_ok=True)
    output = ROOT / 'assets/wallpapers'
    output.mkdir(parents=True, exist_ok=True)
    items = json.loads((ROOT / 'assets/photography.json').read_text())
    images = {}
    for item in items:
        path = obtain(item, cache)
        with Image.open(path) as original:
            image = ImageOps.exif_transpose(original).convert('RGB')
            if image.width < 3840 or image.height < 2160:
                raise ValueError('Do not upscale a low-resolution photograph and claim native 4K')
            images[item['name']] = ImageOps.fit(image, (3840, 2160), method=Image.Resampling.LANCZOS, centering=(0.5, 0.48))
    mountain = images['himalaya-sunrise']
    sunrise = images['mountain-sunrise']
    dark = ImageEnhance.Brightness(ImageEnhance.Color(mountain).enhance(0.75)).enhance(0.48)
    terminal = ImageEnhance.Brightness(dark).enhance(0.45)
    for name, image in [('daylight-mountains', mountain), ('daylight-sunrise', sunrise), ('daylight-night', dark), ('daylight-terminal', terminal)]:
        image.save(output / (name + '.jpg'), quality=88, optimize=True, progressive=True)
    credits = ['# Daylight photographic wallpaper credits', '', 'Photographic assets are CC0-1.0; Daylight source code remains GPL-3.0-only.', 'The originals are real photographs, not generated scenery.', 'Desktop versions are cropped to 3840x2160 and re-encoded without EXIF.', 'The dark and terminal variants are exposure-adjusted derivatives, not photographs taken at night.', 'No text or logo is burned into the photographs, so cover scaling cannot crop a wordmark.', '']
    for item in items:
        credits += [item['name'] + ' — ' + item['author'], item['source'], 'Original SHA256: ' + item['sha256'], 'License: https://creativecommons.org/publicdomain/zero/1.0/', '']
    (output / 'CREDITS.txt').write_text('\n'.join(credits))
    print('Verified photographs rendered: 3840x2160; credits retained; no network requests at desktop startup.')


if __name__ == '__main__':
    main()
