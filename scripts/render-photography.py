#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Render branded landscapes; preserve source provenance and native resolution."""
import hashlib
import json
from pathlib import Path
import time
import urllib.error
import urllib.request
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
Image.MAX_IMAGE_PIXELS = 50000000


def obtain(item, cache):
    path = cache / (item['name'] + '.jpg')
    def matches():
        return path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256']
    if matches():
        return path
    errors = []
    for url in (item['url'], 'https://daylightlinux.ch/media/source/' + path.name):
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


def system_font(name, size):
    """Prefer installed DejaVu; fall back to Pillow's embedded scalable font."""
    for directory in ('/usr/share/fonts/truetype/dejavu', '/usr/share/fonts/TTF'):
        candidate = Path(directory) / name
        if candidate.is_file():
            try:
                return ImageFont.truetype(str(candidate), size)
            except OSError:
                pass
    return ImageFont.load_default(size=size)


def wordmark(image):
    """Use system fonts only for rasterization; no font files are redistributed."""
    result = image.copy().convert('RGBA')
    font = system_font('DejaVuSans-ExtraLight.ttf', 78)
    small = system_font('DejaVuSans.ttf', 26)
    x, y = 430, image.height - 300
    shade = Image.new('RGBA', image.size)
    draw = ImageDraw.Draw(shade)
    # A gradual bottom shade keeps the title readable without a rectangular panel.
    for row in range(image.height - 520, image.height):
        alpha = int(75 * (row - (image.height - 520)) / 520)
        draw.line((0, row, image.width, row), fill=(0, 0, 0, alpha))
    result = Image.alpha_composite(result, shade)
    draw = ImageDraw.Draw(result)
    draw.text((x, y), 'Daylight Linux', font=font, fill=(247, 244, 236), stroke_width=0)
    draw.text((x + 4, y + 108), 'G N U / L I N U X', font=small, fill=(242, 184, 71))
    draw.line((x + 4, y + 166, x + 112, y + 166), fill=(242, 184, 71), width=4)
    return result.convert('RGB')


def main():
    cache = ROOT / 'dist/photography-source'
    cache.mkdir(parents=True, exist_ok=True)
    output = ROOT / 'assets/wallpapers'
    output.mkdir(parents=True, exist_ok=True)
    art = json.loads((ROOT / 'assets/generated-art.json').read_text())
    path = ROOT / art['path']
    if hashlib.sha256(path.read_bytes()).hexdigest() != art['sha256']:
        raise ValueError('Approved generated artwork integrity check failed')
    with Image.open(path) as original:
        mountain = original.convert('RGB')
        if mountain.size != tuple(art['dimensions']):
            raise ValueError('Approved artwork dimensions changed')
    items = json.loads((ROOT / 'assets/photography.json').read_text())
    images = {}
    for item in items:
        with Image.open(obtain(item, cache)) as original:
            image = ImageOps.exif_transpose(original).convert('RGB')
            if image.width < 3840 or image.height < 2160:
                raise ValueError('Never claim an upscaled photograph is native 4K')
            images[item['name']] = wordmark(ImageOps.fit(image, (3840, 2160), method=Image.Resampling.LANCZOS, centering=(0.5, 0.48)))
    dark = ImageEnhance.Brightness(ImageEnhance.Color(mountain).enhance(0.85)).enhance(0.55)
    terminal = ImageEnhance.Brightness(dark).enhance(0.45)
    editions = [('daylight-mountains', mountain), ('daylight-sunrise', images['mountain-sunrise']), ('daylight-himalaya', images['himalaya-sunrise']), ('daylight-night', dark), ('daylight-terminal', terminal)]
    for name, image in editions:
        image.save(output / (name + '.jpg'), quality=92, optimize=True, progressive=True)
    boot = ImageOps.fit(mountain, (640, 480), method=Image.Resampling.LANCZOS).convert('RGBA')
    overlay = Image.new('RGBA', boot.size, (7, 14, 23, 135))
    boot = Image.alpha_composite(boot, overlay)
    draw = ImageDraw.Draw(boot)
    draw.text((48, 42), 'Daylight Linux', font=system_font('DejaVuSans.ttf', 38), fill=(247,244,236))
    draw.text((50, 96), 'Debian 13  /  Live session  /  GNU GPL v3', font=system_font('DejaVuSans.ttf', 14), fill=(242,184,71))
    boot.convert('RGB').save(ROOT / 'assets/branding/boot-splash.png')
    credits = ['Daylight Linux — landscape artwork', 'Developer: Hamdy Abou El Anein', 'Contact: info@daylightlinux.ch', '', 'daylight-mountains.jpg, daylight-night.jpg, daylight-terminal.jpg:', 'Approved AI-generated photorealistic Alpine-lake sunrise, with the Daylight Linux wordmark.', 'This is generated scenery, not a documentary photograph or an identified location.', 'Native delivered dimensions: 1672 x 941. It is not advertised as native 4K.', 'The dark and terminal editions are exposure-adjusted derivatives.', 'Daylight project artwork: GPL-3.0-only to the extent copyright applies.', 'Source SHA256: ' + art['sha256'], '', 'daylight-sunrise.jpg and daylight-himalaya.jpg:', 'Real CC0 photographs cropped to 3840 x 2160, with a rasterized Daylight Linux wordmark.', 'System fonts are used during rendering; font files are not distributed.', 'All exported JPEGs omit camera EXIF data.', '']
    for item in items:
        credits += [item['name'] + ' — ' + item['author'], item['source'], 'Original SHA256: ' + item['sha256'], 'License: https://creativecommons.org/publicdomain/zero/1.0/', '']
    (output / 'CREDITS.txt').write_text('\n'.join(credits) + '\n')
    print('Rendered five branded landscape editions; source identities and native resolutions preserved.')


if __name__ == '__main__':
    main()
