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
# This geometric next page is deliberately NOT Quran text or production artwork.
svg_paths2=''.join(f'<path class="ayahPolygon" surah="2" ayah="{n}" number="002{n:03d}" d="M 2 {n*70} L 342 {n*70} L 342 {n*70+60} L 2 {n*70+60} Z" fill-opacity="0"/>' for n in range(1,6))
fixture2='<svg xmlns="http://www.w3.org/2000/svg" viewBox="-53 -198 345 550"><g id="content"><path d="M0 0 L300 0 L300 300 L0 300 Z" fill="#bbb"/></g>'+svg_paths2+'</svg>'+' '*12000
checks=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  for width,height in ((360,780),(390,844)):
   for variant in ('printed','mirror','fallback'):
    page=browser.new_page(viewport={'width':width,'height':height},service_workers='block',reduced_motion='reduce')
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual',dark:true}));")
    def route_svg(route):
     is_cdn='cdn.quran.ws' in route.request.url
     allow=(variant=='printed' and is_cdn) or (variant=='mirror' and not is_cdn)
     if allow and route.request.url.endswith(('/001.svg','/002.svg')):
      original=fixture if route.request.url.endswith('/001.svg') else fixture2
      route.fulfill(status=200,body=original,headers={'Content-Type':'image/svg+xml','Access-Control-Allow-Origin':'*'})
     else: route.fulfill(status=503,body='test-only unavailable')
    page.route('https://cdn.quran.ws/svg/pages/v1.1.1/hafs-kfqc/**',route_svg)
    page.route('https://raw.githubusercontent.com/quran-ws/quran-svg/9fc0c87/mushafs/hafs/kfqc/svg/**',route_svg)
    page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded',timeout=35000)
    before=page.locator('header>.site-nav button[data-tab]').all_text_contents()
    assert len(before)==6,(width,'official six tabs missing',before)
    page.locator('header>.site-nav button[data-tab="mushaf"]').click()
    page.wait_for_function("document.body.classList.contains('salati-quran-immersive')",timeout=15000)
    page.locator('#qVerses .quran-reading-page').first.wait_for(timeout=25000)
    if variant in ('printed','mirror'):
     page.locator('#qVerses .salati-printed-page').first.wait_for(timeout=18000)
     assert page.locator('#qVerses .salati-publisher-plate [data-ayah="1:1"]').count()>=1
     page.locator('#qVerses .salati-publisher-plate [data-ayah="1:1"]').first.click(force=True)
     assert page.locator('#verseReciterMenu').count()>=1,'Original verse-tap audio menu missing'
     # Pull upward in the actual scrollport: the NEXT printed page must follow
     # in the same vertical reader, not appear behind arrow controls.
     page.locator('#qVerses .salati-printed-page[data-reading-page="2"]').wait_for(timeout=20000)
     assert page.locator('#qVerses .salati-printed-page[data-reading-page="1"]').count()==1
     assert page.locator('#qVerses .salati-printed-page[data-reading-page="2"]').count()==1
     page.locator('#qVerses').evaluate('e => { e.scrollTop=Math.min(e.scrollHeight-e.clientHeight,e.clientHeight*.7); e.dispatchEvent(new Event("scroll")); }')
     page.wait_for_function("document.querySelector('#qVerses').scrollTop>0",timeout=10000)
     # Virtualisation may unload an SVG once it is far offscreen. The ordered
     # Quran pages and printed bottom folios must still stay in the DOM.
     assert page.locator('#qVerses .quran-reading-page[data-reading-page="1"]').count()==1
     assert page.locator('#qVerses .quran-reading-page[data-reading-page="2"]').count()==1
     assert page.locator('#mushaf > .mushaf-pagination').is_hidden(),'Detached page counter shown outside Mushaf paper'
    else:
     page.wait_for_function("document.querySelector('#qVerses .quran-reading-page')?.dataset.plateUnavailable==='true'",timeout=20000)
     assert page.locator('#qVerses .quran-reading-page .quran-text').count()>0,'Network error blanked Quran text'
    if variant in ('printed','mirror'):
     # Real print surfaces occupy the reading viewport from its top edge,
     # and two adjacent printed leaves must NOT have white separator cards.
     seamless=page.evaluate("""() => {
      const sc=document.querySelector('#qVerses');
      sc.scrollTop=0;
      const one=sc.querySelector('.salati-printed-page[data-reading-page="1"]').getBoundingClientRect();
      const two=sc.querySelector('.salati-printed-page[data-reading-page="2"]').getBoundingClientRect();
      const area=sc.getBoundingClientRect();
      const menu=document.querySelector('.mushaf-toolbar').getBoundingClientRect();
      const plate=sc.querySelector('.salati-printed-page .salati-publisher-plate').getBoundingClientRect();
      const sheet=document.querySelector('#qSheet').getBoundingClientRect();
      const pad=getComputedStyle(sc.querySelector('.salati-printed-page'));
      return {top:one.top-area.top,gap:two.top-one.bottom,menuHeight:menu.height,
       plateWidth:plate.width,plateLeft:plate.left,plateRight:plate.right,
       pageLeft:one.left,pageRight:one.right,
       sheetLeft:sheet.left,sheetRight:sheet.right,
       pagePadLeft:parseFloat(pad.paddingLeft),pagePadRight:parseFloat(pad.paddingRight),
       scrollWidth:sc.scrollWidth,clientWidth:sc.clientWidth,
       contentHeight:sc.scrollHeight,readerHeight:sc.clientHeight};
     }""")
     assert abs(seamless['top'])<3,(width,'blank space above first Mushaf leaf',seamless)
     assert abs(seamless['gap'])<3,(width,'artificial white gap between two Mushaf pages',seamless)
     assert seamless['menuHeight']<2,(width,'tool panel steals vertical reading space',seamless)
     assert seamless['plateWidth']>=width-2,(width,'publisher page not screen width',seamless)
     # On the LIVE 390px production old card used 13.64px outer margins and
     # 15px inner padding per side, leaving only ~333px for scripture.
     # Both margins must now be ZERO in authentic printed-page mode.
     assert abs(seamless['plateLeft'])<2 and abs(seamless['plateRight']-width)<2,(width,'publisher ink still trapped inside production card margins',seamless)
     assert abs(seamless['pageLeft'])<2 and abs(seamless['pageRight']-width)<2,(width,'Quran page card still too narrow',seamless)
     assert abs(seamless['sheetLeft'])<2 and abs(seamless['sheetRight']-width)<2,(width,'qSheet still nested in padded main layout',seamless)
     assert seamless['pagePadLeft']<2 and seamless['pagePadRight']<2,(width,'old 15px page padding returned',seamless)
     assert seamless['scrollWidth']<=seamless['clientWidth']+2,(width,'horizontal crop/overflow',seamless)
     assert seamless['contentHeight']>seamless['readerHeight'],(width,'next leaf inaccessible by vertical scroll',seamless)
     # The same real Salati options button reveals original selectors only on demand.
     page.locator('#qReadingOptions').click()
     assert page.locator('#mushaf .mushaf-selectors').is_visible()
     page.locator('#qReadingOptions').click()
     assert page.locator('#mushaf .mushaf-selectors').is_hidden()
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
    if variant in ('printed','mirror'):
     # Future theme edits are allowed to change paint, never the
     # geometry, scroll direction, original nav, or player placement.
     baseline=page.evaluate("""() => {
      const r=document.querySelector('#qVerses').getBoundingClientRect();
      return {w:r.width,h:r.height,y:r.y,top:document.querySelector('#mushafPlayerSlot').getBoundingClientRect().top,
       total:document.querySelector('#qVerses').scrollHeight};
     }""")
     page.evaluate("""() => {
      const root=document.querySelector('#mushaf');
      root.style.setProperty('--mushaf-paper','#FFF8E8');
      root.style.setProperty('--mushaf-player','#17202C');
      root.style.setProperty('--mushaf-play','#2563EB');
     }""")
     themed=page.evaluate("""() => {
      const r=document.querySelector('#qVerses').getBoundingClientRect();
      return {w:r.width,h:r.height,y:r.y,top:document.querySelector('#mushafPlayerSlot').getBoundingClientRect().top,
       total:document.querySelector('#qVerses').scrollHeight,
       paper:getComputedStyle(document.querySelector('#qVerses')).backgroundColor,
       play:getComputedStyle(document.querySelector('#qTransport')).backgroundColor};
     }""")
     assert all(abs(themed[k]-baseline[k])<2 for k in ('w','h','y','top')),(width,'theme change mutated Quran geometry',baseline,themed)
     assert themed['paper']=='rgb(255, 248, 232)' and themed['play']=='rgb(37, 99, 235)',(width,'isolated theme tokens not respected',themed)
    page.screenshot(path=str(OUTPUT/f'{variant}-{width}.png'),animations='disabled')
    if variant in ('printed','mirror'):
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
assert len(checks)==6
print('PASS: 2 mobile sizes x primary/mirror/offline; two continuous printed pages; blue player; fullscreen geometry; original nav untouched. Print-image pixel parity not certified.')
