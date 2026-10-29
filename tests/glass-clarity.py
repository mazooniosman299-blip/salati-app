"""Reference regression: translucent prayer selection, white icons, visible control outlines."""
from pathlib import Path
from functools import partial
from threading import Thread
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
import json,re
root=Path(__file__).resolve().parents[1];out=root/'reports/glass-clarity-1.0.104';out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')));Thread(target=s.serve_forever,daemon=True).start()
checks=[]
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(service_workers='block');errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual'}))")
  page.goto(f'http://127.0.0.1:{s.server_port}/',wait_until='domcontentloaded')
  for width in [360,390,760,1550]:
   page.set_viewport_size({'width':width,'height':1000})
   page.click('[data-tab=times]');page.wait_for_selector('.prayer.active')
   selected=page.locator('.prayer.active').evaluate('(e)=>{let c=getComputedStyle(e);return{fill:c.backgroundColor,image:c.backgroundImage,radius:c.borderRadius}}')
   assert selected['fill']=='rgba(0, 0, 0, 0)' and 'linear-gradient' in selected['image'],selected
   assert '255, 255, 255, 0.09' in selected['image'],selected
   page.locator('.prayer-overview').screenshot(path=str(out/f'widget-{width}.png'))
   page.click('[data-tab=mushaf]')
   colors=page.locator('.mushaf-emblem path').evaluate_all('(es)=>es.map(e=>getComputedStyle(e).fill)')
   assert colors and set(colors)=={'rgb(255, 255, 255)'},colors
   assert page.locator('.mushaf-emblem').get_attribute('viewBox')=='0 0 256 256'
   assert page.locator('#qTransport').bounding_box()['width']==44
   for control in ['qRepeat','qAutoNext']:
    page.locator('#'+control).evaluate('(e)=>e.checked=false')
    assert page.locator('#'+control).evaluate('(e)=>getComputedStyle(e,"::before").backgroundColor')=='rgb(255, 255, 255)'
   page.click('[data-tab=qibla]')
   colors=page.locator('.kaaba-icon path').evaluate_all('(es)=>es.map(e=>({fill:getComputedStyle(e).fill,stroke:getComputedStyle(e).stroke}))')
   assert all(c['fill']in['rgb(255, 255, 255)','rgb(4, 5, 9)'] for c in colors),colors
   assert all(c['stroke']=='rgb(255, 255, 255)'for c in colors[:3]),colors
   page.locator('.qibla-card').screenshot(path=str(out/f'qibla-{width}.png'))
   page.click('[data-tab=settings]')
   toggle=page.locator('#fajrAnnouncementToggle')
   for checked in [False,True]:
    toggle.evaluate('(e,v)=>e.checked=v',checked)
    style=toggle.evaluate('(e)=>{let c=getComputedStyle(e),t=getComputedStyle(e,"::before");return{border:c.borderTopColor,borderWidth:c.borderTopWidth,track:c.backgroundColor,gradient:c.backgroundImage,w:e.offsetWidth,h:e.offsetHeight,thumb:t.backgroundColor,thumbWidth:t.width}}')
    assert style['borderWidth']=='1px' and style['w']==66 and style['h']==38,style
    assert style['thumb']=='rgb(255, 255, 255)'and style['thumbWidth']=='30px',style
    assert style['border']==('rgb(255, 255, 255)'if checked else'rgba(255, 255, 255, 0.46)'),style
   toggle.evaluate('(e)=>e.checked=false')
   border=page.locator('#previewFajrPhrase').evaluate('(e)=>{let c=getComputedStyle(e);return{border:c.borderTopColor,width:c.borderTopWidth,color:c.color,bg:c.backgroundImage}}')
   assert border['border']=='rgba(255, 255, 255, 0.46)'and border['width']=='1px',border
   assert border['color']=='rgb(255, 255, 255)'and 'linear-gradient' in border['bg'],border
   page.locator('#previewFajrPhrase').scroll_into_view_if_needed();page.screenshot(path=str(out/f'settings-{width}.png'))
   for tab in ['times','mushaf','qibla','dhikr','tasbih','settings']:
    page.click(f'[data-tab={tab}]');page.wait_for_timeout(80)
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,tab)
   checks.append({'width':width,'selection':selected,'fajr_button':border})
  assert not errors,errors;b.close()
 (out/'checks.json').write_text(json.dumps({'result':'PASS','widths':checks,'page_errors':errors,'physical_device_tested':False},indent=2)+'\n')
 print('PASS: transparent glass selection, monochrome white library book, white Kaaba outline and complete visible Fajr switch/button tracks at four widths; six-page overflow checks.')
finally:s.shutdown()
