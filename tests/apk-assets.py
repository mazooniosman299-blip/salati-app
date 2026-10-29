"""Check the built APK against the prepared Android payload (which adapts web-only help text)."""
from pathlib import Path
import sys,zipfile,io,os,re,subprocess,shutil
from PIL import Image
root=Path(__file__).resolve().parents[1]
apk=Path(sys.argv[1]) if len(sys.argv)>1 else root/'android/app/build/outputs/apk/debug/app-debug.apk'
payload=root/'android/app/src/main/assets/www'
with zipfile.ZipFile(apk) as z:
 for file in sorted(payload.rglob('*')):
  if file.is_file():
   relative=file.relative_to(payload).as_posix()
   assert z.read('assets/www/'+relative)==file.read_bytes(),relative
 for name in ['style-v1.0.104.css','light-theme-v1.0.104.css','salati-design-v1.0.104.css','reference-layout-v1.0.104.css','app-v1.0.104.js','public-pages.css','public-page-theme.js','privacy.html']:
  assert z.read('assets/www/'+name)==(root/'dist'/name).read_bytes(),name
 native_entry=next((n for n in z.namelist()if n.endswith('/widget_reference_mosque.png')),None)
 if native_entry is None:
  # Release resource optimization renames PNG paths; resolve by resource ID/name.
  aapt=shutil.which('aapt2')
  if not aapt:
   sdk=Path(os.environ.get('ANDROID_HOME',os.environ.get('ANDROID_SDK_ROOT','')))
   installed=sorted((sdk/'build-tools').glob('*/aapt2'))
   assert installed,'Set ANDROID_HOME to verify optimized release resources'
   aapt=str(installed[-1])
  table=subprocess.check_output([aapt,'dump','resources',str(apk)],text=True)
  match=re.search(r'drawable/widget_reference_mosque\n\s+\(nodpi\) \(file\) (\S+)',table)
  assert match,'Approved widget image resource is missing'
  native_entry=match[1]
 with Image.open(io.BytesIO(z.read(native_entry))) as packaged,Image.open(root/'dist/images/mosque-reference-original.png') as approved:
  assert packaged.convert('RGBA').tobytes()==approved.convert('RGBA').tobytes(),'Compiled native image pixels differ from approved original crop'
 html=z.read('assets/www/index.html')
 assert b'app-v1.0.104.js' in html and b'style-v1.0.104.css' in html
 assert b'var(--control-fill);color:var(--control-ink);border-radius:20px' in z.read('assets/www/style-v1.0.104.css')
print('PASS: all prepared Android assets match APK bytes; current web code/style/public-page assets match their source; entrypoint uses 1.0.104.')
