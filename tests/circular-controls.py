"""Visible circular tap targets must remain square, including mobile flex layouts."""
from pathlib import Path
from functools import partial
from threading import Thread
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
import json
root=Path(__file__).resolve().parents[1];out=root/'reports/reference-ui-1.0.106';out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')));Thread(target=s.serve_forever,daemon=True).start();checks=[]
try:
 with sync_playwright()as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(service_workers='block');page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual'}))")
  page.goto(f'http://127.0.0.1:{s.server_port}/',wait_until='domcontentloaded')
  for width in [320,360,390,760,1440]:
   page.set_viewport_size({'width':width,'height':1000});page.click('[data-tab=settings]')
   controls=page.locator('.prayer-adjust-row .adjust-stepper button').evaluate_all('(es)=>es.map(e=>{let r=e.getBoundingClientRect(),c=getComputedStyle(e);return{width:r.width,height:r.height,radius:c.borderRadius,display:c.display,place:c.placeItems}})')
   assert len(controls)==12
   numbers=page.locator('.adjust-stepper input').evaluate_all('(es)=>es.map(e=>({value:e.value,color:getComputedStyle(e).color,fill:getComputedStyle(e).webkitTextFillColor}))');assert all(n['color']=='rgb(255, 255, 255)' and n['fill']=='rgb(255, 255, 255)' for n in numbers),numbers
   assert all(abs(c['width']-c['height'])<.1 and c['width']>=44 and c['radius']=='50%'for c in controls),(width,controls)
   assert all(c['display']=='grid' and c['place']=='center'for c in controls),(width,controls)
   before=page.locator('#adjust-fajr').input_value();page.locator('[data-adjust=fajr][data-step="1"]').click();assert int(page.locator('#adjust-fajr').input_value())==int(before)+1;page.locator('[data-adjust=fajr][data-step="-1"]').click();assert page.locator('#adjust-fajr').input_value()==before
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
   page.locator('.minute-adjustments').screenshot(path=str(out/f'circles-{width}.png'))
   page.click('#locationPickerOpen');page.wait_for_selector('#locationMenu[open]');close=page.locator('#locationMenu .choice-close').bounding_box();assert close['width']==close['height']==44,(width,close);page.locator('#locationMenu .choice-close').click();assert not page.locator('#locationMenu').is_visible()
   page.click('#voicePickerOpen');page.wait_for_selector('#voicePicker[open]');voice=page.locator('#voicePickerClose').bounding_box();assert voice['width']==voice['height']==44,(width,voice);page.locator('#voicePickerClose').click();assert not page.locator('#voicePicker').is_visible()
   checks.append({'width':width,'stepper_buttons':controls,'location_close':close,'voice_close':voice})
  b.close()
 (out/'circles.json').write_text(json.dumps({'result':'PASS','checks':checks},indent=2)+'\n');print('PASS: 12 +/- circles plus location/voice close controls remain 44x44, centered and functional at five widths; no overflow.')
finally:s.shutdown()
