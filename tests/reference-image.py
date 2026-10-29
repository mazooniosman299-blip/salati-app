"""The supplied mosque is reused exactly, not regenerated or replaced by an old asset."""
from pathlib import Path
from PIL import Image
from lxml import html
import json,hashlib
root=Path(__file__).resolve().parents[1]
meta=json.loads((root/'design-references/mosque-crop.json').read_text())
source=root/meta['source_repository_path'];web=root/'dist'/meta['web_asset'];native=root/meta['native_asset']
assert hashlib.sha256(source.read_bytes()).hexdigest()==meta['source_sha256']
with Image.open(source) as original,Image.open(web) as asset:
 expected=original.crop(tuple(meta['crop_box']))
 assert asset.size==expected.size
 assert asset.mode==expected.mode and asset.tobytes()==expected.tobytes(),'Every asset pixel must match the selected original crop'
assert web.read_bytes()==native.read_bytes(),'Web and Android must share the same approved image'
page=html.fromstring((root/'dist/index.html').read_text());photo=page.xpath('//div[@class="hero-picture"]/img')[0]
assert photo.get('src')==meta['web_asset'] and photo.get('hidden') is None,'Web must display the actual approved image'
assert 'data-reference-image-pending' not in (root/'dist/index.html').read_text()
import xml.etree.ElementTree as ET
ns='{http://schemas.android.com/apk/res/android}'
layout=ET.parse(root/'android/app/src/main/res/layout/prayer_widget.xml')
scenery=next(e for e in layout.iter()if e.get(ns+'id')=='@+id/widget_scenery')
assert scenery.get(ns+'visibility','visible')=='visible'
assert scenery.get(ns+'src')=='@drawable/widget_reference_mosque'
java=(root/'android/app/src/main/java/com/salati/prayer/PrayerWidget.java').read_text()
assert 'daylight?R.drawable.widget_mosque_day' not in java and 'R.drawable.widget_reference_mosque' in java
assert './images/mosque-reference-original.png' in (root/'dist/sw.js').read_text(),'Approved image must be precached offline'
print('PASS: exact original pixel crop, unchanged native/web image identity, active bindings and offline asset cache.')
