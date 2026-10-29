"""Only on/off switches and audio playback controls are blue; other UI remains glass."""
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
  page.goto(f'http://127.0.0.1:{s.server_port}/',wait_until='domcontentloaded')
  for width in [390,1440]:
   page.set_viewport_size({'width':width,'height':1000});page.click('[data-tab=settings]')
   switches=page.locator('[data-audio-prayer],#fajrAnnouncementToggle,#audioEnable,#duaToggle,#silentAdhanToggle')
   assert switches.count()==9
   for switch in switches.all():
    original=switch.evaluate('(e)=>e instanceof HTMLInputElement?e.checked:e.getAttribute("aria-checked")==="true"')
    for enabled in [False,True]:
     switch.evaluate('(e,v)=>{if(e instanceof HTMLInputElement)e.checked=v;else{e.setAttribute("aria-checked",String(v));e.classList.toggle("is-on",v);}}',enabled)
     page.wait_for_timeout(250)
     c=switch.evaluate('(e)=>({fill:getComputedStyle(e).backgroundColor,edge:getComputedStyle(e).borderTopColor})')
     assert c=={'fill':'rgb(21, 61, 122)'if enabled else'rgb(11, 35, 71)','edge':'rgb(45, 93, 155)'},(switch.get_attribute('id'),enabled,c)
    switch.evaluate('(e,v)=>{if(e instanceof HTMLInputElement)e.checked=v;else{e.setAttribute("aria-checked",String(v));e.classList.toggle("is-on",v);}}',original)
   page.wait_for_timeout(300);page.locator('#previewFajrPhrase').scroll_into_view_if_needed();page.mouse.move(0,0);page.screenshot(path=str(out/f'settings-{width}.png'))
   for key in ['previewFajrPhrase','previewAdhan','previewDua','audioStop']:
    assert page.locator('#'+key).evaluate('(e)=>getComputedStyle(e).backgroundColor')=='rgb(21, 61, 122)',key
   for key in ['resetPrayerAdjustments','applyPrayerAdjustments','cancelPrayerAdjustments','locationPickerOpen','methodPickerOpen']:
    c=page.locator('#'+key).evaluate('(e)=>getComputedStyle(e).backgroundColor');assert c not in ['rgb(21, 61, 122)','rgb(26, 77, 145)'],(key,c)
   page.locator('#applyPrayerAdjustments').scroll_into_view_if_needed();page.screenshot(path=str(out/f'other-buttons-{width}.png'))
   page.click('[data-tab=mushaf]');page.wait_for_function('document.querySelector("#qSurah").options.length>=114')
   assert page.locator('#qTransport').evaluate('(e)=>getComputedStyle(e,"::before").backgroundColor')=='rgb(21, 61, 122)'
   for key in ['qRepeat','qAutoNext']:
    for enabled in [False,True]:
     el=page.locator('#'+key);el.evaluate('(e,v)=>e.checked=v',enabled);page.wait_for_timeout(250);actual=el.evaluate('(e)=>getComputedStyle(e).backgroundColor');assert actual==('rgb(21, 61, 122)'if enabled else'rgb(11, 35, 71)'),(width,key,enabled,actual)
   page.locator('.reference-player').screenshot(path=str(out/f'player-{width}.png'))
   for tab in ['times','mushaf','dhikr','qibla','tasbih','settings']:
    page.click(f'[data-tab={tab}]');assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,tab)
    nav=page.locator('header .nav-icon-button').evaluate_all('(es)=>es.map(e=>getComputedStyle(e).backgroundColor)');assert all(c=='rgb(4, 5, 9)'for c in nav),nav
   page.click('#locationPickerOpen');rows=page.locator('#locationOptions button').evaluate_all('(es)=>es.slice(0,4).map(e=>getComputedStyle(e).backgroundColor)');assert all(c not in ['rgb(21, 61, 122)','rgb(26, 77, 145)']for c in rows),rows;page.keyboard.press('Escape')
   checks.append({'width':width,'switches':9,'checkboxes':2,'playback_only_blue':'PASS','neutral_other_controls':'PASS'})
  assert not errors,errors;b.close()
 (out/'checks.json').write_text(json.dumps({'result':'PASS','cases':checks,'test_run':True,'page_errors':errors},indent=2)+'\n');print('PASS: on/off controls blue in both distinguishable states, audio playback blue, other actions/fields/menus/nav remain glass, 6 pages/2 widths.')
finally:s.shutdown()
