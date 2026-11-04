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
   assert sum(c['active'] for c in tiles)==1,(width,'one active prayer after valid city and time calculation',tiles)
   #4Nov home reference supersedes old square strip; widget assertions remain separate.
   assert all(c['radius']=='12px' for c in tiles),(width,'new home reference corners',tiles)
   assert all(c['bg']==('rgb(41, 47, 57)' if c['active'] else 'rgb(21, 26, 34)') for c in tiles),(width,'reference charcoal cards',tiles)
   assert page.locator('#prayers .prayer-icon').evaluate_all("es=>es.every(e=>getComputedStyle(e).display!=='none'&&e.getBoundingClientRect().width===22)"),(width,'six reference icons')
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(width,'prayer strip overflows viewport')
   if width in (390,768):page.locator('#prayers').screenshot(path=str(out/f'prayers-{width}.png'))
   page.click('[data-tab=settings]')
   assert page.locator('#fajrAnnouncementToggle,#previewFajrPhrase,.announcement-settings,#announcementStatus').count()==0
   assert page.locator('[data-audio-prayer=fajr]').count()==1,'Keep normal Fajr adhan'
   assert page.locator('#previewAdhan').count()==1,'Keep normal audio preview'
   assert not errors,(width,errors)
   page.close()
  browser.close()
 print('PASS: five widths, 6 rounded reference home cards, charcoal backgrounds and ordinary Fajr adhan, removed old Fajr controls')
finally:
 server.shutdown()
