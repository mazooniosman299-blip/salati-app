"""Larger white dates stay under the city on the physical left; native mirrors the hierarchy."""
from pathlib import Path
from functools import partial
from threading import Thread
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
import json,xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1];out=root/'reports/reference-ui-1.0.106';out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')));Thread(target=s.serve_forever,daemon=True).start();checks=[]
try:
 with sync_playwright()as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(service_workers='block');page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual'}))")
  page.goto(f'http://127.0.0.1:{s.server_port}/',wait_until='domcontentloaded')
  for width in [320,390,760,1440]:
   page.set_viewport_size({'width':width,'height':1000});page.click('[data-tab=times]')
   city=page.locator('#cityLabel').bounding_box();overview=page.locator('.prayer-overview').bounding_box();dates=page.locator('#gregorianDate,#dateLabel').evaluate_all('(es)=>es.map(e=>{let r=e.getBoundingClientRect(),s=getComputedStyle(e);return{x:r.x,y:r.y,right:r.right,width:r.width,color:s.color,size:parseFloat(s.fontSize),align:s.textAlign}})')
   assert all(d['align']=='left'and d['color']=='rgb(255, 255, 255)'and d['size']>=(14 if width<=760 else 18) and d['x']<overview['x']+overview['width']*.4 and d['y']>=city['y']+city['height']for d in dates),(width,dates,city)
   assert dates[1]['y']>dates[0]['y'];assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   hero=page.locator('.hero-info').bounding_box();right=hero['x']+hero['width']-float(page.locator('.hero-info').evaluate('(e)=>getComputedStyle(e).paddingRight').removesuffix('px'))
   for selector in ['.hero-prayer>span','#nextName','#countdown']:
    e=page.locator(selector);box=e.bounding_box();align=e.evaluate('(e)=>getComputedStyle(e).textAlign');assert abs(box['x']+box['width']-right)<2 or align=='right',(width,selector,box,right,align)
   cells=page.locator('#prayers .prayer').all();assert len(cells)==6;tops=[c.bounding_box()['y']for c in cells];assert max(tops)-min(tops)<1
   page.locator('.prayer-overview').screenshot(path=str(out/f'widget-dates-{width}.png'));checks.append({'width':width,'dates':dates})
  b.close()
 ns='{http://schemas.android.com/apk/res/android}';layout=ET.parse(root/'android/app/src/main/res/layout/prayer_widget.xml')
 for key in ['widget_date','widget_hijri']:
  e=next(e for e in layout.iter()if e.get(ns+'id')=='@+id/'+key);assert e.get(ns+'gravity')=='left'and e.get(ns+'textColor')=='#FFFFFF'and e.get(ns+'textSize')=='14sp'
 native=(root/'android/app/src/main/java/com/salati/prayer/PrayerWidget.java').read_text();assert 'for(float sp=14;sp>=12;sp-=.5f)'in native and 'return 8;'not in native
 (out/'date-checks.json').write_text(json.dumps({'result':'PASS','web':checks,'native_source_hierarchy':'PASS','native_physical_render_tested':False},indent=2)+'\n');print('PASS: larger white Gregorian/Hijri dates below city on left at four widths; unchanged six-time strip; Android left/white14sp and minimum12sp fitting rules verified.')
finally:s.shutdown()
