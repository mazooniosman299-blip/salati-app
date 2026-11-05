"""Verify exported launcher transparency/safe area and actual APK asset identity."""
from pathlib import Path
from PIL import Image
import io,sys,zipfile,hashlib,os,subprocess,re,xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1];res=root/'android/app/src/main/res'
asset=res/'drawable-nodpi/ic_salati_launcher.webp';body=asset.read_bytes()
im=Image.open(io.BytesIO(body)).convert('RGBA');assert im.size==(384,384)
# New explicit5Nov approval supersedes the129 transparent-white-only icon.
reference=root/'design-references/launcher-20261105/emerald-mosque-selected.png'
assert hashlib.sha256(reference.read_bytes()).hexdigest()=='9fe039bc20338ba3ad009098ca52ac573c63c8bb4066791ee170837f8c14b532'
assert im.getextrema()[3]==(255,255),'Selected coloured scene must fill the icon'
from PIL import ImageChops,ImageStat
original=Image.open(reference).convert('RGB').resize(im.size,Image.Resampling.LANCZOS)
error=sum(ImageStat.Stat(ImageChops.difference(original,im.convert('RGB'))).mean)/3
assert error<6.5,('Export diverges from exact selected artwork',error)
pixels=[im.getpixel((x,y)) for y in range(im.height) for x in range(im.width)]
assert sum(g>r*1.15 and g>b*1.05 for r,g,b,a in pixels)>len(pixels)*.15,'Selected emerald scene missing'
assert sum(r>180 and g>100 and b<155 for r,g,b,a in pixels)>len(pixels)*.05,'Selected golden mosque lighting missing'
ns='{http://schemas.android.com/apk/res/android}'
bg=ET.parse(res/'drawable/ic_salati_background.xml').getroot().find('solid')
assert bg.get(ns+'color')=='#00966B','Coloured adaptive backing must match selected scene'
fg=ET.parse(res/'drawable/ic_salati_foreground.xml').getroot()
assert all(fg.get(ns+'inset'+side)=='14%' for side in ['Left','Top','Right','Bottom'])
assert fg.find('bitmap').get(ns+'src')=='@drawable/ic_salati_launcher'
# Check the dome, crescent and both minaret tips against Android66dp safe circle.
for x,y in [(.50,.17),(.22,.25),(.78,.25),(.35,.45),(.65,.45),(.50,.82)]:
 assert ((x-.5)**2+(y-.5)**2)**.5*108*.72<=33,'Essential mosque silhouette clipped'
for version in ['drawable-v26','drawable-v33']:
 tree=ET.parse(res/version/'ic_salati.xml').getroot()
 assert tree.find('foreground').get(ns+'drawable')=='@drawable/ic_salati_foreground'
 if version=='drawable-v33':
  assert tree.find('monochrome').get(ns+'drawable')=='@drawable/ic_salati_monochrome','Do not tint an opaque bitmap into a solid square'
mono=ET.parse(res/'drawable/ic_salati_monochrome.xml').getroot()
assert mono.tag=='vector' and len(mono.findall('path'))>0,'OS themed icon must be a real silhouette'
if len(sys.argv)>1:
 apk=Path(sys.argv[1]);assert apk.stat().st_size<=25*1024*1024,'APK exceeds hosting limit'
 aapt=Path(os.environ['ANDROID_HOME'])/'build-tools/36.0.0/aapt'
 table=subprocess.check_output([str(aapt),'dump','--values','resources',str(apk)],text=True)
 # aapt optimizes entry filenames; resolve the actual compiled drawable symbol.
 entries=re.findall(r'(?m)^\s*resource 0x[0-9a-f]+ [^\n]*:drawable/ic_salati_launcher:[^\n]*\n\s*\(string8\) "([^"]+)"',table)
 with zipfile.ZipFile(apk) as z:
  assert len(entries)==1 and z.read(entries[0])==body,'APK does not contain the verified selected icon'
print('PASS exact approved emerald mosque export, full coloured background, adaptive safe area, separate Android33 silhouette and'+(' actual signed APK asset identity' if len(sys.argv)>1 else ' exported source')+'; SHA256 '+hashlib.sha256(body).hexdigest())
