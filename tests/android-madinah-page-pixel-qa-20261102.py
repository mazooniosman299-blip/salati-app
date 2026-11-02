#!/usr/bin/env python3
"""Real native Android WebView image-only proof: printed Madinah ornate plates.

Do not treat old HTML text fallback as an acceptable pass. Require both
original green and magenta decorative ink visible in the Android screenshot,
and a nontrivial cream parchment area. No OCR or any Quran text transcription.
"""
from pathlib import Path
from PIL import Image
import json,sys

file=Path(sys.argv[1] if len(sys.argv)>1 else 'reports/android-webview-20261102/mushaf-reader.png')
assert file.is_file(),('Native Quran screenshot missing',str(file))
im=Image.open(file).convert('RGB')
w,h=im.size
assert w>=320 and h>=650,(w,h)
green=magenta=cream=0
for y in range(int(h*.12),int(h*.83),2):
 for x in range(int(w*.06),int(w*.94),2):
  r,g,b=im.getpixel((x,y))
  if 22<r<200 and 56<g<204 and b<185 and g>r*1.18 and g>b*.94:green+=1
  if 90<r<247 and 20<g<170 and 50<b<225 and r>g*1.32 and b>g*1.15:magenta+=1
  if r>216 and g>200 and b>175 and max(r,g,b)-min(r,g,b)<65:cream+=1
report={'screen':[w,h],'genuine_madinah_green_pixels':green,'genuine_madinah_magenta_pixels':magenta,'cream_paper_pixels':cream,'preview_only':True}
file.with_suffix('.madinah-pixels.json').write_text(json.dumps(report,indent=2)+'\n')
assert green>=100 and magenta>=30 and cream>=400,(report,'No live original Medina printed page in native WebView: image unavailable or fallback shown')
print('PASS actual colorful Medina Mushaf printed artwork inside native Android WebView:',report)
