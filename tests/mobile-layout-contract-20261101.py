"""Prevent UI regressions: mobile settings, six square prayer cells and fixed nav."""
from functools import partial
from pathlib import Path
from threading import Thread
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
import json
root=Path(__file__).resolve().parents[1]
out=root/'reports/mobile-layout-contract'
out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')))
Thread(target=server.serve_forever,daemon=True).start()
stats=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  for width,height in [(320,700),(360,740),(390,844),(412,915),(430,932),(768,1024)]:
   page=browser.new_page(viewport={'width':width,'height':height},service_workers='block')
   page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual'}))")
   errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
   assert page.locator('link[href="mobile-layout-contract-20261101.css"]').count()==1
   page.wait_for_function("document.querySelectorAll('#prayers .prayer').length===6")
   cells=page.locator('#prayers .prayer').evaluate_all("""es=>es.map(e=>({active:e.classList.contains('active'),x:e.getBoundingClientRect().x,right:e.getBoundingClientRect().right,bg:getComputedStyle(e).backgroundColor,radius:getComputedStyle(e).borderRadius}))""")
   assert len(cells)==6 and sum(c['active'] for c in cells)==1,(width,cells)
   assert all(c['radius']=='8px' for c in cells),(width,'square glass cells',cells)
   assert next(c for c in cells if c['active'])['bg']=='rgba(0, 0, 0, 0.72)',(width,'black translucent selected',cells)
   assert all(c['x']>=0 and c['right']<=width+1 for c in cells),(width,'prayer cells must fit')
   for tab in ['settings','times','mushaf','qibla','dhikr','tasbih','settings']:
    page.click(f'[data-tab={tab}]')
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,tab,'no horizontal page overflow')
    if width<=760:
     geo=page.evaluate("""() => {
      const rect=s=>{let r=document.querySelector(s).getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,right:r.right,bottom:r.bottom,top:r.top}};
      return {main:rect('main'),nav:rect('header>.site-nav'),card:rect('#settings .card'),audio:rect('#settings .audio-card'),form:rect('#settings #preferences'),fields:rect('#settings .fields'),window:[innerWidth,innerHeight]};
     }""")
     assert geo['main']['x']>=-1 and geo['main']['right']<=width+1,(width,tab,'main must never exceed screen',geo)
     assert geo['nav']['x']>=-1 and geo['nav']['right']<=width+1,(width,tab,'nav width',geo)
     assert abs(geo['nav']['bottom']-height)<=2,(width,tab,'nav fixed to viewport bottom',geo)
     assert geo['main']['bottom']<=geo['nav']['top']-3,(width,tab,'nav does not overlap scrolling content',geo)
     for k in ['card','audio','form','fields']:
      assert geo[k]['x']>=-1 and geo[k]['right']<=width+1,(width,tab,k+' must not be clipped',geo)
   if width<=760:
    page.click('[data-tab=settings]')
    page.locator('main').evaluate('e=>e.scrollTop=e.scrollHeight')
    page.screenshot(path=str(out/f'settings-end-{width}.png'))
    page.locator('main').evaluate('e=>e.scrollTop=0')
    page.screenshot(path=str(out/f'settings-top-{width}.png'))
    page.click('[data-tab=times]')
    page.screenshot(path=str(out/f'prayers-{width}.png'))
   assert not errors,(width,'browser exception',errors)
   stats.append({'viewport':[width,height],'six_cells_square_black_translucent':True,'settings_not_clipped':True,'nav_fixed_to_bottom':width<=760,'no_overlap':True,'errors':0})
   page.close()
  browser.close()
finally:
 server.shutdown()
(out/'results.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n')
print('PASS: settings/main never clip, selected prayer square black translucent and nav stays at viewport bottom at six responsive sizes')
