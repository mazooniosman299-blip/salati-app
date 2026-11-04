"""Verify exported launcher transparency/safe area and actual APK asset identity."""
from pathlib import Path
from PIL import Image
import io,sys,zipfile,hashlib,os,subprocess,re,xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1];res=root/'android/app/src/main/res'
asset=res/'drawable-nodpi/ic_salati_launcher.webp';body=asset.read_bytes()
im=Image.open(io.BytesIO(body)).convert('RGBA');assert im.size==(384,384)
opaque=[]
for y in range(im.height):
 for x in range(im.width):
  r,g,b,a=im.getpixel((x,y))
  if a>=128:
   assert min(r,g,b)>230,'Selected white emblem must not contain an opaque dark background'
   opaque.append((x,y))
assert opaque and im.getpixel((0,0))[3]==0
# 18% adaptive inset leaves64% of108dp: all essential ink fits the66dp safe circle.
radius=max(((x+0.5-192)**2+(y+0.5-192)**2)**0.5 for x,y in opaque)*108*.64/384
assert radius<=33,('Adaptive icon would clip under a circular mask',radius)
ns='{http://schemas.android.com/apk/res/android}'
bg=ET.parse(res/'drawable/ic_salati_background.xml').getroot().find('solid')
assert bg.get(ns+'color')=='#00000000','No black launcher backplate'
for version in ['drawable-v26','drawable-v33']:
 tree=ET.parse(res/version/'ic_salati.xml').getroot()
 assert tree.find('foreground').get(ns+'drawable')=='@drawable/ic_salati_foreground'
 if version=='drawable-v33':assert tree.find('monochrome') is not None
if len(sys.argv)>1:
 apk=Path(sys.argv[1]);assert apk.stat().st_size<=25*1024*1024,'APK exceeds hosting limit'
 aapt=Path(os.environ['ANDROID_HOME'])/'build-tools/36.0.0/aapt'
 table=subprocess.check_output([str(aapt),'dump','--values','resources',str(apk)],text=True)
 # aapt optimizes entry filenames; resolve the actual compiled drawable symbol.
 entries=re.findall(r'(?m)^\s*resource 0x[0-9a-f]+ [^\n]*:drawable/ic_salati_launcher:[^\n]*\n\s*\(string8\) "([^"]+)"',table)
 with zipfile.ZipFile(apk) as z:
  assert len(entries)==1 and z.read(entries[0])==body,'APK does not contain the verified selected icon'
print('PASS transparent white selected launcher, circular adaptive safe area, Android33 themed support and'+(' actual signed APK asset identity' if len(sys.argv)>1 else ' exported source')+'; SHA256 '+hashlib.sha256(body).hexdigest())
