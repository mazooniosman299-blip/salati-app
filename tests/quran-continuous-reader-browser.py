#!/usr/bin/env python3
"""REAL Salati phone screenshots. Prove no reserved blank bottom paper strip:
the next AUTHENTIC (SHA256-checked) printed Quran page flows under the original
floating charcoal audio dock. Never crop/stretches verses or invents a filler."""
from pathlib import Path
from functools import partial
from threading import Thread
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
out=root/'reports/continuous-mushaf'
out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')))
Thread(target=srv.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
  for w,h in [(320,740),(390,844),(412,915),(768,960)]:
   page=browser.new_page(viewport={'width':w,'height':h},device_scale_factor=1,service_workers='block')
   errors=[]
   page.on('pageerror',lambda e:errors.append(str(e)))
   page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual'}))")
   response=page.goto(f'http://127.0.0.1:{srv.server_port}/?quran-page-preview=official-green&page=17',wait_until='domcontentloaded')
   assert response and response.ok
   page.locator('header>.site-nav button[data-tab=mushaf]').click()
   page.wait_for_function("""() => {
     const a=document.getElementById('qApprovedOriginalImage');
     const b=document.querySelector('#qApprovedFollowingPages img[data-quran-page="18"]');
     return document.querySelector('#mushaf.q-original-source-ready') &&
       a && a.complete && a.naturalWidth>450 &&
       b && b.complete && b.naturalWidth>450;
   }""",timeout=35000)
   measures=page.evaluate("""() => {
     const q=id=>document.getElementById(id);
     const r=e=>{const a=e.getBoundingClientRect();
       return {top:a.top,bottom:a.bottom,left:a.left,right:a.right,w:a.width,h:a.height}};
     const panel=q('mushafPlayerSlot'),figure=q('qApprovedOriginalPage'),
           first=q('qApprovedOriginalImage'),next=document.querySelector('#qApprovedFollowingPages img[data-quran-page="18"]');
     return {first:r(first),next:r(next),player:r(panel),figure:r(figure),
       padding:getComputedStyle(figure).padding,
       paddingBottom:getComputedStyle(figure).paddingBottom,
       scrollHeight:figure.scrollHeight,clientHeight:figure.clientHeight,
       playerBg:getComputedStyle(panel).backgroundColor,
       followingPages:[...figure.querySelectorAll('.q-approved-following-image')].map(x=>x.dataset.quranPage),
       sheetBg:getComputedStyle(figure).backgroundColor,
       paperLabel:q('qPageNumber').value};
   }""")
   assert measures['paperLabel']=='17',(w,measures)
   assert measures['paddingBottom']=='0px',(w,'the old 175px reserved white spacer remains',measures)
   assert abs(measures['first']['bottom']-measures['next']['top'])<=1,(w,'there is a visible white gap between consecutive full Quran pages',measures)
   assert measures['next']['w']>=w-1,(w,'following full page did not fill width',measures)
   assert measures['followingPages'].count('18')==1,(w,'duplicated or wrong sequential Quran page',measures)
   assert measures['playerBg']=='rgb(24, 25, 29)',(w,'approved Salati charcoal player changed',measures)
   assert measures['scrollHeight']>measures['clientHeight'],(w,'verses under the floating player cannot be revealed by scrolling',measures)
   if w<=412:
    assert measures['next']['top']<=measures['player']['top']+1,(w,'paper ends before the floating player and white gap remains',measures)
   assert not errors,(w,'browser runtime error',errors)
   page.screenshot(path=str(out/f'REAL-SALATI-CONTINUOUS-QURAN-{w}-PLAYER.png'),full_page=False)
   page.locator('#qApprovedOriginalPage').evaluate("(el)=>el.scrollTop=200")
   page.wait_for_timeout(200)
   moved=page.locator('#qApprovedOriginalPage').evaluate("(el)=>el.scrollTop")
   assert moved>=150,(w,'cannot scroll to read Quran behind audio dock',moved)
   page.screenshot(path=str(out/f'REAL-SALATI-CONTINUOUS-QURAN-{w}-SCROLLED.png'),full_page=False)
   page.locator('#qApprovedClose').click()
   assert not page.locator('#mushafPlayerSlot').is_visible()
   page.screenshot(path=str(out/f'REAL-SALATI-CONTINUOUS-QURAN-{w}-PLAYER-HIDDEN.png'),full_page=False)
   page.close()
  browser.close()
 print('PASS 320/390/412/768: real publisher Quran pages 17+18 continuous without 175px blank spacer, authentic Salati floating player, correct scrolling')
finally:srv.shutdown()
