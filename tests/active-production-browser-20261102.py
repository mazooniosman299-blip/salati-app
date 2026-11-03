#!/usr/bin/env python3
"""Current-source/browser proof, not retired stylesheet text fixtures.

Checks true active pages in Chromium at seven viewports, all six application
sections, the original scrollable Quran, responsive navigation and city grid.
Screenshots are evidence for user comparison; no claim of perfect pixel parity
with an unsupplied external reference image is made.
"""
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright
import json

root=Path(__file__).resolve().parents[1]
out=root/'reports/active-production-browser-20261102'
out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')))
Thread(target=server.serve_forever,daemon=True).start()
summary=[]
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  for width,height in [(320,740),(360,780),(390,844),(412,915),(480,900),(760,960),(1280,850)]:
   page=browser.new_page(viewport={'width':width,'height':height},service_workers='block',reduced_motion='reduce')
   errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   page.add_init_script("""localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',method:'Oman',locationSet:true,locationMode:'manual'}))""")
   response=page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded',timeout=30000)
   assert response and response.ok,(width,'homepage failed')
   page.evaluate('document.fonts.ready')
   assert page.locator('link[rel="stylesheet"]').evaluate_all("es=>es.map(e=>e.getAttribute('href'))")==['salati-ui.css']
   assert page.locator('script[src*="preview-sample-location"]').count()==0
   assert page.evaluate("getComputedStyle(document.body).backgroundColor")=='rgb(11, 14, 19)',(width,'body leaked another priority')
   assert page.locator('header>.site-nav button[data-tab]').count()==6
   page.wait_for_function("() => document.querySelectorAll('#prayers .prayer').length===6",timeout=15000)
   for tab in ('times','mushaf','qibla','dhikr','tasbih','settings'):
    if tab!='mushaf' and width>760 and page.locator('#qReaderBack').is_visible():page.locator('#qReaderBack').click()
    page.locator(f'header>.site-nav button[data-tab="{tab}"]').click()
    page.wait_for_function("(tab)=>document.querySelector('header>.site-nav button.active')?.dataset.tab===tab",arg=tab)
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(width,tab,'horizontal overflow')
    assert page.locator('header>.site-nav button.active').count()==1
    nav=page.locator('header>.site-nav').evaluate("""e=>{
      let b=e.getBoundingClientRect(),s=getComputedStyle(e);
      return {left:b.left,right:b.right,bottom:b.bottom,top:b.top,position:s.position}
    }""")
    assert nav['left']>=-1 and nav['right']<=width+1,(width,tab,nav)
    if width<=760:
     assert nav['position']=='fixed' and abs(nav['bottom']-height)<=2,(width,tab,'fixed nav',nav)
    clips=page.locator('header>.site-nav button span').evaluate_all("""es=>es.filter(e=>e.getBoundingClientRect().width>0).map(e=>e.scrollWidth-e.clientWidth)""")
    assert all(delta<=2 for delta in clips),(width,tab,'clipped label',clips)
    if tab=='mushaf':
     page.wait_for_selector('#qVerses .quran-reading-page',timeout=20000)
     q=page.locator('#qVerses')
     x=q.evaluate("""e=>({height:e.clientHeight,scrollHeight:e.scrollHeight,overflow:getComputedStyle(e).overflowY,
       pages:e.querySelectorAll('.quran-reading-page').length,arrows:e.querySelectorAll('button[data-next],button[data-prev]').length})""")
     assert x['height']>100 and x['scrollHeight']>=x['height'],(width,'Quran clipped',x)
     assert x['overflow'] in ('auto','scroll') and x['arrows']==0,(width,'Quran must use continuous scroll',x)
     assert page.locator('#mushafPlayerSlot').count()==1
     assert page.evaluate("!document.querySelector('#qVerses').contains(document.querySelector('#mushafPlayerSlot'))")
     if width==390:
      q.hover()
      for _ in range(12):
       page.mouse.wheel(0,800);page.wait_for_timeout(120)
      page.wait_for_function("() => document.querySelectorAll('#qVerses .quran-reading-page').length>=2",timeout=10000)
    if width in (390,1280):
     page.screenshot(path=str(out/f'{tab}-{width}px.png'),full_page=False)
   assert not errors,(width,'browser errors',errors[:6])
   summary.append({'viewport':[width,height],'tabs':6,'browser_errors':0})
   page.close()
  for lang in ('ar','en'):
   city=browser.new_page(viewport={'width':390,'height':844},service_workers='block')
   response=city.goto(f'http://127.0.0.1:{server.server_port}/{lang}/prayer-times/index.html',wait_until='domcontentloaded',timeout=30000)
   assert response and response.ok,(lang,'city directory failed')
   grid=city.locator('.city-directory-grid').first
   assert grid.count() and grid.evaluate("e=>getComputedStyle(e).display")=='grid',(lang,'city directory grid broken by removing !important')
   hidden=city.locator('[data-country-group][hidden],[data-city-search][hidden]')
   if hidden.count():
    assert hidden.evaluate_all("es=>es.every(e=>getComputedStyle(e).display==='none')"),(lang,'hidden directory entries visible')
   city.screenshot(path=str(out/f'city-directory-{lang}.png'))
   city.close()
  # Reproduce the first-load Android bridge condition without a stored city:
  # no PREVIEW data is allowed to prefill an unconsenting user's settings.
  fresh=browser.new_page(service_workers='block')
  fresh.add_init_script("window.SalatiNative={};localStorage.removeItem('salati');")
  fresh.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded',timeout=30000)
  state=fresh.evaluate("localStorage.getItem('salati') || '{}'")
  assert 'مسقط (معاينة)' not in state and 'salatiPreviewSampleAcknowledged' not in state,('Unauthorized sample data',state[:300])
  fresh.close()
  browser.close()
finally:
 server.shutdown();server.server_close()
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print('PASS active production browser: six tabs, seven viewports, continuous Quran, nav/strip, city directories, no preview location override')
