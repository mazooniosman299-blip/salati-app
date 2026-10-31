#!/usr/bin/env python3
"""Enforce that the downloaded Android APK embeds the website shipped beside it."""
from pathlib import Path
import sys,zipfile,hashlib
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
apk=Path(sys.argv[1]) if len(sys.argv)>1 else None
if not apk or not apk.is_file():raise SystemExit('Expected APK filename')
if apk.stat().st_size>25*1024*1024:raise SystemExit('Signed APK exceeds Pages 25 MiB limit')
required=[
 'index.html','app-v1.0.109.js','selection-refinement-20261101.css',
 'mushaf-legibility-20261101.css','user-fixes-20261101.css',
 'quran-mushaf-markers-20261101.js',
]
with zipfile.ZipFile(apk) as z:
 names=set(z.namelist())
 for rel in required:
    if 'assets/www/'+rel not in names:raise SystemExit('APK missing current UI asset '+rel)
 checked=0
 for rel in required:
    web=(DIST/rel).read_bytes()
    native=z.read('assets/www/'+rel)
    if hashlib.sha256(web).digest()!=hashlib.sha256(native).digest():
       raise SystemExit('APK embeds stale '+rel+'; abort publication')
    checked+=1
 # Check all shared first-party styles and scripts, preventing future invisible drift.
 for f in list(DIST.glob('*.css'))+list(DIST.glob('*.js')):
    if 'assets/www/'+f.name not in names:continue
    if f.read_bytes()!=z.read('assets/www/'+f.name):
       raise SystemExit('APK has outdated stylesheet or script '+f.name)
    checked+=1
print('PASS: verified',checked,'website/native assets match byte-for-byte')
