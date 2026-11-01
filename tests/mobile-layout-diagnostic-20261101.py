"""Diagnose actual Salati mobile geometry before changing global CSS."""
from pathlib import Path
from functools import partial
from threading import Thread
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import json
root=Path(__file__).resolve().parents[1];out=root/'reports/mobile-layout-diagnostic';out.mkdir(parents=True,exist_ok=True)
class Silent(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Silent,directory=str(root/'dist')))
Thread(target=server.serve_forever,daemon=True).start()
rows=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for w,h in [(320,700),(360,740),(390,844),(412,915),(430,932)]:
   page=browser.new_page(viewport={'width':w,'height':h},device_scale_factor=1,service_workers='block')
   page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual'}))")
   errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
   page.wait_for_function("document.querySelectorAll('#prayers .prayer').length===6")
   page.click('[data-tab=times]')
   page.screenshot(path=str(out/f'times-{w}.png'))
   prayers=page.locator('#prayers .prayer').evaluate_all("""es=>es.map(e=>({className:e.className,rect:rect(e),background:getComputedStyle(e).backgroundColor,round:getComputedStyle(e).borderRadius,border:getComputedStyle(e).borderTopColor,padding:getComputedStyle(e).padding}))""".replace('rect(e)', '({x:e.getBoundingClientRect().x,y:e.getBoundingClientRect().y,width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height})'))
   page.click('[data-tab=settings]')
   metrics=page.evaluate("""() => {
     const rect=sel=>{const el=document.querySelector(sel);if(!el)return null;const r=el.getBoundingClientRect(),s=getComputedStyle(el);return {x:r.x,y:r.y,width:r.width,height:r.height,display:s.display,position:s.position,overflowY:s.overflowY,paddingBottom:s.paddingBottom,bottom:s.bottom,transform:s.transform}};
     return {viewport:[innerWidth,innerHeight],docHeight:document.documentElement.scrollHeight,bodyHeight:document.body.scrollHeight,mainScrollHeight:document.querySelector('main')?.scrollHeight,mainClientHeight:document.querySelector('main')?.clientHeight,
       elements:Object.fromEntries(['html','body','header','header>.site-nav','main','#settings','#settings .card','#settings .fields','#settings .location-field','#settings .prayer-switches','#settings .prayer-switches label','#settings .prayer-switches input','#settings .prayer-switches input:checked','#settings .minute-adjustments','#settings .adjust-grid','#settings .audio-card','#settings #voicePickerOpen','main>footer'].map(k=>[k,rect(k)])),
       navbarStyles:Array.from(document.querySelectorAll('header>.site-nav button')).map(el=>({text:el.innerText,rect:{x:el.getBoundingClientRect().x,y:el.getBoundingClientRect().y,width:el.getBoundingClientRect().width,height:el.getBoundingClientRect().height}}))};
   }""")
   page.screenshot(path=str(out/f'settings-viewport-{w}.png'))
   page.locator('#settings .card').first.screenshot(path=str(out/f'settings-card-{w}.png'))
   page.locator('#settings .audio-card').screenshot(path=str(out/f'settings-audio-{w}.png'))
   rows.append({'width':w,'height':h,'times':prayers,'settings':metrics,'errors':errors})
   page.close()
  browser.close()
finally:
 server.shutdown()
(out/'results.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
print('DIAGNOSTIC:',json.dumps([{'width':r['width'],'nav':r['settings']['elements']['header>.site-nav'],'main':r['settings']['elements']['main'],'settings':r['settings']['elements']['#settings'],'audioSwitch':r['settings']['elements']['#settings .prayer-switches input'],'activePrayer':[p for p in r['times'] if 'active' in p['className']],'errors':r['errors']} for r in rows],ensure_ascii=False))
