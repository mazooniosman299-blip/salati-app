"""Actual Android RemoteViews bounds and screenshots, never browser/widget mockups."""
from pathlib import Path
import json,re,subprocess,time,xml.etree.ElementTree as ET

root=Path(__file__).resolve().parents[1]
out=root/'reports/native-widget-preview';out.mkdir(parents=True,exist_ok=True)
package='com.salati.prayer.preview'
def adb(*args):return subprocess.check_output(['adb',*map(str,args)],timeout=35)
def rectangle(node):return list(map(int,re.findall(r'\d+',node.attrib['bounds'])))
results=[]
try:
 for width in [900,1080,1440]:
  adb('shell','wm','size',f'{width}x2340');adb('shell','wm','density','440')
  adb('shell','am','force-stop',package)
  adb('shell','am','start','-W','-n',package+'/com.salati.prayer.WidgetPreviewActivity','--ei','active','2')
  found={}
  for attempt in range(8):
   time.sleep(1)
   try:
    adb('shell','uiautomator','dump','--compressed','/sdcard/salati-widget.xml')
    raw=adb('shell','cat','/sdcard/salati-widget.xml')
    hierarchy=ET.fromstring(raw[raw.index(b'<?xml'):])
    found={n.attrib.get('resource-id','').split('/')[-1]:n for n in hierarchy.iter('node')}
    if all(k in found for k in ['widget_next_label','widget_next','widget_countdown']):break
   except (subprocess.CalledProcessError,ET.ParseError,ValueError):pass
  assert all(k in found for k in ['widget_next_label','widget_next','widget_countdown']),('Actual native widget not rendered',width)
  names=['widget_next_label','widget_next','widget_countdown']
  bounds={k:rectangle(found[k]) for k in names}
  assert all(b[2]>b[0] and b[3]>b[1] for b in bounds.values()),bounds
  edges=[b[2] for b in bounds.values()]
  assert max(edges)-min(edges)<=2,('Caption, prayer and countdown right edges differ',width,bounds)
  assert width-max(edges)>=20*440/160-2,('Countdown too close to frame',width,bounds)
  assert found['widget_next'].attrib['text']=='الظهر',found['widget_next'].attrib
  assert ':' in found['widget_countdown'].attrib['text']
  assert all(k in found for k in ['widget_date','widget_hijri','widget_fajr','widget_sunrise','widget_dhuhr','widget_asr','widget_maghrib','widget_isha'])
  (out/f'aligned-{width}.xml').write_bytes(raw)
  (out/f'aligned-{width}.png').write_bytes(adb('exec-out','screencap','-p'))
  results.append({'physical_width':width,'density':440,'bounds':bounds,'right_edge':edges[0],'result':'PASS'})
finally:
 adb('shell','wm','size','1080x2340');adb('shell','wm','density','440')
(out/'alignment-results.json').write_text(json.dumps({'device':'actual Android emulator RemoteViews','physical_phone':'NOT RUN','cases':results},ensure_ascii=False,indent=2)+'\n')
print('PASS actual native widget3right-edges, safe frame gap and preserved date/six prayer views at3widths')
