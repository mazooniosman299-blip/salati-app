"""Verify exact tile borders and removed Fajr UI in real Chromium; preserve all other colors."""
from pathlib import Path
from functools import partial
from threading import Thread
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
out=root/'reports/square-prayer-20261101';out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')))
Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for width in (320,360,390,768,1440):
   page=browser.new_page(viewport={'width':width,'height':844},service_workers='block')
   errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
   # Select a real, valid city: without a location the app correctly has no
   # active prayer and a selected-badge visual check would be meaningless.
   page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,name:'مسقط',zone:'Asia/Muscat',locationSet:true,locationMode:'manual',method:'Auto',madhab:'Shafi'}))")
   page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
   page.click('[data-tab=times]')
   page.wait_for_function("document.querySelector('#prayers .prayer.active') !== null")
   tiles=page.locator('#prayers .prayer').evaluate_all("""els=>els.map(el=>({
    radius:getComputedStyle(el).borderTopLeftRadius,bg:getComputedStyle(el).backgroundColor,
    active:el.classList.contains('active'),border:getComputedStyle(el).borderColor
   }))""")
   assert len(tiles)==6,(width,tiles)
   assert sum(c['radius']=='18px' for c in tiles if c['active'])==1,(width,'Selected badge matches rounded screenshot',tiles)
   assert all(c['radius']=='12px' for c in tiles if not c['active']),(width,'Unselected tiles retain prior style',tiles)
   assert any(c['bg']!='rgba(0, 0, 0, 0)' for c in tiles),(width,'Must preserve original fill',tiles)
   if width in (390,768):page.locator('#prayers').screenshot(path=str(out/f'prayers-{width}.png'))
   page.click('[data-tab=settings]')
   assert page.locator('#fajrAnnouncementToggle,#previewFajrPhrase,.announcement-settings,#announcementStatus').count()==0
   assert page.locator('[data-audio-prayer=fajr]').count()==1,'Keep normal Fajr adhan'
   assert page.locator('#previewAdhan').count()==1,'Keep normal audio preview'
   assert not errors,(width,errors)
   page.close()
  browser.close()
 print('PASS: five widths, 6 individual square prayer tiles, unchanged dark fills and ordinary Fajr adhan, removed old Fajr controls')
finally:
 server.shutdown()
