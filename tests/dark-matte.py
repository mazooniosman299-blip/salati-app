"""Actual Chromium acceptance for the user's permanent charcoal-only brief."""
from pathlib import Path
from functools import partial
from threading import Thread
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
import json
root=Path(__file__).resolve().parents[1]
out=root/'reports/dark-matte-1.0.103';(out/'screenshots').mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')));Thread(target=server.serve_forever,daemon=True).start()
checks=[]
try:
 with sync_playwright()as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  page=browser.new_page(service_workers='block',color_scheme='light');errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',dark:false,lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual',count:12,audio:{approachMinutes:5}}))")
  page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded');page.wait_for_selector('.nav-selection')
  assert page.locator('#theme').count()==0,'Remove theme toggle completely'
  assert page.locator('body').evaluate('(e)=>e.classList.contains("dark")')
  assert page.evaluate('JSON.parse(localStorage.salati).count')==12
  assert page.evaluate('JSON.parse(localStorage.salati).dark')is True
  assert page.locator('#times .recitation-player').count()==0
  for width in [360,390,412,768,1024,1366,1920]:
   page.set_viewport_size({'width':width,'height':1100})
   page.click('header [data-tab=times]');page.wait_for_timeout(180)
   dates=page.locator('#cityLabel,#gregorianDate,#dateLabel').evaluate_all('(es)=>es.map(e=>{const c=getComputedStyle(e),r=e.getBoundingClientRect();return {id:e.id,size:c.fontSize,weight:c.fontWeight,font:c.fontFamily,color:c.color,opacity:c.opacity,x:r.x,y:r.y,right:r.right,bottom:r.bottom}})')
   for date in dates[1:]:
    for field in ['font','color','opacity']:assert date[field]==dates[0][field],(width,field,dates)
    assert float(date['size'].removesuffix('px'))<float(dates[0]['size'].removesuffix('px'))
    assert date['color']=='rgb(255, 255, 255)'and date['opacity']=='1'
   assert page.locator('.hero-info small').count()==0
   assert page.locator('.hero-info').evaluate('(e)=>e.getBoundingClientRect().x>document.querySelector(".location").getBoundingClientRect().x')
   assert page.locator('#countdown').evaluate('(e)=>getComputedStyle(e).color')=='rgb(255, 255, 255)'
   assert page.locator('.hero-picture img').evaluate('(e)=>getComputedStyle(e).filter')=='none'
   assert page.locator('.hero-picture img').evaluate('(e)=>getComputedStyle(e).opacity')=='1'
   assert page.locator('#prayers .prayer').count()==6
   next_box=page.locator('#nextName').bounding_box();timer=page.locator('#countdown').bounding_box();assert timer['y']>=next_box['y']+next_box['height']-1
   for tab in ['times','mushaf','qibla','dhikr','tasbih','settings']:
    page.click('header [data-tab='+tab+']');page.wait_for_timeout(80)
    try:
     page.wait_for_function("document.body.classList.contains('dark') && getComputedStyle(document.getElementById('locate')).color === 'rgb(255, 255, 255)'",timeout=4000)
    except Exception:
     print('DARK_DIAGNOSTIC',page.evaluate("""() => ({classes:document.body.className,html:document.documentElement.className,locate:getComputedStyle(document.getElementById('locate')).color,styles:[...document.styleSheets].map(x=>x.href?.split('/').slice(-1)[0]),inline:document.getElementById('locate').outerHTML.slice(0,260)})"""))
     raise
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,tab,'horizontal overflow')
    assert page.locator('body').evaluate('(e)=>getComputedStyle(e).backgroundColor')=='rgb(11, 14, 19)'
    if width<761:
     nav=page.locator('header>.site-nav').bounding_box();assert nav['y']>700 and nav['y']+nav['height']<=1101
     assert page.locator('header>.site-nav [data-tab]').evaluate_all('(es)=>es.every(e=>e.getBoundingClientRect().height>=44)')
    if width in [390,1366]:page.screenshot(path=str(out/'screenshots'/f'{tab}-{width}.png'))
    button_colors=page.locator('button:not(:disabled)').evaluate_all('(es)=>es.filter(e=>e.getBoundingClientRect().width&&e.getBoundingClientRect().height).map(e=>({id:e.id,color:getComputedStyle(e).color}))')
    assert all(c['color']=='rgb(255, 255, 255)'for c in button_colors),(width,tab,button_colors)
    triggers=page.locator('button[aria-haspopup]')
    for i in range(triggers.count()):
     button=triggers.nth(i)
     if button.is_visible()and not button.is_disabled():
      button.click();assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.keyboard.press('Escape')
   checks.append({'width':width,'dates':dates,'six_tabs':'PASS'})
  page.click('header [data-tab=times]');page.click('#lang');assert page.locator('html').get_attribute('dir')=='ltr'
  assert page.locator('body').evaluate('(e)=>getComputedStyle(e).backgroundColor')=='rgb(11, 14, 19)'
  page.reload(wait_until='domcontentloaded');assert page.locator('body').evaluate('(e)=>e.classList.contains("dark")')
  assert not errors,errors
  for blocked in [False,True]:
   recovery=browser.new_page(service_workers='block',color_scheme='light')
   recovery_errors=[];recovery.on('pageerror',lambda e:recovery_errors.append(str(e)))
   recovery.add_init_script("Object.defineProperty(Storage.prototype,'getItem',{value(){throw new Error('blocked')}});Object.defineProperty(Storage.prototype,'setItem',{value(){throw new Error('blocked')}});"if blocked else "localStorage.setItem('salati','{broken')")
   recovery.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded');recovery.wait_for_selector('.nav-selection')
   assert recovery.locator('body').evaluate('(e)=>getComputedStyle(e).backgroundColor')=='rgb(11, 14, 19)'
   assert not recovery_errors,recovery_errors;recovery.close()
  first_paint=browser.new_page(java_script_enabled=False,color_scheme='light')
  first_paint.route('**/*.css',lambda route:route.abort())
  first_paint.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
  assert first_paint.locator('body').evaluate('(e)=>getComputedStyle(e).backgroundColor')=='rgb(11, 14, 19)'
  assert first_paint.locator('body').evaluate('(e)=>getComputedStyle(e).colorScheme')=='dark'
  first_paint.close();browser.close()
 (out/'acceptance.json').write_text(json.dumps({'result':'PASS','checks':checks,'page_errors':errors,'physical_device_tested':False},indent=2)+'\n')
 print('PASS: permanent dark theme, preserved settings, large city/smaller white date styles, correct right-side live title/name/countdown, original image, six tabs/menus at seven required widths, RTL/LTR and reload.')
finally:server.shutdown()
