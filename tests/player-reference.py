"""Only the Arabic player appearance affected by the latest visual feedback."""
from pathlib import Path
from functools import partial
from threading import Thread
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
import json
root=Path(__file__).resolve().parents[1];out=root/'reports/action-glass-1.0.107';(out/'screenshots').mkdir(parents=True,exist_ok=True);checks=[]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')));Thread(target=s.serve_forever,daemon=True).start()
try:
 with sync_playwright()as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(service_workers='block');errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual'}))")
  page.goto(f'http://127.0.0.1:{s.server_port}/',wait_until='domcontentloaded');page.click('header [data-tab=mushaf]');page.wait_for_function('document.getElementById("qTrack").textContent.includes("الجزء")')
  assert page.locator('.recitation-caption>strong').inner_text()=='المصحف الشريف'
  for width in [360,390,412,1366,1600]:
   page.set_viewport_size({'width':width,'height':1000});page.wait_for_timeout(120)
   player=page.locator('.reference-player');box=player.bounding_box();parent=page.locator('#mushaf').bounding_box()
   assert box['width']>=parent['width']*.9,(width,box,parent)
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   styles=player.evaluate('(e)=>{const s=getComputedStyle(e),play=getComputedStyle(e.querySelector("#qTransport"),"::before"),seek=getComputedStyle(e.querySelector("#qSeek"));return{edge:s.borderTopColor,disc:play.borderTopColor,track:seek.getPropertyValue("--line").trim(),edgeToken:s.getPropertyValue("--media-edge").trim(),trackToken:s.getPropertyValue("--media-track").trim()}}')
   assert styles=={'edge':'rgba(255, 255, 255, 0.14)','disc':'rgba(255, 255, 255, 0.25)','track':'rgba(255,255,255,.3)','edgeToken':'rgba(255,255,255,.14)','trackToken':'rgba(255,255,255,.3)'},styles
   assert page.locator('#qStop').is_visible()and page.locator('#qTransport').bounding_box()['width']==44
   if width>=1366:assert box['width']/box['height']>=8,(width,box)
   if width in[390,1600]:player.screenshot(path=str(out/'screenshots'/f'player-ar-{width}-v2.png'))
   checks.append({'viewport':width,'player':box,'styles':styles})
  assert not errors,errors;b.close()
 (out/'player-reference-checks.json').write_text(json.dumps({'result':'PASS','language':'ar','cases':checks,'page_errors':errors},indent=2)+'\n')
 print('PASS: Arabic title/metadata, exact final charcoal frame/disc/track palette, full responsive player width, wide desktop proportions, preserved controls and no overflow at5 widths.')
finally:s.shutdown()
