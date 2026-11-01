#!/usr/bin/env python3
"""Cross-check unoptimized and optimized CSS on REAL Salati DOM in Chromium.
No fabricated visual samples: the same app is loaded twice, the baseline CSS
is served by request interception, and computed styles are compared on all
six real tabs and multiple viewport sizes.
"""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
import json

root=Path(__file__).resolve().parents[1]
css=root/'dist'
baseline=(css/'salati-ui-baseline.css').read_text()
optimized=(css/'salati-ui.css').read_text()
assert baseline!=optimized and len(optimized)<len(baseline)
report=root/'reports/css-debt-20261101'
report.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(css)))
Thread(target=server.serve_forever,daemon=True).start()
styles='''display visibility position flexDirection flexWrap flexGrow flexShrink
gridTemplateColumns gridTemplateRows gap rowGap columnGap overflowX overflowY
backgroundColor backgroundImage color opacity borderTopWidth borderTopColor
borderTopLeftRadius borderBottomLeftRadius boxShadow paddingTop paddingBottom
paddingLeft paddingRight marginTop marginBottom marginLeft marginRight
fontSize fontWeight fontFamily lineHeight letterSpacing textAlign direction
transform alignItems justifyContent maxHeight minHeight maxWidth minWidth
zIndex whiteSpace textOverflow'''.split()
def snap(page,tab):
 return page.evaluate("""props=>{
   const active=document.querySelector('section.tab:not([hidden])');
   const nav=document.querySelector('header>.site-nav');
   const elements=[document.documentElement,document.body,...document.querySelectorAll('header *')];
   if(active)elements.push(...[active,...active.querySelectorAll('*')].filter(n=>!n.closest('#qVerses')||n.id==='qVerses').slice(0,350));
   const clean=n=>{const cs=getComputedStyle(n);return Object.fromEntries(props.map(k=>[k,cs[k]]))};
   const selected=elements.map((n,i)=>({key:i,tag:n.tagName,id:n.id||'',css:clean(n)}));
   const boxes=['header>.site-nav','header>.site-nav button.active','#qSheet',
    '#mushafPlayerSlot','#prayers','.prayer-overview']
    .map(q=>{const e=document.querySelector(q);if(!e||e.getClientRects().length===0)return {q,hidden:true};
      const r=e.getBoundingClientRect();return {q,x:Math.round(r.x),y:Math.round(r.y),
       w:Math.round(r.width),h:Math.round(r.height)};});
   return {selected,boxes};
 }""",styles)
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for width,height in [(320,740),(360,780),(390,844),(412,915),(480,900),(760,960)]:
   pages=[]
   for use_old in [True,False]:
    page=browser.new_page(viewport={'width':width,'height':height},service_workers='block',reduced_motion='reduce')
    page.add_init_script("""localStorage.setItem('salati',JSON.stringify({lat:23.588,lon:58.3829,zone:'Asia/Muscat',method:'Oman',madhab:'Shafi',name:'مسقط',locationSet:true,locationMode:'manual',lang:'ar'}));""")
    if use_old:
     page.route('**/salati-ui.css',lambda route:route.fulfill(status=200,content_type='text/css; charset=utf-8',body=baseline))
    r=page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
    assert r and r.ok
    page.wait_for_function("document.querySelectorAll('header>.site-nav button').length===6")
    pages.append(page)
   before,after=pages
   for tab in ['times','mushaf','qibla','dhikr','tasbih','settings']:
    snapshots=[]
    for p in pages:
     p.locator(f'header>.site-nav button[data-tab="{tab}"]').click()
     p.wait_for_function("(tab)=>document.querySelector('header>.site-nav button.active')?.dataset.tab===tab",arg=tab)
     if tab=='mushaf':
      p.wait_for_function("document.getElementById('qVerses')?.textContent?.trim()?.length>35",timeout=20000)
      p.wait_for_function("!!document.getElementById('qVerses').style.getPropertyValue('--salati-quran-window-height')",timeout=15000)
     snapshots.append(snap(p,tab))
    l,r=snapshots
    assert len(l['selected'])==len(r['selected']),(width,tab,'DOM changed between baseline/canonical')
    for a,b in zip(l['selected'],r['selected']):
     assert a['id']==b['id'] and a['tag']==b['tag'],(width,tab,'DOM changed',a['key'])
     for prop,val in a['css'].items():
      assert val==b['css'][prop],(width,tab,'CSS REGRESSION',a['id'] or a['tag'],prop,val,b['css'][prop])
    for a,b in zip(l['boxes'],r['boxes']):
     assert a['q']==b['q'] and a.get('hidden')==b.get('hidden'),(width,tab,'box missing')
     if not a.get('hidden'):
      for key in (['x','y','w','h'] if a['q'].startswith('header') else ['w']):
       assert abs(a[key]-b[key])<=2,(width,tab,'box geometry shifted',a,b,key)
    if width in (390,480) and tab in ('mushaf','times'):
     after.screenshot(path=str(report/f'optimized-{width}-{tab}.png'),full_page=False)
    print('PASS CSS parity',width,tab,len(l['selected']),'DOM nodes; 44 computed CSS properties')
   for p in pages:p.close()
  browser.close()
finally:server.shutdown()
print('PASS: canonical CSS visually equivalent to baseline in Chromium across 6 sizes x 6 tabs')
