"""Extract approved original screenshot pixels only; no synthesis, retouching or resampling."""
from pathlib import Path
from PIL import Image
import hashlib,json
root=Path(__file__).resolve().parents[1]
source=root/'design-references/user-mosque-original.png'
box=(460,78,1580,400)
with Image.open(source) as im:
 assert im.size==(2048,684),'Crop coordinates are specific to the supplied approved original.'
 crop=im.crop(box)
 output=root/'dist/images/mosque-reference-original.png';crop.save(output)
 native=root/'android/app/src/main/res/drawable-nodpi/widget_reference_mosque.png';native.parent.mkdir(exist_ok=True);native.write_bytes(output.read_bytes())
meta={'source':'User uploaded Salati_Original_Mosque_References.zip / 01_original_widget_reference.png','source_repository_path':str(source.relative_to(root)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'crop_box':box,'size':list(crop.size),'web_asset':'images/mosque-reference-original.png','native_asset':str(native.relative_to(root)),'asset_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'processing':'Lossless PNG crop only. No new image, generated replacement, inpainting, resampling or color changes.','day_night':'The same approved pixels are used in both modes; Android changes only its text-legibility overlay.'}
(root/'design-references/mosque-crop.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
(root/'dist/images/SELECTED-MOSQUE-SOURCE.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
print('Extracted exact original pixels:',crop.size)
