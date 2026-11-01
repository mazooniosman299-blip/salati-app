#!/usr/bin/env python3
"""Android SYSTEM WebView pixel smoke test: no mockups or browser emulation.
Screenshots come from adb screencap after opening the actual preview APK.
Test two real input taps and ensure blue active selection moves across tabs.
"""
from pathlib import Path
from PIL import Image
import json,sys

folder=Path('reports/android-webview-20261102')
first=folder/'times.png'
second=folder/'mushaf.png'
assert first.is_file() and second.is_file(), 'Missing actual adb screenshots'
a,b=Image.open(first).convert('RGB'),Image.open(second).convert('RGB')
assert a.size==b.size, 'Screen geometry changed during navigation'
w,h=a.size
assert w>=320 and h>=650,(w,h)

def nav_blue(im):
 # Keep away from Quran player/audio action above the fixed tab bar.
 # Ignore bottom OS gesture/navigation chrome.
 columns=[]
 for x in range(int(w*.08),int(w*.95)):
  found=0
  for y in range(max(0,h-140),h-32):
   r,g,blue=im.getpixel((x,y))
   if 5<=r<=55 and 45<=g<=140 and 120<=blue<=250 and blue>g*1.5:
    found+=1
  if found>=10:columns.append(x)
 assert len(columns)>=15,('No blue active tab found on screenshot',len(columns),w,h)
 return {'left':min(columns),'right':max(columns),'center':round(sum(columns)/len(columns),1),'pixel_count':len(columns)}
a_stats,b_stats=nav_blue(a),nav_blue(b)
# Times is the rightmost nav cell; Mushaf is its immediate left neighbor.
assert a_stats['center']>b_stats['center']+20,('Tapping Quran did not move the active blue background',a_stats,b_stats)
# Quran shows cream parchment in upper/middle body, unlike home/time screen.
def cream_count(im):
 total=0
 for y in range(int(h*.18),int(h*.76),6):
  for x in range(int(w*.12),int(w*.88),6):
   r,g,b=im.getpixel((x,y))
   if r>210 and g>205 and b>180 and max(r,g,b)-min(r,g,b)<35:total+=1
 return total
c1,c2=cream_count(a),cream_count(b)
assert c2>c1+100,('Mushaf parchment not visible after opening Quran',c1,c2)
# Native WebView used to show a BLANK cream surah title and unadorned
# verse dots, even though Chromium screenshots showed the original gold
# medallions. Verify real textured ornament pixels in the surah heading band.
def ornament_pixels(im):
 total=0
 for y in range(int(h*.145),int(h*.198)):
  for x in list(range(int(w*.08),int(w*.33)))+list(range(int(w*.70),int(w*.92))):
   r,g,b=im.getpixel((x,y))
   if (r<206 and g<191 and b<172 and r>65 and g>55 and b>40):
    total+=1
 return total
pattern=ornament_pixels(b)
assert pattern>=80,('Android Quran surah ornament not rendered; plain heading regression',pattern,w,h)
result={'screen':[w,h],'blue_times':a_stats,'blue_mushaf':b_stats,'parchment_times':c1,'parchment_mushaf':c2,'surah_ornament_pixels':pattern}
(folder/'result.json').write_text(json.dumps(result,indent=2))
print('PASS NATIVE ANDROID SYSTEM WEBVIEW '+json.dumps(result))
