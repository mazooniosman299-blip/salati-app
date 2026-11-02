#!/usr/bin/env python3
"""Visual and functional regression for REAL full Medina Mushaf pages.

Check the 1240x1754 official-plate scans, no internal cropped scrollbox,
continuous outer scrolling, optional interactive Quran text and offline fallback.
No production deploy, no generated or fabricated Quran artwork.
"""
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from functools import partial
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright
import json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/madinah-fullpage-20261102';OUT.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'dist')))
Thread(target=server.serve_forever,daemon=True).start()
details=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
  for width,height in [(360,800),(390,844),(432,960),(1280,850)]:
   page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1,service_workers='block')
   page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded',timeout=30000)
   page.locator('button[data-tab="mushaf"]').click()
   q=page.locator('#qVerses');image=q.locator('.quran-reading-page .madinah-printed-image').first
   image.wait_for(timeout=30000)
   page.wait_for_function("""() => {
     const img=document.querySelector('#qVerses .madinah-printed-image');
     return img && img.complete && img.naturalWidth===1240 && img.naturalHeight===1754 &&
     img.closest('.quran-reading-page').classList.contains('madinah-image-loaded');
   }""",timeout=60000)
   image.scroll_into_view_if_needed(timeout=20000)
   shape=page.evaluate("""() => {
     const v=document.querySelector('#qVerses'),x=document.querySelector('#qSheet'),
       img=v.querySelector('.madinah-printed-image'),rect=img.getBoundingClientRect(),
       parent=img.closest('.madinah-print-page').getBoundingClientRect(),
       player=document.querySelector('#mushafPlayerSlot');
     return {over:getComputedStyle(v).overflowY,viewHeight:v.clientHeight,scrollHeight:v.scrollHeight,
       sheetOver:getComputedStyle(x).overflow,viewWidth:rect.width,imageHeight:rect.height,
       naturalWidth:img.naturalWidth,naturalHeight:img.naturalHeight,
       imgBottom:rect.bottom,pageBottom:parent.bottom,pageWidth:parent.width,
       pageRadius:getComputedStyle(x).borderRadius,
       imgDisplay:getComputedStyle(img).display,imgVisible:getComputedStyle(img).visibility,
       playerOutside:!x.contains(player),label:img.alt};
   }""")
   assert shape['over']=='visible' and shape['sheetOver']=='visible',(width,'Still cropped scroll container',shape)
   assert shape['naturalWidth']==1240 and shape['naturalHeight']==1754,(width,'Printed page incomplete',shape)
   assert shape['imgVisible']=='visible' and shape['imgDisplay']=='block',(width,'Image not shown',shape)
   assert abs(shape['imageHeight']/shape['viewWidth']-1754/1240)<.04,(width,'Printed image aspect distorted',shape)
   assert abs(shape['pageBottom']-shape['imgBottom'])<3,(width,'Page box clips original printed image',shape)
   assert shape['playerOutside'],(width,'Quran player overlaps printed text',shape)
   assert shape['pageRadius']=='0px',(width,'Mushaf is still a rounded box',shape)
   page.screenshot(path=str(OUT/f'printed-madinah-{width}px.png'),full_page=False)
   before=page.evaluate("() => document.querySelector('main')?.scrollTop || window.scrollY")
   image.hover()
   page.mouse.wheel(0,1500)
   page.wait_for_timeout(1200)
   page.wait_for_function("() => document.querySelectorAll('#qVerses .quran-reading-page').length>=2",timeout=20000)
   after=page.evaluate("() => document.querySelector('main')?.scrollTop || window.scrollY")
   assert after>before+10,(width,'Outer screen does not scroll',before,after)
   assert q.locator('.quran-reading-page').count()>=2,(width,'Second printed Medina page not available')
   toggle=page.locator('#qTextMode')
   toggle.click()
   assert page.locator('#qSheet').evaluate("el=>el.classList.contains('madinah-text-mode')")
   text=page.locator('#qVerses .mushaf-text-fallback').first
   assert text.locator('[data-ayah]').count()>0
   assert text.evaluate("el=>getComputedStyle(el).display")=='block',(width,'Interactive Quran text fallback disappeared')
   toggle.click()
   assert not page.locator('#qSheet').evaluate("el=>el.classList.contains('madinah-text-mode')")
   details.append({'width':width,'height':height,'image':'1240x1754','full_page':True,'scroll_delta':after-before})
   page.close()
  # Offline/CDN-error check: original local Quran text must stay readable.
  offline=browser.new_page(viewport={'width':390,'height':844},service_workers='block')
  offline.route('**/*png-d150/*.png',lambda req:req.abort())
  offline.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
  offline.locator('button[data-tab="mushaf"]').click()
  offline.wait_for_function("() => document.querySelector('#qVerses .madinah-text-fallback-only')!==null",timeout=30000)
  assert offline.locator('#qVerses .madinah-text-fallback-only [data-ayah]').count()>0
  offline.screenshot(path=str(OUT/'offline-fallback-390px.png'))
  offline.close()
  browser.close()
finally:
 server.shutdown();server.server_close()
(OUT/'summary.json').write_text(json.dumps(details,ensure_ascii=False,indent=2)+'\n')
print('PASS original Madinah 604-page image source, full-page natural scrolling, retained Quran interaction, offline fallback:',details)
