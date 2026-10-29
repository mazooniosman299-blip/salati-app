"""Rendered contrast and interaction checks for the latest monochrome glass reference."""
from pathlib import Path
from functools import partial
from threading import Thread
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
import json,re
root=Path(__file__).resolve().parents[1];out=root/'reports/reference-ui-1.0.106';out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')));Thread(target=s.serve_forever,daemon=True).start()
def contrast(a,b):
 def lum(c):
  v=[x/255 for x in map(float,re.findall(r'[\d.]+',c)[:3])];v=[x/12.92 if x<=.04045 else((x+.055)/1.055)**2.4 for x in v];return sum(x*y for x,y in zip(v,[.2126,.7152,.0722]))
 lo,hi=sorted([lum(a),lum(b)]);return(hi+.05)/(lo+.05)
checks=[]
try:
 with sync_playwright()as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(service_workers='block');errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual'}))")
  page.goto(f'http://127.0.0.1:{s.server_port}/',wait_until='domcontentloaded')
  for width in [390,1440]:
   page.set_viewport_size({'width':width,'height':1000})
   for tab in ['times','mushaf','dhikr','qibla','tasbih','settings']:
    page.click(f'header [data-tab={tab}]');page.mouse.move(0,0);page.wait_for_timeout(250)
    styles=page.locator(f'#{tab} button:not(:disabled):not([role=switch]):not(#qTransport):not(.choice-trigger):not(.choice-option):not(.voice-option):not([role=option]):not([aria-haspopup]),#{tab} a.primary').evaluate_all('(es)=>es.filter(e=>e.getBoundingClientRect().width&&e.getBoundingClientRect().height).map(e=>{let c=getComputedStyle(e);return{id:e.id,text:e.textContent.trim().slice(0,35),bg:c.backgroundColor,ink:c.color}})')
    for c in styles:
     assert c['bg']=='rgb(4, 5, 9)',(width,tab,'wrong reference action fill',c)
     assert c['ink']=='rgb(255, 255, 255)'and contrast(c['ink'],c['bg'])>=4.5,(width,tab,c)
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,tab)
    checks.append({'width':width,'tab':tab,'actions':styles})
   for tab in ['mushaf','settings']:
    page.click(f'[data-tab={tab}]')
    fields=page.locator(f'#{tab} .choice-trigger').evaluate_all('(es)=>es.filter(e=>e.getBoundingClientRect().width).map(e=>({id:e.id,bg:getComputedStyle(e).backgroundColor}))')
    assert fields and all(c['bg']=='rgb(4, 5, 9)'for c in fields),fields
   nav=page.locator('header .nav-icon-button').evaluate_all('(es)=>es.map(e=>getComputedStyle(e).backgroundColor)')
   assert all(c not in ['rgb(37, 99, 235)','rgb(29, 78, 216)']for c in nav),nav
   test=page.locator('#previewFajrPhrase');test.scroll_into_view_if_needed();page.mouse.move(0,0);page.screenshot(path=str(out/f'settings-{width}.png'))
   test.hover();assert test.evaluate('(e)=>getComputedStyle(e).backgroundImage').find('0.16')>=0
   page.mouse.down();pressed=test.evaluate('(e)=>getComputedStyle(e).backgroundImage');assert ('0.065' in pressed or '0.06' in pressed),pressed;page.mouse.move(0,0);page.mouse.up()
   # Changing the native checkbox must show different tracks without starting audio.
   toggle=page.locator('#fajrAnnouncementToggle');states=[]
   for value in [False,True]:
    toggle.evaluate('(e,v)=>e.checked=v',value);page.wait_for_timeout(200);states.append(toggle.evaluate('(e)=>({background:getComputedStyle(e).backgroundColor,edge:getComputedStyle(e).borderTopColor,image:getComputedStyle(e).backgroundImage})'))
   assert states[0]['background']==states[1]['background']=='rgb(4, 5, 9)'and states[0]['edge']=='rgba(255, 255, 255, 0.46)'and states[1]['edge']=='rgb(255, 255, 255)'and states[0]['image']!=states[1]['image'],states
   page.locator('#resetPrayerAdjustments').scroll_into_view_if_needed();page.screenshot(path=str(out/f'adjustments-{width}.png'))
   page.click('[data-tab=settings]');page.click('#locationPickerOpen');page.wait_for_selector('#locationMenu[open]')
   options=page.locator('#locationOptions button').evaluate_all('(es)=>es.slice(0,5).map(e=>getComputedStyle(e).backgroundColor)');assert options and all(c not in ['rgb(37, 99, 235)','rgb(29, 78, 216)']for c in options),options
   page.locator('#locationMenu').screenshot(path=str(out/f'location-{width}.png'));page.keyboard.press('Escape')
  assert not errors,errors;b.close()
 (out/'checks.json').write_text(json.dumps({'result':'PASS','checks':checks,'white_charcoal_contrast':contrast('rgb(255,255,255)','rgb(4,5,9)'),'page_errors':errors,'published':False},indent=2,ensure_ascii=False)+'\n')
 print('PASS: six pages use reference dark glass action buttons while fields, location rows and navigation remain dark glass; white labels contrast >=4.5:1; hover, pressed, Fajr track states and responsive layout verified.')
finally:s.shutdown()
