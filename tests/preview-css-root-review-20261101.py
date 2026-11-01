#!/usr/bin/env python3
"""Acceptance after CSS bundling: assert user screenshot fixes on REAL app UI.
No Quran page clipping, no CSS overrides from legacy links, compact nav.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright
import re

root=Path(__file__).resolve().parents[1]
dist=root/'dist'
report=root/'reports/css-root-review-20261101'
report.mkdir(parents=True,exist_ok=True)
html=(dist/'index.html').read_text()
styles=re.findall(r'<link\s+rel="stylesheet"\s+href="([^"]+\.css)"\s*>',html)
assert styles==['salati-ui.css','/city-pages.css'],('runtime still loads multiple/legacy CSS',styles)
assert (dist/'salati-ui.css').is_file() and (dist/'salati-ui.css').stat().st_size>100000
assert not (dist/'active-reference-nav-20261101.css').exists()
assert not (dist/'design-restoration-v1.0.113.css').exists()
assert "'./salati-ui.css'" in (dist/'sw.js').read_text()
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(dist)))
Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for w,h in ((320,740),(360,780),(390,844),(412,915),(480,900),(593,1280),(760,960)):
   p=browser.new_page(viewport={'width':w,'height':h},service_workers='block')
   faults=[]
   p.on('pageerror',lambda e:faults.append(str(e)))
   p.add_init_script("""localStorage.setItem('salati',JSON.stringify({lat:23.588,lon:58.3829,zone:'Asia/Muscat',method:'Oman',madhab:'Shafi',name:'مسقط',locationSet:true,locationMode:'manual',lang:'ar'}))""")
   response=p.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
   assert response and response.ok,(w,'load failed')
   p.wait_for_function("document.querySelectorAll('header>.site-nav button[data-tab]').length===6")
   for tab in ('times','mushaf','qibla','dhikr','tasbih','settings'):
    p.locator(f'header>.site-nav button[data-tab="{tab}"]').click()
    p.wait_for_function("(tab)=>document.querySelector('header>.site-nav button.active')?.dataset.tab===tab",arg=tab)
    data=p.evaluate("""()=>{
     const nav=document.querySelector('header>.site-nav'),box=nav.getBoundingClientRect();
     return {height:box.height,width:box.width,buttons:[...nav.querySelectorAll('button[data-tab]')].map(b=>{const s=getComputedStyle(b),t=b.querySelector('span');return {tab:b.dataset.tab,active:b.classList.contains('active'),color:s.backgroundColor,border:s.borderTopWidth,clip:t.scrollWidth-t.clientWidth}})};
    }""")
    assert len(data['buttons'])==6
    assert sum(b['active'] for b in data['buttons'])==1
    for b in data['buttons']:
     assert b['clip']<2,(w,tab,'cut label',b)
     if b['active']:assert b['color']=='rgb(17, 74, 183)',(w,tab,'selection not blue',b)
     else:assert b['color']=='rgba(0, 0, 0, 0)' and b['border']=='0px',(w,tab,'legacy inactive box',b)
    if w<=760:
     assert 57<=data['height']<=63,(w,tab,'nav not compact reference',data)
     assert data['width']>=w-20,(w,tab,'nav not full width',data)
    if tab=='mushaf':
     p.wait_for_function("document.querySelector('[data-ayah=\"1:7\"]')!==null",timeout=20000)
     d=p.evaluate("""()=>{
      const by=id=>document.getElementById(id),bounds=e=>{const r=e.getBoundingClientRect();return {top:r.top,bottom:r.bottom,left:r.left,right:r.right,height:r.height}};
      const root=by('qVerses'),sheet=by('qSheet'),player=by('mushafPlayerSlot'),last=root.querySelector('[data-ayah="1:7"]'),page=last.closest('.quran-reading-page');
      const rs=getComputedStyle(root);
      return {sheet:bounds(sheet),verses:bounds(root),last:bounds(last),page:bounds(page),player:bounds(player),
       pos:getComputedStyle(player).position,heightCSS:rs.height,maxHeightCSS:rs.maxHeight,overflowY:rs.overflowY,
       scrollHeight:root.scrollHeight,clientHeight:root.clientHeight,outside:!sheet.contains(player),firstPageContainsLast:page.contains(last)};
     }""")
     assert d['outside'] and d['firstPageContainsLast'],(w,'DOM Quran/player',d)
     assert d['verses']['bottom']>=d['last']['bottom']-2,(w,'last Fatiha verse outside Quran',d)
     assert d['sheet']['bottom']<=d['player']['top']+1,(w,'audio dock overlaps Quran',d)
     assert d['overflowY'] in ('visible','clip'),(w,'Quran still scroll-clipped',d)
     assert d['maxHeightCSS']=='none',(w,'Quran has hard maximum height',d)
     assert abs(d['scrollHeight']-d['clientHeight'])<5,(w,'Quran still has internally clipped content',d)
     if w in (360,390,593):
      p.screenshot(path=str(report/f'mushaf-{w}.png'),full_page=True)
   if faults:raise AssertionError((w,'JS errors',faults))
   p.close()
   print('PASS',w,'one runtime CSS, six movable blue tabs, no clipped Quran, player below parchment')
  browser.close()
finally:
 server.shutdown()
