#!/usr/bin/env python3
"""Capture real Salati-approved Quran player at phone widths. NO DEPLOY."""
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
out=root/'reports/approved-quran-player'
out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')))
Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
  for w,h in [(320,740),(390,844),(412,915),(768,960)]:
   page=browser.new_page(viewport={'width':w,'height':h},service_workers='block')
   errors=[]
   page.on('pageerror',lambda e:errors.append(str(e)))
   page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual'}))")
   response=page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
   assert response and response.ok
   page.locator('header>.site-nav button[data-tab=mushaf]').click()
   page.wait_for_function("() => document.body.classList.contains('salati-quran-approved-screen')",timeout=30000)
   page.wait_for_function("() => !!document.querySelector('#qVerses [data-ayah]')",timeout=30000)
   geom=page.evaluate("""() => {
    const get=id=>document.getElementById(id);
    const rect=e=>{const r=e.getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,w:r.width,h:r.height}};
    const slot=get('mushafPlayerSlot'),inner=slot.querySelector('.recitation-player');
    return {slot:rect(slot),play:rect(get('qTransport')),bg:getComputedStyle(inner).backgroundColor,
      white:getComputedStyle(get('qTrack')).color,
      mainWhite:getComputedStyle(inner.querySelector('.recitation-caption strong')).color,
      movedReciter:slot.contains(get('qReciter')),
      rawReciterOutside:!!document.querySelector('.mushaf-selectors #qReciter'),
      oldTimer:!!get('qTimer'),before:getComputedStyle(slot,'::before').content,
      playColor:getComputedStyle(get('qTransport')).backgroundColor,
      scrollSpace:getComputedStyle(get('qVerses')).paddingBottom};
   }""")
   assert geom['slot']['left']>=0 and geom['slot']['right']<=w+1,(w,geom)
   assert geom['slot']['bottom']<=h+1 and geom['play']['w']>=40,(w,geom)
   assert geom['bg']=='rgb(24, 25, 29)' and geom['playColor']=='rgb(37, 99, 235)',(w,geom)
   assert geom['white']=='rgb(255, 255, 255)' and geom['mainWhite']==geom['white'],(w,geom)
   assert geom['movedReciter'] and not geom['rawReciterOutside'] and not geom['oldTimer'],(w,geom)
   assert not errors,(w,errors)
   page.screenshot(path=str(out/f'REAL-salati-approved-player-{w}.png'),full_page=False)
   assert page.locator('#qReciter').count()==1
   page.locator('#qApprovedSettings').click()
   assert page.locator('#qReciter').is_visible() and page.locator('#qSeek').is_visible()
   page.locator('#qApprovedSettings').click()
   old=page.locator('#qRepeat').is_checked()
   page.locator('#qApprovedRepeat').click()
   assert page.locator('#qRepeat').is_checked()!=old
   page.locator('#qApprovedSpeed').click()
   assert page.evaluate("document.getElementById('qAudio').playbackRate")>1
   page.locator('#qApprovedClose').click()
   assert not page.locator('#mushafPlayerSlot').is_visible()
   page.locator('#qApprovedOpen').click()
   assert page.locator('#mushafPlayerSlot').is_visible()
   page.locator('#qApprovedReaderBack').click()
   assert not page.evaluate("document.body.classList.contains('salati-quran-approved-screen')")
   page.close()
  browser.close()
 print('PASS real Salati player: white titles, charcoal/blue controls, reciter moved, no notch/clock, all controls interactive, 320/390/412/768px')
finally:
 server.shutdown()
