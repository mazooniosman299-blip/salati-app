"""Targeted 1.0.103 date hierarchy, preserved reference icons and compact player checks."""
from pathlib import Path
from functools import partial
from threading import Thread
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
import json,xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1];out=root/'reports/1.0.103-refinement';(out/'screenshots').mkdir(parents=True,exist_ok=True)
ns={'s':'http://www.w3.org/2000/svg'};sprite=ET.parse(root/'dist/icons/navigation.svg')
for id,name in [('mushaf','book-open'),('dhikr','heart'),('qibla','compass')]:
 source=ET.parse(root/'node_modules/@phosphor-icons/core/assets/regular'/f'{name}.svg')
 assert [n.attrib for n in sprite.findall(f'.//s:symbol[@id="{id}"]//s:path',ns)]==[n.attrib for n in source.findall('.//s:path',ns)],id
layout=ET.parse(root/'android/app/src/main/res/layout/prayer_widget.xml');attr='{http://schemas.android.com/apk/res/android}'
labels={e.get(attr+'id'):e for e in layout.iter()if e.get(attr+'id')}
city=labels['@+id/widget_location'];assert city.get(attr+'textSize')=='17sp'
for id in ['widget_date','widget_hijri']:
 e=labels['@+id/'+id];assert float(e.get(attr+'textSize').removesuffix('sp'))<17
 assert e.get(attr+'textColor')=='#FFFFFF'and e.get(attr+'ellipsize')is None
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')));Thread(target=server.serve_forever,daemon=True).start();checks=[]
try:
 with sync_playwright()as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(service_workers='block');errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual'}))")
  page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded');page.wait_for_selector('.nav-selection')
  for width in [360,390,412,768,1024,1366,1920]:
   page.set_viewport_size({'width':width,'height':1000});page.click('header [data-tab=times]')
   for lang in ['ar','en']:
    if page.locator('html').get_attribute('lang')!=lang:page.click('#lang')
    data=page.locator('#cityLabel,#gregorianDate,#dateLabel').evaluate_all('(es)=>es.map(e=>{const c=getComputedStyle(e),r=e.getBoundingClientRect();return {id:e.id,size:parseFloat(c.fontSize),color:c.color,weight:c.fontWeight,overflow:c.overflowWrap,x:r.x,y:r.y,bottom:r.bottom,scroll:e.scrollWidth,client:e.clientWidth}})')
    assert data[0]['size']==(19 if width<=360 else 21 if width<=760 else 28),(width,data)
    for e in data[1:]:assert e['size']<data[0]['size']and e['color']=='rgb(255, 255, 255)'and e['scroll']<=e['client']+1,(width,lang,data)
    assert data[2]['y']>=data[1]['bottom']-1
    assert page.locator('#times .recitation-player').count()==0
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    for id in ['mushaf','dhikr','qibla']:
     icon=page.locator(f'header [data-tab={id}] .nav-symbol');style=icon.evaluate('(e)=>{const s=getComputedStyle(e);return [s.width,s.height,s.color]}');assert style==['24px','24px','rgb(255, 255, 255)']
    checks.append({'width':width,'lang':lang,'dates':data})
    if width in[390,1366]and lang=='ar':page.locator('.prayer-overview').screenshot(path=str(out/'screenshots'/f'widget-{width}.png'))
   if page.locator('html').get_attribute('lang')!='ar':page.click('#lang')
   page.click('header [data-tab=mushaf]');page.wait_for_selector('#mushaf #qTransport')
   assert page.locator('.recitation-player').count()==1
   play=page.locator('#qTransport');box=play.bounding_box();assert box['width']==box['height']==44
   disc=play.evaluate('(e)=>{const s=getComputedStyle(e,"::before");return {left:s.left,right:s.right,border:s.borderTopWidth,radius:s.borderRadius}}');assert disc=={'left':'4px','right':'4px','border':'1px','radius':'50%'}
   stop=page.locator('#qStop').bounding_box();caption=page.locator('.recitation-caption').bounding_box();assert stop['y']<caption['y']+caption['height']and stop['x']+stop['width']<=caption['x']+1
   assert page.locator('#qStop').is_visible()
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   if width in[390,1366]:page.locator('.recitation-player').screenshot(path=str(out/'screenshots'/f'player-{width}.png'))
  assert not errors,errors;b.close()
 (out/'focused-checks.json').write_text(json.dumps({'result':'PASS','cases':checks,'icons':'Original regular Phosphor book-open/heart/compass; white24px, unchanged paths','play_touch_target':44,'visual_play_disc':36,'stop_preserved':True,'physical_device_tested':False,'page_errors':errors},ensure_ascii=False,indent=2)+'\n')
 print('PASS: 14 date width/language cases, unchanged large city and white outline icons, compact single Mushaf player with preserved stop and44px play target/36px disc; no overflow/page errors. Native XML hierarchy checked; no physical device claim.')
finally:server.shutdown()
