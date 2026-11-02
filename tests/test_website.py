#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Validate the generated site, its complete menus and local links without network."""
import argparse
import base64
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit, unquote
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'website'))
from discovery import PAGES, SITE


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags=[]; self.refs=[]; self.ids=set(); self.h1=0; self.lang=None
        self.ld=''; self.in_ld=False
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs); self.tags.append((tag,attrs))
        if tag=='html': self.lang=attrs.get('lang')
        if tag=='h1': self.h1+=1
        if attrs.get('id'): self.ids.add(attrs['id'])
        for key in ('href','src'):
            if key in attrs:self.refs.append(attrs[key])
        if tag=='script' and attrs.get('type')=='application/ld+json':self.in_ld=True
    def handle_endtag(self,tag):
        if tag=='script':self.in_ld=False
    def handle_data(self,data):
        if self.in_ld:self.ld+=data
    def meta(self,name,attribute='name'):
        return [a.get('content') for t,a in self.tags if t=='meta' and a.get(attribute)==name]


def validate(site):
    pages={}; count=0; descriptions=set(); canonicals=set()
    for lang,prefix in [('en',''),('fr','fr/')]:
        for filename,*_ in PAGES:
            path=site/(prefix+filename); text=path.read_text()
            parsed=Page(); parsed.feed(text);pages[prefix+filename]=parsed
            assert parsed.lang==lang and parsed.h1==1, path
            assert 'contact@daylightlinux.ch' not in text, path
            assert 'info@daylightlinux.ch' in text, path
            assert '<details class="site-menu">' in text, path
            menu=re.search(r'<nav class="menu-panel".*?</nav>',text,re.S).group(0)
            for entry,*_ in PAGES:assert 'href="/'+prefix+entry+'"' in menu,(path,entry)
            canonical=[a['href'] for t,a in parsed.tags if t=='link' and a.get('rel')=='canonical']
            assert len(canonical)==1 and canonical[0] not in canonicals,path
            canonicals.add(canonical[0])
            description=parsed.meta('description');assert len(description)==1 and 35<=len(description[0])<=200,(path,description)
            assert (lang,description[0]) not in descriptions,('Duplicate description',path)
            descriptions.add((lang,description[0]))
            for key in ('og:title','og:description','og:url','og:image','og:image:alt'):
                assert len(parsed.meta(key,'property'))==1,(path,key)
            assert parsed.meta('twitter:card')==['summary_large_image'],path
            alternates={a.get('hreflang'):a['href'] for t,a in parsed.tags if t=='link' and a.get('hreflang')}
            assert set(alternates)=={'en','fr','x-default'},path
            structured=json.loads(parsed.ld);assert structured['@context']=='https://schema.org',path
            assert not any(k in parsed.ld for k in ('aggregateRating','reviewCount','ratingValue')),path
            csp=parsed.meta('Content-Security-Policy','http-equiv')[0]
            digest=base64.b64encode(hashlib.sha256(parsed.ld.encode()).digest()).decode()
            assert 'sha256-'+digest in csp,path
            assert 'unsafe-inline' not in csp,path
            assert not any('fonts.googleapis' in ref or 'google-analytics' in ref for ref in parsed.refs),path
            count+=1
        download=(site/(prefix+'download.html')).read_text()
        assert download.index('id="raspberry-pi"')<download.index('id="pc-live"')
        home=(site/(prefix+'index.html')).read_text().split('<main',1)[1]
        assert re.search(r'class="button" href="/'+prefix+r'raspberry-pi.html"',home)
        feed=ET.parse(site/(prefix+'feed.xml')).getroot()
        assert feed.tag=='rss' and len(feed.findall('./channel/item'))>=2
    links=0
    for name,page in pages.items():
        for ref in page.refs:
            url=urlsplit(ref)
            if url.scheme or url.netloc:continue
            if url.path.startswith(('/apt/','/old/site/')):continue
            target=(site/unquote(url.path).lstrip('/')) if url.path.startswith('/') else site/name
            if url.path and not url.path.startswith('/'):target=(site/name).parent/unquote(url.path)
            assert target.exists(),(name,ref,'missing local resource')
            if url.fragment:
                relative=str(target.relative_to(site));other=pages.get(relative)
                if other:assert url.fragment in other.ids,(name,ref,'missing fragment')
            links+=1
    sitemap=ET.parse(site/'sitemap.xml').getroot()
    listed={node.text for node in sitemap.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
    assert listed==canonicals,'Sitemap and canonical page inventory diverge'
    manifest=json.loads((site/'site-manifest.json').read_text())
    for name,digest in manifest['files'].items():
        assert hashlib.sha256((site/name).read_bytes()).hexdigest()==digest,('Bad manifest',name)
    with zipfile.ZipFile(site/'media/daylight-media-kit.zip') as archive:
        assert archive.testzip() is None
        assert not any(Path(n).suffix.lower() in ('.ttf','.otf','.woff','.woff2') for n in archive.namelist())
        assert 'README.txt' in archive.namelist()
    result={'pages':count,'local_links_checked':links,'sitemap_urls':len(listed),'languages':['en','fr'],'result':'PASS'}
    print(json.dumps(result,indent=2))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site',type=Path,default=ROOT/'dist/site')
    args=parser.parse_args();validate(args.site.resolve())
