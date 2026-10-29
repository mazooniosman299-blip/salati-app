"""Buttons keep intentional gaps without relying on whitespace in minified HTML."""
from pathlib import Path
from functools import partial
from threading import Thread
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
import json
root=Path(__file__).resolve().parents[1];out=root/'reports/reference-ui-1.0.106';out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')));Thread(target=s.serve_forever,daemon=True).start();checks=[]
try:
 with sync_playwright()as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(service_workers='block');page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual'}))")
  page.goto(f'http://127.0.0.1:{s.server_port}/',wait_until='domcontentloaded')
  for width in [320,390,760,1440]:
   page.set_viewport_size({'width':width,'height':1000})
   for tab in ['times','mushaf','qibla','dhikr','tasbih','settings']:
    page.click(f'[data-tab={tab}]');pairs=page.evaluate('''()=>{const out=[];for(const parent of document.querySelectorAll('footer>div,.audio-buttons,.adjust-actions,.adhkar-actions,.font-tools')){const buttons=[...parent.children].filter(e=>e.matches('button,a.primary')&&e.getBoundingClientRect().width);for(let i=1;i<buttons.length;i++){const a=buttons[i-1].getBoundingClientRect(),b=buttons[i].getBoundingClientRect(),overlap=Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top),gap=overlap>0?Math.max(a.left,b.left)-Math.min(a.right,b.right):Math.max(a.top,b.top)-Math.min(a.bottom,b.bottom);out.push({parent:parent.className||parent.tagName,gap});}}return out}''')
    assert all(x['gap']>=5.9 for x in pairs),(width,tab,pairs);assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,tab)
   page.locator('footer').screenshot(path=str(out/f'footer-{width}.png'));gap=page.locator('footer>div').evaluate('(e)=>getComputedStyle(e).gap');assert gap=='12px',gap;checks.append({'width':width,'footer_gap':gap})
  b.close()
 (out/'button-spacing.json').write_text(json.dumps({'result':'PASS','checks':checks},indent=2)+'\n');print('PASS: footer12px gap and button-group spacing across six pages/four widths; no horizontal overflow.')
finally:s.shutdown()
