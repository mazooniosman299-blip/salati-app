"""Validate the static, canonical public page inventory and crawler files."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import xml.etree.ElementTree as ET
import hashlib
import subprocess
import json

root = Path(__file__).resolve().parents[1]
dist = root / 'dist'
origin = 'https://salati-world-prayer.sprytitan65.chatgpt.site'
expected = {origin+'/', origin+'/privacy.html'} | {origin+'/'+lang+'/prayer-times/'+c['slug']+'.html' for c in json.loads((root/'city-pages/cities.json').read_text()) for lang in ['ar','en']} | {origin+'/'+lang+'/'+suffix for lang in ['ar','en'] for suffix in ['prayer-times/index.html','prayer-times/calculation-guide.html','about.html']}
class Head(HTMLParser):
    def __init__(self):
        super().__init__(); self.canonicals=[]; self.robots=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='link' and a.get('rel')=='canonical': self.canonicals.append(a['href'])
        if tag=='meta' and a.get('name','').lower() in ('robots','googlebot'): self.robots.append(a.get('content','').lower())
xml=ET.parse(dist/'sitemap.xml')
assert xml.getroot().tag=='{http://www.sitemaps.org/schemas/sitemap/0.9}urlset'
urls=[x.text for x in xml.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
assert len(urls)==len(set(urls)) and set(urls)==expected
robots=RobotFileParser(); robots.parse((dist/'robots.txt').read_text().splitlines())
assert robots.site_maps()==[origin+'/sitemap.xml']
for url in urls:
    path=urlparse(url).path
    file=dist/('index.html' if path=='/' else path.lstrip('/'))
    assert file.is_file()
    head=Head(); head.feed(file.read_text())
    assert head.canonicals==[url]
    assert all('noindex' not in r and 'none' not in r.split(',') for r in head.robots)
    assert robots.can_fetch('Googlebot',url) and robots.can_fetch('*',url)
# Preserve crawler files and Google's original proof through the actual build.
files=[dist/'sitemap.xml',dist/'robots.txt',dist/'google611146e9ceec162a.html']
before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
subprocess.run(['npm','run','build'],cwd=root,check=True)
assert before=={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
original=subprocess.check_output(['git','show','HEAD:dist/google611146e9ceec162a.html'],cwd=root)
assert files[-1].read_bytes()==original
print(f'PASS: {len(urls)} real canonical pages; valid sitemap; Googlebot allowed; sitemap declared; no noindex; build preserves crawler files and original Google proof.')
