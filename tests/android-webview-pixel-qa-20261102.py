#!/usr/bin/env python3
"""Real Android System WebView screenshot validation (no mocked UI).
The native Quran has controls above parchment; opening the tab and scrolling
to the actual reading panel are two separate interactions and screenshots.
"""
from pathlib import Path
from PIL import Image
import json
folder=Path("reports/android-webview-20261102")
files=[folder/(name+".png") for name in ("times","mushaf","mushaf-reader")]
assert all(p.is_file() for p in files), ("Missing native adb screenshot",files)
a,b,reader=[Image.open(p).convert("RGB") for p in files]
assert a.size==b.size==reader.size, "Screen changed dimensions"
w,h=a.size
assert w>=320 and h>=650,(w,h)

def nav_blue(im):
    columns=[]
    for x in range(int(w*.08),int(w*.95)):
        found=0
        for y in range(max(0,h-140),h-32):
            r,g,blue=im.getpixel((x,y))
            if 5<=r<=55 and 45<=g<=140 and 120<=blue<=250 and blue>g*1.5:
                found+=1
        if found>=10:columns.append(x)
    assert len(columns)>=15,("No native blue active tab",len(columns),w,h)
    return {"left":min(columns),"right":max(columns),
            "center":round(sum(columns)/len(columns),1),"pixel_count":len(columns)}

at,am=nav_blue(a),nav_blue(b)
assert at["center"]>am["center"]+20,("Quran tab did not activate",at,am)

def cream(px):
    r,g,bl=px
    return r>210 and g>205 and bl>180 and max(r,g,bl)-min(r,g,bl)<35

def cream_count(im):
    return sum(cream(im.getpixel((x,y)))
               for y in range(int(h*.15),int(h*.83),4)
               for x in range(int(w*.1),int(w*.9),4))
home,initial,scrolled=map(cream_count,(a,b,reader))
assert scrolled>home+450,("Quran parchment missing AFTER scroll",home,initial,scrolled)

# Locate the cream panel from real pixels, not a fixed viewport fraction.
cream_rows=[]
for y in range(int(h*.12),int(h*.82)):
    n=sum(cream(reader.getpixel((x,y)))
          for x in range(int(w*.11),int(w*.89),3))
    if n >= int((w*.78/3)*.48):
        cream_rows.append(y)
assert len(cream_rows)>50,("No substantial reader parchment visible",len(cream_rows))
start=cream_rows[0]
# The selected original edition has no reconstructed top ornamental frame.
# Require visible Quran ink inside real parchment, including opening pages.
ink=0
for y in range(start,min(int(h*.84),cream_rows[-1]+1)):
    for x in range(int(w*.09),int(w*.91)):
        r,g,bl=reader.getpixel((x,y))
        if 15<r<125 and 15<g<125 and 15<bl<125 and max(r,g,bl)-min(r,g,bl)<45:ink+=1
assert ink>=300,("Native Quran original page ink missing",ink,start,w,h)
result={"screen":[w,h],"blue_times":at,"blue_mushaf":am,
        "parchment_times":home,"parchment_initial":initial,
        "parchment_scrolled":scrolled,"original_page_ink_pixels":ink,
        "parchment_start_y":start}
(folder/"result.json").write_text(json.dumps(result,indent=2))
print("PASS NATIVE ANDROID SYSTEM WEBVIEW",json.dumps(result))
