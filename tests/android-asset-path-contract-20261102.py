#!/usr/bin/env python3
"""Fail Android APK packaging if internal local HTML links or CSS paths 404.

The Android WebView origin intercepts only /assets/www/*; rooted website
paths must be remapped in the APK copy, not on the public website.
"""
from pathlib import Path
import re
from collections import Counter

root=Path(__file__).resolve().parents[1]
site=root/'dist'
pkg=root/'android/app/src/main/assets/www'
java=(root/'android/app/src/main/java/com/salati/prayer/MainActivity.java').read_text(encoding='utf-8')
assert 'p.startsWith("/assets/www/")' in java
assert 'trustedResourceOrigin' in java
assert pkg.is_dir(),'Run scripts/prepare-android.py before contract test'
assert (pkg/'index.html').is_file()
assert 'https://salati-app-ctc.pages.dev/downloads/salati-1.0.121.apk' in (pkg/'index.html').read_text(encoding='utf-8')
# Native app may link external downloads; those are intentionally not package assets.
local=re.compile(r'\b(?:src|href|poster|action)\s*=\s*["\x27](/[^"\x27]+)["\x27]',re.I)
counter=Counter()
for h in pkg.rglob('*.html'):
 text=h.read_text(encoding='utf-8')
 for url in local.findall(text):
  if url.startswith('//'):continue
  clean=url.split('?',1)[0].split('#',1)[0]
  if clean.startswith('/assets/www/'):
   rel=clean[len('/assets/www/'):]
   assert (pkg/rel).is_file(),(h,url,'rewritten native asset does not exist')
   counter['valid_local']+=1
  elif (pkg/clean.lstrip('/')).is_file():
   raise AssertionError((h,url,'native HTML still points outside Android trusted asset origin'))
  else:
   counter['unbundled_root_urls']+=1
 assert not re.search(r'(?<!assets/www)/city-pages\.css',text) if h.name=='index.html' else True
assert counter['valid_local']>=833,counter
assert counter['unbundled_root_urls']==0, ('Unresolved Android-native root URL, expected HTTPS redirect for downloads',counter)
for test in ('index.html','ar/about.html','en/prayer-times/muscat.html','privacy.html'):
 assert (pkg/test).is_file(),test
print('PASS NATIVE WEBVIEW ASSET PATHS',dict(counter),'all rooted packaged assets use /assets/www/ with existing files')
