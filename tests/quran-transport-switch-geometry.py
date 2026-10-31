"""Live Chromium geometry regression for Quran transport and two toggles."""
from pathlib import Path
from functools import partial
from threading import Thread
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
import json
root=Path(__file__).resolve().parents[1]
folder=root/'reports/quran-controls-geometry'
folder.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')))
Thread(target=server.serve_forever,daemon=True).start()
checks=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  for width in [320,390,760,1440]:
   page=browser.new_page(viewport={'width':width,'height':920},service_workers='block')
   errs=[]
   page.on('pageerror',lambda e:errs.append(str(e)))
   page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
   page.click('[data-tab=mushaf]')
   page.wait_for_function("document.querySelector('#qSurah').options.length>=114")
   transport=page.locator('#qTransport')
   metrics=transport.evaluate("""e=>{let r=e.getBoundingClientRect(),s=getComputedStyle(e),p=getComputedStyle(e,'::before'),v=e.querySelector('svg').getBoundingClientRect();
     return {width:r.width,height:r.height,ratio:r.width/r.height,display:s.display,radius:s.borderRadius,pseudoRadius:p.borderRadius,pseudoInset:p.inset,icon:[v.width,v.height],pseudoColor:p.backgroundColor}}""")
   assert abs(metrics['ratio']-1)<.001 and metrics['width']==44 and metrics['height']==44,(width,'transport not circular',metrics)
   assert metrics['radius']=='50%' and metrics['pseudoRadius']=='50%',(width,metrics)
   assert metrics['pseudoColor']=='rgb(37, 99, 235)',(width,metrics)
   assert metrics['icon']==[17,17],(width,metrics)
   toggle_metrics=[]
   for id in ['qRepeat','qAutoNext']:
    el=page.locator('#'+id)
    for expected in [False,True,False]:
     el.evaluate('(e,v)=>e.checked=v',expected)
     page.wait_for_timeout(180)
     m=el.evaluate("""e=>{let r=e.getBoundingClientRect(),s=getComputedStyle(e),p=getComputedStyle(e,'::after');
     let a=p.transform; let n=new DOMMatrixReadOnly(a);return{w:r.width,h:r.height,radius:s.borderRadius,thumbW:parseFloat(p.width),thumbH:parseFloat(p.height),thumbRadius:p.borderRadius,thumbLeft:parseFloat(p.left),translation:n.m41,trackColor:s.backgroundColor,thumbColor:p.backgroundColor,checked:e.checked}}""")
     assert m['w']==54 and m['h']==32 and m['thumbW']==24 and m['thumbH']==24,(width,id,expected,m)
     assert m['thumbRadius']=='50%' and m['thumbLeft']==4 and m['thumbColor']=='rgb(255, 255, 255)',(width,id,expected,m)
     assert abs(m['translation']-(22 if expected else 0))<.2,(width,id,expected,m)
     assert m['trackColor']==('rgb(37, 99, 235)' if expected else 'rgb(11, 14, 19)'),(width,id,expected,m)
     toggle_metrics.append({'id':id,'state':expected,'values':m})
    el.click()
    assert el.is_checked(),(width,id,'click must toggle state')
   page.locator('#mushaf .quran-play-options').screenshot(path=str(folder/f'toggles-{width}.png'))
   page.locator('#mushaf .reference-player').screenshot(path=str(folder/f'player-{width}.png'))
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
   assert not errs,(width,errs)
   checks.append({'width':width,'play':metrics,'toggles':toggle_metrics})
   page.close()
  browser.close()
 (folder/'results.json').write_text(json.dumps({'passed':True,'screens':checks},ensure_ascii=False,indent=2)+'\n')
 print('PASS: 44px circular play; both 54x32 pill tracks and 24x24 round thumbs, click state and colors at 4 responsive widths')
finally:
 server.shutdown()
