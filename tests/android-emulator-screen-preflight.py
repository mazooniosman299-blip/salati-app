#!/usr/bin/env python3
"""Preflight native Android screenshot without OCR.

Mode dialog: success if the system ANR modal is covering the app.
Mode quran-tap: print x y of the next tab left of the rightmost blue tab.
"""
from PIL import Image
import sys

assert len(sys.argv)==3, 'usage: preflight.py dialog|quran-tap /path/to/screenshot.png'
mode,path=sys.argv[1:]
im=Image.open(path).convert('RGB')
w,h=im.size
assert w>=320 and h>=650, (w,h)
if mode=='dialog':
 # The emulator sometimes displays a Pixel Launcher ANR over our app. The
 # translucent white rounded dialog spans the center AND lower-middle, while
 # both Salati's home and Mushaf screens are dark at ~72% screen height.
 samples=[im.getpixel((w//2,int(h*y))) for y in (.40,.72)]
 modal=all(min(rgb)>185 and max(rgb)-min(rgb)<40 for rgb in samples)
 if modal: print('SYSTEM ANR overlay detected, close Pixel Launcher dialog',file=sys.stderr)
 raise SystemExit(0 if modal else 1)
if mode=='quran-tap':
 pixels=[]
 for y in range(h-145,h-25):
  for x in range(int(w*.07),int(w*.96)):
   r,g,b=im.getpixel((x,y))
   if 5<=r<=60 and 40<=g<=150 and 110<=b<=255 and b>g*1.5:
    pixels.append((x,y))
 assert len(pixels)>300, ('No undimmed blue tab in real Android screenshot',len(pixels),w,h)
 xs=[x for x,_ in pixels];ys=[y for _,y in pixels]
 active_x=(min(xs)+max(xs))//2
 active_y=(min(ys)+max(ys))//2
 tab_pitch=(w-16)//6
 mushaf_x=active_x-tab_pitch
 assert mushaf_x>0 and mushaf_x<w, ('Quran target outside screen',active_x,tab_pitch)
 print(mushaf_x,active_y)
else:
 raise ValueError('unknown mode '+mode)
