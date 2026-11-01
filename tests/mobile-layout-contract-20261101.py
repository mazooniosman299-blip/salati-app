"""Prevent UI regressions: mobile settings, six rounded prayer capsules and fixed nav."""
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
  for width,height in [(320,700),(360,740),(390,844),(412,915),(430,932),(480,900),(768,1024)]:
   page=browser.new_page(viewport={'width':width,'height':height},service_workers='block')
   page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual'}))")
   errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
   assert page.locator('link[href="mobile-layout-contract-20261101.css"]').count()==1
   page.wait_for_function("document.querySelectorAll('#prayers .prayer').length===6")
   cells=page.locator('#prayers .prayer').evaluate_all("""es=>es.map(e=>({active:e.classList.contains('active'),x:e.getBoundingClientRect().x,right:e.getBoundingClientRect().right,bg:getComputedStyle(e).backgroundColor,radius:getComputedStyle(e).borderRadius}))""")
   assert len(cells)==6 and sum(c['active'] for c in cells)==1,(width,cells)
   assert all(c['radius']=='24px' for c in cells),(width,'reference capsule radius',cells)
   assert next(c for c in cells if c['active'])['bg']=='rgb(53, 74, 103)',(width,'blue-slate reference selected',cells)
   assert all(c['x']>=0 and c['right']<=width+1 for c in cells),(width,'prayer cells must fit')
   for tab in ['settings','times','mushaf','qibla','dhikr','tasbih','settings']:
    page.click(f'[data-tab={tab}]')
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,tab,'no horizontal page overflow')
    if width<=760:
     if tab=='settings':
      settingsBox=page.locator('#settings #preferences>.fields').evaluate("e=>({display:getComputedStyle(e).display,cols:getComputedStyle(e).gridTemplateColumns,latY:document.querySelector('#lat').getBoundingClientRect().y,lonY:document.querySelector('#lon').getBoundingClientRect().y})")
      assert settingsBox['display']=='grid',(width,'settings fields must be grid; grid-template-columns on flex is inert',settingsBox)
      if width<=430:assert settingsBox['lonY']>settingsBox['latY']+30,(width,'stack numeric controls on compact handset',settingsBox)
      else:assert abs(settingsBox['latY']-settingsBox['lonY'])<=3,(width,'two columns on wide handset',settingsBox)
     geo=page.evaluate("""() => {
      const rect=s=>{let r=document.querySelector(s).getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,right:r.right,bottom:r.bottom,top:r.top}};
      return {main:rect('main'),nav:rect('header>.site-nav'),card:rect('#settings .card'),audio:rect('#settings .audio-card'),form:rect('#settings #preferences'),fields:rect('#settings .fields'),lat:rect('#lat'),lon:rect('#lon'),zone:rect('#zone'),locationOpen:rect('#locationPickerOpen'),window:[innerWidth,innerHeight]};
     }""")
     assert all(geo[k] is not None for k in ['lat','lon','zone','locationOpen']),(width,tab,geo)
     assert geo['main']['x']>=-1 and geo['main']['right']<=width+1,(width,tab,'main must never exceed screen',geo)
     assert geo['nav']['x']>=-1 and geo['nav']['right']<=width+1,(width,tab,'nav width',geo)
     assert abs(geo['nav']['bottom']-height)<=2,(width,tab,'nav fixed to viewport bottom',geo)
     assert geo['main']['bottom']<=geo['nav']['top']-3,(width,tab,'nav does not overlap scrolling content',geo)
     for k in ['card','audio','form','fields','lat','lon','zone','locationOpen']:
      assert geo[k]['x']>=-1 and geo[k]['right']<=width+1,(width,tab,k+' must not be clipped',geo)
   if width<=760:
    # Reproduce native Android style mode without introducing a fake GPS bridge.
    page.locator('body').evaluate("e=>e.classList.add('native-android')")
    navBottom=page.locator('header>.site-nav').evaluate("e=>e.getBoundingClientRect().bottom")
    assert abs(navBottom-height)<=2,(width,'Android WebView nav must sit at viewport bottom',navBottom,height)
    page.click('[data-tab=settings]')
    page.locator('main').evaluate('e=>e.scrollTop=e.scrollHeight')
    page.screenshot(path=str(out/f'settings-end-{width}.png'))
    page.locator('main').evaluate('e=>e.scrollTop=0')
    page.screenshot(path=str(out/f'settings-top-{width}.png'))
    page.click('[data-tab=times]')
    page.screenshot(path=str(out/f'prayers-{width}.png'))
   assert not errors,(width,'browser exception',errors)
   stats.append({'viewport':[width,height],'six_rounded_reference_capsules':True,'settings_not_clipped':True,'nav_fixed_to_bottom':width<=760,'no_overlap':True,'errors':0})
   page.close()
  browser.close()
finally:
 server.shutdown()
(out/'results.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n')
print('PASS: settings/main never clip, selected prayer rounded blue-slate reference and nav stays at viewport bottom at six responsive sizes')
