#!/usr/bin/env python3
"""Capture real Salati Quran-only installable trial UI; not an AI mockup."""
from pathlib import Path
from functools import partial
from threading import Thread
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
import json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports'/'quran-only-trial'
OUT.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args): pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'dist')))
Thread(target=server.serve_forever,daemon=True).start()
records=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
  for width,height in ((390,844),(430,932)):
   page=browser.new_page(viewport={'width':width,'height':height},service_workers='block')
   errors=[]
   page.on('pageerror',lambda error: errors.append(str(error)))
   page.add_init_script("""() => {
    localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,
     zone:'Asia/Muscat',name:'مسقط',method:'Oman',locationSet:true,
     locationMode:'manual',dark:true}));
   }""")
   response=page.goto('http://127.0.0.1:'+str(server.server_port)+'/',wait_until='domcontentloaded',timeout=35000)
   assert response and response.ok
   page.locator('header>.site-nav button[data-tab="mushaf"]').click()
   page.locator('#qVerses .quran-reading-page').first.wait_for(timeout=30000)
   page.wait_for_timeout(1800)
   metrics=page.evaluate("""() => {
    const css=(sel,pseudo='')=>{const e=document.querySelector(sel);return e?getComputedStyle(e,pseudo).backgroundColor:null};
    const rect=sel=>{const r=document.querySelector(sel).getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height}};
    const img=document.querySelector('#qTrialPlateImage');
    return {body:css('body'),panel:css('#mushafPlayerSlot'),blue:css('#qTransport','::before'),
      appVisible:!document.querySelector('#mushaf').hidden,
      readerPresent:document.querySelector('#qVerses .quran-reading-page')!==null,
      imageLoaded:img.complete && img.naturalWidth>100,
      trialActive:document.querySelector('#mushaf').classList.contains('quran-trial-active'),
      player:rect('#mushafPlayerSlot'),button:rect('#qTransport'),
      tabs:[...document.querySelectorAll('header>.site-nav button[data-tab]')].length,
      icons:['qStop','qPrevSurah','qTransport','qNextSurah','qLoopSurah'].every(id=>!!document.getElementById(id))};
   }""")
   assert metrics['body']=='rgb(11, 14, 19)',metrics
   assert metrics['panel']=='rgb(24, 25, 29)',metrics
   assert metrics['blue']=='rgb(37, 99, 235)',metrics
   assert metrics['tabs']==6 and metrics['icons'] and metrics['readerPresent'],metrics
   assert metrics['player']['width']>250 and metrics['button']['width']>=50,metrics
   page.screenshot(path=str(OUT/f'quran-real-app-{width}.png'),animations='disabled',full_page=True)
   if metrics['imageLoaded']:
    page.locator('#qTrialSwitch').click()
    assert page.evaluate("!document.querySelector('#mushaf').classList.contains('quran-trial-active')")
    assert page.locator('#qVerses .quran-reading-page').first.is_visible()
    page.locator('#qTrialSwitch').click()
    assert page.evaluate("document.querySelector('#mushaf').classList.contains('quran-trial-active')")
   page.locator('#qLoopSurah').click()
   assert page.locator('#qRepeat').is_checked()
   page.locator('#qLoopSurah').click()
   assert not page.locator('#qRepeat').is_checked()
   assert not errors,errors[:5]
   records.append({'viewport':[width,height],**metrics,'runtime_errors':errors})
   page.close()
  browser.close()
finally:
 server.shutdown();server.server_close()
(OUT/'metrics.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS real Salati Quran trial screenshots, original dark-blue palette, six-tab shell, genuine player IDs and functional repeat toggle')
print('External single-page sample loaded:',[x['imageLoaded'] for x in records])
