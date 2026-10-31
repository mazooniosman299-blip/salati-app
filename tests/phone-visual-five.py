"""Live Chromium acceptance of five specific mobile Salati visual fixes."""
from pathlib import Path
from functools import partial
from threading import Thread
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
import json

root=Path(__file__).resolve().parents[1]
out=root/'reports/phone-five-visual'
out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')))
Thread(target=server.serve_forever,daemon=True).start()
results=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  for width in [390,1440]:
   page=browser.new_page(viewport={'width':width,'height':940},service_workers='block')
   page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual'}))")
   errors=[]
   page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
   page.wait_for_selector('header>.site-nav .nav-icon-button',state='visible')
   assert page.locator('link[href="design-restoration-v1.0.113.css"]').count()==1
   nav=page.locator('header>.site-nav .nav-icon-button')
   assert nav.count()==6
   navstyles=nav.evaluate_all("""els=>els.map(e=>{let s=getComputedStyle(e);let r=e.getBoundingClientRect();return{bg:s.backgroundColor,gradient:s.backgroundImage,border:s.borderTopWidth,borderColor:s.borderTopColor,icon:e.querySelector('svg')?.getBoundingClientRect().width,width:r.width,height:r.height}})""")
   assert all(n['bg']=='rgb(11, 14, 19)' and n['border']=='1px' and n['icon']>0 and n['width']>36 for n in navstyles),(width,'navigation icon tiles',navstyles)
   if width==390:
    assert all(n['height']>=54 for n in navstyles)
    assert nav.evaluate_all("""els=>els.every(e=>e.getBoundingClientRect().top===els[0].getBoundingClientRect().top)""")
   page.click('[data-tab=mushaf]')
   page.wait_for_function("document.querySelector('#qSurah').options.length >=114")
   reading=page.locator('#qSheet').evaluate("""e=>{let s=getComputedStyle(e),b=getComputedStyle(document.body);return{bg:s.backgroundColor,body:b.backgroundColor,border:s.borderTopWidth,outline:s.outlineWidth,color:s.color}}""")
   assert reading['bg']=='rgb(21, 26, 34)' and reading['bg']!=reading['body'] and reading['border']=='1px' and reading['color']=='rgb(255, 255, 255)',(width,reading)
   page.locator('#qSheet').screenshot(path=str(out/f'mushaf-{width}.png'))
   page.click('[data-tab=qibla]')
   qibla=page.locator('#qibla .qibla-card').evaluate("""e=>{let s=getComputedStyle(e);return{bg:s.backgroundColor,border:s.borderTopWidth,color:s.color}}""")
   assert qibla['bg']=='rgb(17, 22, 30)' and qibla['border']=='1px',(width,qibla)
   dial=page.locator('#qiblaDial').evaluate("""e=>{let s=getComputedStyle(e);return{bg:s.backgroundImage,border:s.borderTopWidth,color:s.borderTopColor}}""")
   assert dial['bg'].startswith('radial-gradient') and dial['border']=='2px',(width,dial)
   page.locator('#qibla .qibla-card').screenshot(path=str(out/f'qibla-{width}.png'))
   page.click('[data-tab=times]')
   page.wait_for_selector('#prayers .prayer')
   overview=page.locator('#times .prayer-overview').evaluate("""e=>{let s=getComputedStyle(e);return{bg:s.backgroundColor,border:s.borderTopWidth}}""")
   assert overview['border']=='1px',(width,overview)
   chips=page.locator('#times #prayers .prayer')
   assert chips.count()==6,(width,chips.count())
   styles=chips.evaluate_all("""es=>es.map(e=>{let s=getComputedStyle(e);return{bg:s.backgroundColor,border:s.borderTopWidth,active:e.classList.contains('active')}})""")
   assert all(x['border']=='1px' and x['bg'] in ('rgb(18, 23, 31)','rgb(36, 43, 54)') for x in styles),(width,styles)
   page.locator('#times .prayer-overview').screenshot(path=str(out/f'prayers-{width}.png'))
   # A single nav-safe gap, not the old two stacked bottom paddings.
   for tab in ('times','mushaf','qibla','dhikr','tasbih','settings'):
    page.click(f'[data-tab={tab}]')
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),(width,tab,'horizontal overflow')
    if width==390:
     space=page.locator(f'#{tab}').evaluate("""e=>{const s=getComputedStyle(e);return{padding:parseFloat(s.paddingBottom),minHeight:s.minHeight}}""")
     assert space['padding']<=12,(tab,'duplicate mobile footer spacer',space)
   if width==390:
    main=page.locator('main').evaluate("""e=>parseFloat(getComputedStyle(e).paddingBottom)""")
    assert main<=120,('single mobile nav-safe clearance',main)
   assert not errors,(width,errors)
   results.append({'width':width,'quran':reading,'qibla':qibla,'dial':dial,'prayers':overview,'chips':styles,'nav':navstyles,'errors':errors})
   page.close()
  browser.close()
 (out/'results.json').write_text(json.dumps({'passed':True,'checks':results},ensure_ascii=False,indent=2)+'\n')
 print('PASS: five phone visual fixes verified in real Chromium at 390 and 1440px, six tabs each')
finally:
 server.shutdown()
