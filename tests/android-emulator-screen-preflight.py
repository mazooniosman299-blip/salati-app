#!/usr/bin/env python3
"""Preflight native Android screenshot without OCR.

Mode dialog: success if the system ANR modal is covering the app.
Mode quran-tap: print x y of Quran tab. Mode reader-swipe: screenshot-derived safe parchment swipe coordinates (no reciter picker taps).
"""
from PIL import Image
import sys,io,base64

assert len(sys.argv)>=3, 'usage: preflight.py mode /path/to/screenshot.png'
mode,path=sys.argv[1:3]

def navigation(im):
 w,h=im.size
 pixels=[]
 for y in range(h-145,h-25):
  for x in range(int(w*.07),int(w*.96)):
   r,g,b=im.getpixel((x,y))
   if 5<=r<=60 and 40<=g<=150 and 110<=b<=255 and b>g*1.5:
    pixels.append((x,y))
 assert len(pixels)>300,('No undimmed blue tab',len(pixels),w,h)
 xs=[x for x,_ in pixels];ys=[y for _,y in pixels]
 active_x=(min(xs)+max(xs))//2;active_y=(min(ys)+max(ys))//2
 # Actual 432x960 native captures place the settled bar at y905. During
 # first paint Android can transiently apply insets twice (observed y866).
 # A coloured pill alone does not prove that labels/input layout are ready.
 assert h-82<=active_y<=h-30,('Navigation insets not settled',active_y,h)
 pitch=(w-16)//6
 assert active_x>w*.8,('Expected initial Times tab',active_x,w)
 for slot in range(6):
  left=8+slot*pitch;right=min(w,left+pitch)
  ink=sum(min(im.getpixel((x,y)))>185
   for y in range(active_y-22,active_y+23)
   for x in range(left,right))
  assert ink>20,('Incomplete navigation icons/labels',slot,ink)
 return active_x-pitch,active_y

if mode=='quran-tap-stable':
 assert len(sys.argv)==5,'Three consecutive actual frames required'
 frames=[Image.open(p).convert('RGB') for p in sys.argv[2:]]
 assert len({f.size for f in frames})==1,'Viewport is still moving'
 points=[navigation(f) for f in frames]
 assert all(abs(x-points[-1][0])<=2 and abs(y-points[-1][1])<=2 for x,y in points),'Navigation is still moving'
 print(*points[-1]);raise SystemExit(0)

assert len(sys.argv)==3,'Single screenshot required for this mode'
im=Image.open(path).convert('RGB')
w,h=im.size
assert w>=320 and h>=650, (w,h)
if mode=='evidence':
 # A bounded real screenshot preview in CI logs permits diagnosis even when
 # the artifact download service is unavailable. This never grants a pass.
 im.thumbnail((216,480));buffer=io.BytesIO();im.save(buffer,format='PNG')
 print('SALATI_SCREENSHOT_PNG_BASE64='+base64.b64encode(buffer.getvalue()).decode())
 raise SystemExit(0)
if mode=='dialog':
 # The emulator sometimes displays a Pixel Launcher ANR over our app. The
 # translucent white rounded dialog spans the center AND lower-middle, while
 # both Salati's home and Mushaf screens are dark at ~72% screen height.
 # Actual Pixel Launcher ANR dialog occupies roughly Y=43–60% of
 # a 960px screen, NOT Y=72%; sampling at 72% produced false negatives.
 # Check several bright interior points to avoid button text or icon pixels.
 samples=[im.getpixel((int(w*x),int(h*y)))
          for y in (.46,.49,.52,.55)
          for x in (.18,.35,.65,.82)]
 modal=sum(min(rgb)>185 and max(rgb)-min(rgb)<45 for rgb in samples)>=11
 if modal: print('SYSTEM ANR overlay detected, close Pixel Launcher dialog',file=sys.stderr)
 raise SystemExit(0 if modal else 1)
if mode in ('reader-swipe','quran-ready'):
 # Only initiate scroll inside *visible parchment*, not at a hard-coded Y
 # that may instead be the reciter selector, audio buttons or navigation.
 def cream(p):
  r,g,b=p
  return r>210 and g>205 and b>180 and max(r,g,b)-min(r,g,b)<35
 rows=[]
 xmin,xmax=int(w*.14),int(w*.86)
 for y in range(int(h*.14),int(h*.9),3):
  n=sum(cream(im.getpixel((x,y))) for x in range(xmin,xmax,4))
  if n>int(((xmax-xmin)/4)*.34):
   rows.append(y)
 if mode=='quran-ready':
  if len(rows)>=20:
   print('Quran actual rendered parchment ready',file=sys.stderr)
   raise SystemExit(0)
  raise SystemExit(1)
 assert len(rows)>=20,('No visible Quran parchment available as safe swipe origin',len(rows),w,h)
 start=rows[int((len(rows)-1)*.67)]
 end=max(int(h*.18),start-min(300,int(h*.35)))
 assert start-end>=100 and start<h-75,('Unsafe Quran swipe location',start,end,w,h)
 print(w//2,start,end)
 raise SystemExit(0)
if mode in ('ready','quran-tap'):
 try:
  point=navigation(im)
 except AssertionError:
  if mode=='ready':raise SystemExit(1)
  raise
 if mode=='ready':
  print('Native Salati complete navigation ready',file=sys.stderr)
  raise SystemExit(0)
 print(*point)
else:
 raise ValueError('unknown mode '+mode)
