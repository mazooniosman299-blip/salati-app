#!/usr/bin/env python3
"""Actual Chromium/Android-WebView geometry contract for four user-approved UI edits.
Zero design recreation: tests the existing dist/index.html and original app script.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
out=root/'reports/four-regression-fixes'
out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')))
Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for width,height in [(320,740),(360,740),(390,844),(412,915),(480,900)]:
   page=b.new_page(viewport={'width':width,'height':height},service_workers='block')
   faults=[]
   page.on('pageerror',lambda e:faults.append(str(e)))
   page.add_init_script("""localStorage.setItem('salati',JSON.stringify({lat:23.588,lon:58.3829,zone:'Asia/Muscat',method:'Oman',madhab:'Shafi',name:'مسقط',locationSet:true,locationMode:'manual',lang:'ar'}));""")
   resp=page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
   assert resp and resp.ok,(width,'home not served')
   page.wait_for_function("document.querySelectorAll('#prayers .prayer').length===6")
   assert page.locator('link[href="preview-four-ui-changes-20261101.css"]').count()==1,(width,'correct preview css not active')
   cells=page.locator('#prayers .prayer').evaluate_all("""es=>es.map(e=>({x:e.getBoundingClientRect().x,y:e.getBoundingClientRect().y,right:e.getBoundingClientRect().right,bottom:e.getBoundingClientRect().bottom,scroll:e.scrollWidth,client:e.clientWidth,label:e.querySelector('span').textContent,time:e.querySelector('strong').textContent,bg:getComputedStyle(e).backgroundColor}))""")
   assert len({round(x['y']) for x in cells})==1,(width,'prayers must be one row',cells)
   assert all(c['x']>=-1 and c['right']<=width+1 for c in cells),(width,'all six must fit phone',cells)
   assert all(c['time'] and c['time']!='—' and '...' not in c['time'] for c in cells),(width,'full prayer time visible',cells)
   assert page.evaluate("document.documentElement.scrollWidth<=innerWidth"),(width,'horizontal overflow')
   assert all(c['bg']=='rgb(38, 39, 43)' for c in cells if c['label']!=''),'graphite prayer background must replace blue'
   page.screenshot(path=str(out/f'home-{width}.png'))
   assert 'تُحسب المواقيت على جهازك دون إرسال موقعك' not in page.locator('body').inner_text(),(width,'remove user-requested informational sentence')
   page.locator('[data-tab=mushaf]').click()
   page.wait_for_function("document.querySelector('#qVerses')?.textContent?.trim().length>35",timeout=20000)
   assert page.locator('#qSheet #mushafPlayerSlot #qTransport').count()==1,(width,'real player must be inside mushaf sheet')
   assert page.locator('#mushaf .mushaf-toolbar #mushafPlayerSlot').count()==0,(width,'player must NOT remain above Quran')
   props=page.locator('#mushafPlayerSlot').evaluate("e=>({position:getComputedStyle(e).position,bottom:getComputedStyle(e).bottom})")
   assert props['position']=='fixed',(width,'keep actual player fixed above nav while reading',props)
   assert page.locator('#mushafPlayerSlot').is_visible(),(width,'original audio player must not disappear')
   assert page.locator('#qSheet #mushafPlayerSlot').evaluate("e=>e.compareDocumentPosition(document.querySelector('#qVerses')) & Node.DOCUMENT_POSITION_FOLLOWING")!=0,(width,'player must precede infinitely long Quran verses')
   bounds=page.locator('#mushafPlayerSlot').evaluate("e=>({top:e.getBoundingClientRect().top,bottom:e.getBoundingClientRect().bottom,left:e.getBoundingClientRect().left,right:e.getBoundingClientRect().right})")
   nav_top=page.locator('header>.site-nav').evaluate("e=>e.getBoundingClientRect().top")
   assert bounds['bottom']<=nav_top+2 and bounds['bottom']>nav_top-95,(width,'audio controls above navbar',bounds,nav_top)
   assert bounds['top']>=0 and bounds['left']>=0 and bounds['right']<=width+1,(width,'player must be readable on mobile',bounds)
   page.screenshot(path=str(out/f'quran-player-{width}.png'))
   page.locator('main').evaluate('e=>e.scrollTop=Math.max(e.scrollTop,500)')
   after=page.locator('#mushafPlayerSlot').evaluate("e=>e.getBoundingClientRect().bottom")
   assert abs(after-bounds['bottom'])<=2,(width,'Quran player must stay near ayahs after scrolling',bounds,after)
   page.locator('[data-tab=settings]').click()
   page.locator('#nativeSettings').evaluate("e=>e.hidden=false") # WebView makes these visible with bridge
   for k in ['nativePermissions','nativeWidget']:
    v=page.locator('#'+k).evaluate("e=>({border:getComputedStyle(e).borderTopWidth,color:getComputedStyle(e).borderTopColor,bg:getComputedStyle(e).backgroundColor,r:e.getBoundingClientRect(),w:innerWidth})")
    assert v['border'] not in ('0px','none'),(width,k,'outlined translucent setting button',v)
    assert float(v['border'].removesuffix('px'))<=1.1,(width,k,'border thinner than rejected oversized frame',v)
    assert v['r']['x']>=-1 and v['r']['right']<=width+1,(width,k,'button clipped',v)
   page.screenshot(path=str(out/f'settings-{width}.png'))
   assert not faults,(width,'JavaScript errors',faults)
   page.close()
   print('PASS',width,'real app: six prayers same row, no privacy message, player INSIDE sheet, translucent settings outlines')
  b.close()
finally:
 server.shutdown()
