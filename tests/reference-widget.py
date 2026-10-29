"""The selected widget's live location, countdown and six times share one responsive surface."""
from pathlib import Path
from functools import partial
from threading import Thread
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')));Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(service_workers='block')
  page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual'}));")
  page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded');page.wait_for_selector('.nav-selection')
  page.wait_for_function('document.querySelector(".hero-picture img").naturalWidth===1120')
  card=page.locator('.prayer-overview');assert card.count()==1,'Selected reference needs one shared prayer/location/countdown surface'
  for width in [320,390,600,760,1024,1440]:
   page.set_viewport_size({'width':width,'height':1000})
   for dark in [False,True]:
    page.evaluate('(dark)=>document.body.classList.toggle("dark",dark)',dark)
    page.click('[data-tab=times]');page.wait_for_timeout(300)
    for target in ['#cityLabel','#gregorianDate','#dateLabel','#nextName','#countdown','#prayers']:assert card.locator(target).count()==1,target
    cells=page.locator('#prayers .prayer').all();assert len(cells)==6
    tops=[round(c.bounding_box()['y'])for c in cells];assert max(tops)-min(tops)<=1,(width,'six times must remain on one aligned strip',tops)
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
    page.click('[data-tab=mushaf]');page.wait_for_selector('#qSeek')
    assert not page.locator('#qPlay').is_visible(),'Reference has one primary play control'
    assert page.locator('.recitation-player #qTrack').count()==1
    assert page.locator('#qTransport').bounding_box()['width']==44
    page.keyboard.press('Tab')
    active=page.locator('header>.site-nav .active').bounding_box();marker=page.locator('.nav-selection').bounding_box()
    assert abs(marker['width']-(active['width']-8))<1.5 and abs(marker['height']-(active['height']-8))<1.5,'Active rectangle must follow its equal-sized navigation target'
  b.close()
 print('PASS: 12 widget/width/theme states share live data, aligned prayer strip, single player and reference rectangular navigation.')
finally:server.shutdown()
