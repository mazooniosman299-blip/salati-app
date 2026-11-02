"""Compare the ACTUAL current Android APK against prepared WebView assets.

Never require retired -v1.0.109 styles or claim a debug-signed APK is the
user-updateable release. Verify all staged bytes and original mosque artwork.
"""
from pathlib import Path
import sys, zipfile, io, os, re, subprocess, shutil, base64
from PIL import Image
root=Path(__file__).resolve().parents[1]
apk=Path(sys.argv[1]) if len(sys.argv)>1 else root/'android/app/build/outputs/apk/debug/app-debug.apk'
payload=root/'android/app/src/main/assets/www'
source=root/'dist'
assert apk.is_file() and apk.stat().st_size>1000000, 'No real Android APK'
assert (payload/'salati-ui.css').is_file(), 'Canonical CSS missing from native WebView'
assert not (payload/'preview-sample-location-20261101.js').exists(), 'Preview GPS setter leaked into production native assets'
with zipfile.ZipFile(apk) as z:
 names=set(z.namelist())
 checked=0
 for file in sorted(payload.rglob('*')):
  if file.is_file():
   relative=file.relative_to(payload).as_posix()
   assert z.read('assets/www/'+relative)==file.read_bytes(), relative
   checked+=1
 assert 'assets/www/preview-sample-location-20261101.js' not in names, 'Preview location setter in APK'
 for name in ('salati-ui.css','app-v1.0.109.js','public-pages.css','public-page-theme.js','privacy.html','city-pages.css'):
  assert 'assets/www/'+name in names, 'Missing active packaged '+name
 for name in ('app-v1.0.109.js','public-pages.css','public-page-theme.js','privacy.html','city-pages.css'):
  assert z.read('assets/www/'+name)==(source/name).read_bytes(),name
 native_css=z.read('assets/www/salati-ui.css').decode('utf-8')
 web_css=(source/'salati-ui.css').read_text(encoding='utf-8')
 for art in ('quran-surah-ornament.svg','quran-ayah-rosette.svg'):
  original=(source/'images'/art).read_bytes()
  old='url("images/'+art+'")'
  assert web_css.count(old)==1,art
  web_css=web_css.replace(old,'url("data:image/svg+xml;base64,'+base64.b64encode(original).decode('ascii')+'")')
 assert native_css==web_css, 'Native CSS differs from canonical CSS outside approved two-original-SVG adaptation'
 assert '!important' not in native_css, 'Legacy force priority leaked into Android'
 assert b'preview-sample-location-20261101.js' not in z.read('assets/www/index.html')
 assert b'href="salati-ui.css"' in z.read('assets/www/index.html')
 for legacy in ('style-v1.0.109.css','light-theme-v1.0.109.css','salati-design-v1.0.109.css','reference-layout-v1.0.109.css'):
  assert 'assets/www/'+legacy not in names,'Old inactive CSS still packaged: '+legacy
 native_entry=next((n for n in z.namelist() if n.endswith('/widget_reference_mosque.png')),None)
 if native_entry is None:
  aapt=shutil.which('aapt2')
  if not aapt:
   sdk=Path(os.environ.get('ANDROID_HOME',os.environ.get('ANDROID_SDK_ROOT','')))
   installed=sorted((sdk/'build-tools').glob('*/aapt2'))
   assert installed,'Set ANDROID_HOME to verify optimized widget image'
   aapt=str(installed[-1])
  table=subprocess.check_output([aapt,'dump','resources',str(apk)],text=True)
  m=re.search(r'drawable/widget_reference_mosque\n\s+\(nodpi\) \(file\) (\S+)',table)
  assert m,'Compiled original widget mosque resource not found'
  native_entry=m[1]
 with Image.open(io.BytesIO(z.read(native_entry))) as packaged, Image.open(source/'images/mosque-reference-original.png') as approved:
  assert packaged.convert('RGBA').tobytes()==approved.convert('RGBA').tobytes(),'Native mosque pixels changed'
print('PASS current Android APK',checked,'byte-verified staged assets; zero demo GPS; matching CSS/JS and original mosque artwork.')
