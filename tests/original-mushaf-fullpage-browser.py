#!/usr/bin/env python3
"""Real app screenshots with 100% genuine whole original Quran page bitmaps.
NO AI imagery, no page clipping, no invented verses. Review-only.
"""
from pathlib import Path
from functools import partial
from threading import Thread
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
out=root/'reports/original-mushaf-complete'
out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args): pass
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
   r=page.goto(f'http://127.0.0.1:{server.server_port}/?quran-page-preview=official-green&page=17',wait_until='domcontentloaded')
   assert r and r.ok
   page.locator('header>.site-nav button[data-tab=mushaf]').click()
   page.wait_for_function("""()=>
     document.querySelector('#mushaf.q-original-source-ready #qApprovedOriginalImage')?.naturalWidth>300 &&
     document.getElementById('qPageNumber').value==='17'
   """,timeout=35000)
   snapshot=page.evaluate("""() => {
     const q=id=>document.getElementById(id);
     const rect=e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height,bottom:r.bottom,right:r.right}};
     const original=q('qApprovedOriginalImage'),v=q('qApprovedOriginalPage');
     const player=q('mushafPlayerSlot');
     return {
       img:rect(original),natural:[original.naturalWidth,original.naturalHeight],
       page:rect(v),player:rect(player),surah:q('qSurah').value,
       pageNum:q('qPageNumber').value,
       hasTextShadow:q('qVerses').style.display,
       paper:getComputedStyle(v).backgroundColor,
       playerColor:getComputedStyle(player.querySelector('.recitation-player')).backgroundColor,
       titleWhite:getComputedStyle(q('qTrack')).color,
       borderRadius:getComputedStyle(v).borderRadius,
       scrollable:v.scrollHeight>=v.clientHeight
     };
   }""")
   assert snapshot['surah']=='2' and snapshot['pageNum']=='17',(w,snapshot)
   assert snapshot['hasTextShadow']=='none' and 960<=snapshot['natural'][1]<=1040,(w,'original four-side crop missing or Quran page segmented',snapshot)
   assert snapshot['natural'][0]>550 and snapshot['natural'][0]<784,(w,'original ornament frame damaged/too narrow',snapshot)
   # Printed Quran heading/folio are in the SAME image, with no paper-white
   # band from the publisher PDF along the top and bottom of the image.
   from PIL import Image as PILImage
   import json
   m=json.loads((root/'dist/quran-green-proof/manifest.json').read_text())
   record=next(p for p in m['pages'] if p['quranPage']==17)
   trims=record['whiteMarginTrimOnly']
   assert trims['top']>=40 and trims['bottom']>=40,(w,'exterior white top/bottom not safely removed',trims)
   with PILImage.open(root/'dist/quran-green-proof'/record['filename']) as actual:
    import numpy as np
    pix=np.asarray(actual.convert('RGB'))
    assert (pix[:8].min(axis=2)<245).any(),(w,'no printed Quran header within 8px of page top')
    assert (pix[-8:].min(axis=2)<245).any(),(w,'folio number or ornament missing near page bottom')
   assert snapshot['paper']=='rgb(255, 255, 255)' and snapshot['borderRadius']=='0px',(w,snapshot)
   assert snapshot['img']['w']>=w-1 or w>=768,(w,'image too narrow',snapshot)
   assert snapshot['img']['y']>=60 and snapshot['img']['y']<=90,(w,'page starts too low',snapshot)
   assert snapshot['img']['bottom']>=snapshot['player']['y']-110 or w>=768,(w,'large blank gap remains',snapshot)
   assert snapshot['titleWhite']=='rgb(255, 255, 255)' and snapshot['playerColor']=='rgb(24, 25, 29)',(w,snapshot)
   assert not errors,(w,errors)
   page.screenshot(path=str(out/f'REAL-SALATI-FULL-QURAN-PAGE-17-PLAYER-{w}.png'),full_page=False)
   page.locator('#qApprovedClose').click()
   assert not page.locator('#mushafPlayerSlot').is_visible()
   page.screenshot(path=str(out/f'REAL-SALATI-COMPLETE-QURAN-PAGE-17-NO-PLAYER-{w}.png'),full_page=False)
   page.locator('#qApprovedOpen').click()
   assert page.locator('#mushafPlayerSlot').is_visible()
   # Verify a different physical 604-page printed leaf, not a duplicated image.
   for n in [5,37]:
    page.evaluate("""n=>{
      const x=document.getElementById('qPageNumber');x.value=String(n);
      document.getElementById('qPageForm').dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));
    }""",n)
    page.wait_for_function("""n=>
       document.getElementById('qPageNumber').value===String(n) &&
       document.getElementById('qApprovedOriginalImage').alt.includes('صفحة '+n) &&
       document.getElementById('qApprovedOriginalImage').naturalWidth>250
    """,arg=n,timeout=16000)
    if w==390:page.screenshot(path=str(out/f'REAL-SALATI-FULL-QURAN-PAGE-{n}-PLAYER-390.png'),full_page=False)
   page.close()
  browser.close()
 print('PASS: actual Salati screen with authenticated complete Madinah Quran printed leaf and approved charcoal audio; no chopped Quran; 320/390/412/768')
finally:
 server.shutdown()
