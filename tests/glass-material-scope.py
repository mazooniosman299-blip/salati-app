"""Reference glass has its own material; blue actions cannot recolor navigation or media."""
from pathlib import Path
from functools import partial
from threading import Thread
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
import json
root=Path(__file__).resolve().parents[1];out=root/'reports/audio-controls-1.0.109';out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')));Thread(target=s.serve_forever,daemon=True).start();checks=[]
try:
 with sync_playwright()as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(service_workers='block');errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual'}))")
  page.goto(f'http://127.0.0.1:{s.server_port}/',wait_until='domcontentloaded');page.click('[data-tab=mushaf]');page.wait_for_function('document.getElementById("qSurah").options.length>=114')
  for width in [320,390,760,1440]:
   page.set_viewport_size({'width':width,'height':1000});page.mouse.move(0,0);page.wait_for_timeout(350)
   nav=page.locator('header .nav-icon-button').evaluate_all('(es)=>es.map(e=>{let s=getComputedStyle(e);return{bg:s.backgroundColor,gradient:s.backgroundImage,border:s.borderTopColor,radius:s.borderRadius}})')
   assert len(nav)==6 and all(x['bg']=='rgb(4, 5, 9)'and'linear-gradient'in x['gradient']and x['border']=='rgba(255, 255, 255, 0.14)'for x in nav),nav
   assert all(x['radius']==('16px'if width<=760 else'20px')for x in nav),nav
   player=page.locator('.reference-player');styles=player.evaluate('(e)=>{let c=getComputedStyle(e),d=getComputedStyle(e.querySelector("#qTransport"),"::before");return{bg:c.backgroundColor,image:c.backgroundImage,border:c.borderTopColor,radius:c.borderRadius,disc:d.backgroundColor,discBorder:d.borderTopColor,discSize:parseFloat(d.width)+2*parseFloat(d.borderLeftWidth)}}')
   assert styles['bg']=='rgb(4, 5, 9)'and styles['disc']=='rgb(21, 61, 122)'and styles['border']=='rgba(255, 255, 255, 0.14)'and styles['radius']=='24px'and styles['discBorder']=='rgb(45, 93, 155)'and styles['discSize']==36,styles
   assert page.locator('#qTransport').bounding_box()['width']==44
   if width in [390,1440]:
    player.screenshot(path=str(out/f'player-{width}.png'));page.locator('header>.site-nav').screenshot(path=str(out/f'navigation-{width}.png'));page.screenshot(path=str(out/f'mushaf-{width}.png'))
   for tab in ['times','mushaf','dhikr','qibla','tasbih','settings']:
    page.click(f'[data-tab={tab}]');assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,tab)
   page.click('[data-tab=mushaf]');page.keyboard.press('Tab');page.locator('header .nav-icon-button.active').focus();focus=page.locator('header .nav-icon-button.active').evaluate('(e)=>({edge:getComputedStyle(e).borderTopColor,outline:getComputedStyle(e).outlineWidth})');assert focus=={'edge':'rgba(255, 255, 255, 0.65)','outline':'0px'},focus;page.locator('header .nav-icon-button.active').evaluate('(e)=>e.blur()');checks.append({'width':width,'navigation':nav,'player':styles})
  assert not errors,errors;b.close()
 (out/'glass-checks.json').write_text(json.dumps({'result':'PASS','cases':checks,'page_errors':errors,'published':False},indent=2)+'\n');print('PASS: charcoal reference material and white icons/frames stay separate from blue actions; 4 widths, 6 tabs, compact blue play disc, no overflow or page errors.')
finally:s.shutdown()
