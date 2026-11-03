#!/usr/bin/env python3
"""Browser proof on the REAL Salati shell (NOT pixel parity to the user's blue art).

A test-only synthetic SVG fixture is used to check geometry, Quran verse-tap
mapping and failure fallback deterministically. NEVER ship the test fixture as
a Quran page: actual publisher pages are fetched at runtime from pinned CDN.
"""
import json
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'reports'/'quran-immersive-browser'
OUTPUT.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args): pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'dist')))
Thread(target=server.serve_forever,daemon=True).start()
svg_paths=''.join(f'<path class="ayahPolygon" surah="1" ayah="{n}" number="001{n:03d}" d="M 2 {n*40} L 342 {n*40} L 342 {n*40+36} L 2 {n*40+36} Z" fill-opacity="0"/>' for n in range(1,8))
# No Arabic verses: this is an explicitly synthetic, non-production test shape.
fixture='<svg xmlns="http://www.w3.org/2000/svg" viewBox="-53 -198 345 550"><g id="content"><path d="M0 0 L300 0 L300 300 L0 300 Z" fill="#aaa"/></g>'+svg_paths+'</svg>'+' '*12000
checks=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  for width,height in ((360,780),(390,844)):
   for variant in ('printed','fallback'):
    page=browser.new_page(viewport={'width':width,'height':height},service_workers='block',reduced_motion='reduce')
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual',dark:true}));")
    def route_svg(route):
     if variant=='printed' and route.request.url.endswith('/001.svg'):
      route.fulfill(status=200,body=fixture,headers={'Content-Type':'image/svg+xml','Access-Control-Allow-Origin':'*'})
     else: route.fulfill(status=503,body='test-only unavailable')
    page.route('https://cdn.quran.ws/svg/pages/v1.1.1/hafs-kfqc/**',route_svg)
    page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded',timeout=35000)
    before=page.locator('header>.site-nav button[data-tab]').all_text_contents()
    assert len(before)==6,(width,'official six tabs missing',before)
    page.locator('header>.site-nav button[data-tab="mushaf"]').click()
    page.wait_for_function("document.body.classList.contains('salati-quran-immersive')",timeout=15000)
    page.locator('#qVerses .quran-reading-page').first.wait_for(timeout=25000)
    if variant=='printed':
     page.locator('#qVerses .salati-printed-page').first.wait_for(timeout=18000)
     assert page.locator('#qVerses .salati-publisher-plate [data-ayah="1:1"]').count()>=1
     page.locator('#qVerses .salati-publisher-plate [data-ayah="1:1"]').first.click(force=True)
     assert page.locator('#verseReciterMenu').count()>=1,'Original verse-tap audio menu missing'
    else:
     page.wait_for_function("document.querySelector('#qVerses .quran-reading-page')?.dataset.plateUnavailable==='true'",timeout=20000)
     assert page.locator('#qVerses .quran-reading-page .quran-text').count()>0,'Network error blanked Quran text'
    metrics=page.evaluate("""() => {
     const m=document.querySelector('#mushaf').getBoundingClientRect();
     const q=document.querySelector('#qVerses').getBoundingClientRect();
     const n=document.querySelector('header>.site-nav').getBoundingClientRect();
     const p=document.querySelector('#mushafPlayerSlot').getBoundingClientRect();
     const b=getComputedStyle(document.querySelector('#qTransport')).backgroundColor;
     return {m:{x:m.x,y:m.y,w:m.width,h:m.height},q:{x:q.x,y:q.y,w:q.width,h:q.height},nav:{top:n.top,bottom:n.bottom},player:{top:p.top,bottom:p.bottom},button:b,
      label:document.querySelector('#qPageLabel').getBoundingClientRect().height,
      scroller:getComputedStyle(document.querySelector('#qVerses')).overflowY};
    }""")
    assert abs(metrics['m']['x'])<2 and abs(metrics['m']['w']-width)<2,(width,metrics)
    assert metrics['q']['x']<2 and metrics['q']['w']>=width-2 and metrics['q']['h']>height*.45,(width,metrics)
    assert metrics['scroller'] in ('auto','scroll'),(width,metrics)
    assert metrics['button']=='rgb(37, 99, 235)',(width,'Blue play state regressed',metrics)
    assert metrics['q']['y']>0 and metrics['player']['top']>=metrics['q']['y']+metrics['q']['h']-2,(width,metrics)
    assert metrics['nav']['top']>=metrics['player']['bottom']-3,(width,'Player covers original nav',metrics)
    assert metrics['label']==0,(width,'Duplicate top page number',metrics)
    page.screenshot(path=str(OUTPUT/f'{variant}-{width}.png'),animations='disabled')
    if variant=='printed':
     page.locator('header>.site-nav button[data-tab="times"]').click()
     page.wait_for_function("!document.body.classList.contains('salati-quran-immersive')")
     assert page.locator('#times .hero-picture img').count()==1
     assert page.locator('header>.site-nav button[data-tab]').all_text_contents()==before,'Original nav changed'
    assert not errors,(width,variant,'Browser JS errors',errors[:5])
    checks.append({'viewport':[width,height],'scenario':variant,'metrics':metrics,'label':'real Salati browser, test-only non-Quran SVG for geometry'})
    page.close()
  browser.close()
finally:
 server.shutdown()
 server.server_close()
(OUTPUT/'checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
assert len(checks)==4
print('PASS 2 mobile sizes, fullscreen exact width, viewport scrollport, blue play, no overlaps, original nav preserved, printed SVG verse tap and offline fallback. NO visual plate pixel match claimed.')
