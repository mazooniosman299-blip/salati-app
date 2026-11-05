"""Verify exported launcher transparency/safe area and actual APK asset identity."""
from pathlib import Path
from PIL import Image
import io,sys,zipfile,hashlib,os,subprocess,re,xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1];res=root/'android/app/src/main/res'
asset=res/'drawable-nodpi/ic_salati_launcher.webp';body=asset.read_bytes()
im=Image.open(io.BytesIO(body)).convert('RGBA');assert im.size==(512,512)
# Explicit latest approval: original white mark, real user-selected sunset photo2.
reference=root/'design-references/mosque-20261105/fahrul-azmi-sunset.webp'
mark=res/'drawable-nodpi/ic_salati_mark.webp'
assert hashlib.sha256(reference.read_bytes()).hexdigest()=='9b111a3f505da38e4871b069353322b4e3510c20dac7af213664a95e8c70f97e'
assert hashlib.sha256(mark.read_bytes()).hexdigest()=='7ccb9017778d5bd4637dc1d33b98fc1108a16e100f2f50ff5917cf0fde4b458a'
from PIL import ImageChops,ImageStat
scene=Image.open(reference).convert('RGB').crop((180,0,899,719)).resize(im.size,Image.Resampling.LANCZOS).convert('RGBA')
scene=Image.alpha_composite(scene,Image.new('RGBA',im.size,(0,0,0,40)))
logo=Image.open(mark).convert('RGBA').resize((328,328),Image.Resampling.LANCZOS)
scene.alpha_composite(logo,(92,92))
error=sum(ImageStat.Stat(ImageChops.difference(scene.convert('RGB'),im.convert('RGB'))).mean)/3
assert error<6.5,('Export diverges from original mark and selected real photograph',error)
assert im.getextrema()[3]==(255,255),'Real photograph must fill the background'
assert body==(root/'dist/icon-512.webp').read_bytes(),'PWA and native must use identical canonical tile'
small=Image.open(root/'dist/icon-192.png').convert('RGB')
assert small.tobytes()==im.convert('RGB').resize((192,192),Image.Resampling.LANCZOS).tobytes()
import base64,json
svg=(root/'dist/icon.svg').read_text();assert base64.b64decode(re.search(r'base64,([^"\s]+)',svg)[1])==body
assert 'src="icon-192.png"' in (root/'dist/index.html').read_text(),'In-app brand must use the same graphic'
manifest=json.loads((root/'dist/manifest.json').read_text());assert any(i['src']=='icon-512.webp' and i['type']=='image/webp' for i in manifest['icons'])
ns='{http://schemas.android.com/apk/res/android}'
bg=ET.parse(res/'drawable/ic_salati_background.xml').getroot()
assert bg.tag=='bitmap' and bg.get(ns+'src')=='@drawable/ic_salati_launcher'
fg=ET.parse(res/'drawable/ic_salati_foreground.xml').getroot()
assert fg.tag=='shape' and fg.find('solid').get(ns+'color')=='#00000000','Composite must not receive a duplicate logo or inset'
# The original mark's visible pixels must survive Android's66dp safe circle.
alpha=logo.getchannel('A')
for y in range(328):
 for x in range(328):
  if alpha.getpixel((x,y))>127:
   assert (((x+92-256)/512)**2+((y+92-256)/512)**2)**.5*108<=33,'Original mark outside adaptive safe circle'
for version in ['drawable-v26','drawable-v33']:
 tree=ET.parse(res/version/'ic_salati.xml').getroot()
 assert tree.find('background').get(ns+'drawable')=='@drawable/ic_salati_background'
 assert tree.find('foreground').get(ns+'drawable')=='@drawable/ic_salati_foreground'
 if version=='drawable-v33':assert tree.find('monochrome').get(ns+'drawable')=='@drawable/ic_salati_monochrome'
mono=ET.parse(res/'drawable/ic_salati_monochrome.xml').getroot()
assert mono.tag=='inset' and mono.find('bitmap').get(ns+'src')=='@drawable/ic_salati_mark','OS tint must use original transparent silhouette, not an opaque photo'
assert Image.open(mark).convert('RGBA').getextrema()[3]==(0,255)
if len(sys.argv)>1:
 apk=Path(sys.argv[1])
 aapt=Path(os.environ['ANDROID_HOME'])/'build-tools/36.0.0/aapt'
 badging=subprocess.check_output([str(aapt),'dump','badging',str(apk)],text=True)
 application=re.search(r"package: name='([^']+)'",badging)[1]
 assert application in ['com.salati.prayer','com.salati.prayer.preview']
 if application=='com.salati.prayer':assert apk.stat().st_size<=25*1024*1024,'Public APK exceeds hosting limit'
 table=subprocess.check_output([str(aapt),'dump','--values','resources',str(apk)],text=True)
 # aapt optimizes entry filenames; resolve the actual compiled drawable symbol.
 entries=re.findall(r'(?m)^\s*resource 0x[0-9a-f]+ [^\n]*:drawable/ic_salati_launcher:[^\n]*\n\s*\(string8\) "([^"]+)"',table)
 with zipfile.ZipFile(apk) as z:
  assert len(entries)==1 and z.read(entries[0])==body,'APK does not contain the verified selected icon'
print('PASS selected real sunset photo with original white mark, unified header/PWA/native identity, adaptive safe area, separate Android33 silhouette and'+(' actual APK asset identity (signing checked separately)' if len(sys.argv)>1 else ' exported source')+'; SHA256 '+hashlib.sha256(body).hexdigest())
