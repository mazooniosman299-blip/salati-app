"""Verify actual Android RemoteViews, not CSS/browser approximations."""
from pathlib import Path
from PIL import Image, ImageChops
from xml.etree import ElementTree as ET
import re

folder=Path('reports/native-widget')
first=Image.open(folder/'maghrib.png').convert('RGB')
second=Image.open(folder/'asr.png').convert('RGB')
assert first.size==second.size and first.width>=1000,(first.size,second.size)
root=ET.parse(folder/'maghrib.xml').getroot()
nodes=[n.attrib for n in root.iter('node')]
def bounds(raw):
 x1,y1,x2,y2=map(int,re.findall(r'\d+',raw));return (x1,y1,x2,y2)
def hit(value,lower=0):
 return [bounds(n['bounds']) for n in nodes if n.get('text')==value and bounds(n['bounds'])[1]>=lower]
labels=['الفجر','الشروق','الظهر','العصر','المغرب','العشاء']
times=['4:55','6:13','11:55','3:08','5:33','6:44']
for name in labels:
 assert hit(name),f'Native TextView for {name} must be present'
for value in times:
 assert hit(value),f'Native clock {value} must be present'
widgetTimes=[hit(v)[-1] for v in times]
centers=[(a[1]+a[3])/2 for a in widgetTimes]
assert max(centers)-min(centers)<=12,('Six clocks must remain one exact row',widgetTimes)
for value,name in zip(times,labels):
 label=hit(name)[-1];clock=hit(value)[-1]
 assert label[3]<=clock[1]+3,(name,'Prayer name must stay ABOVE the capsule time',label,clock)
selected=hit('5:33')[-1]
assert selected[2]-selected[0]>=44,'Time-only pill must fit numerals'
# The currently selected time has a gray fill; after changing the selected
# prayer to Asr the same cell must lose it.
def mean(img,box):
 crop=img.crop(box)
 samples=list(crop.getdata())
 return tuple(sum(p[i] for p in samples)/len(samples) for i in range(3))
# Sample padding left of glyphs inside the time TextView so gray vs dark
# background is measurable, not white text contrast.
x1,y1,x2,y2=selected
area=(x1+4,y1+4,x1+max(7,int((x2-x1)*.17)),y2-4)
gray=mean(first,area);dark=mean(second,area)
assert sum(gray)/3 > sum(dark)/3+12,('The gray capsule must follow the current prayer',gray,dark,area)
assert ImageChops.difference(first,second).getbbox(),'Active prayer switch must visibly change Android widget'
print('PASS: Android RemoteViews screenshot: six RTL times in one row; labels remain outside; gray capsule follows active prayer.')
