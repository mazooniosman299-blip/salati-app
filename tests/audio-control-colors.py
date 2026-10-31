"""Screenshot acceptance: blue enabled switches and Quran audio, neutral non-action controls."""
from pathlib import Path
from functools import partial
from threading import Thread
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
import json

root = Path(__file__).resolve().parents[1]
out = root / 'reports' / 'audio-controls-2026-10-31'
out.mkdir(parents=True, exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a): pass
s = ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')))
Thread(target=s.serve_forever,daemon=True).start()
checks=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  page=browser.new_page(service_workers='block')
  errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual'}))")
  page.goto(f'http://127.0.0.1:{s.server_port}/',wait_until='domcontentloaded')
  for width in [390,1440]:
   page.set_viewport_size({'width':width,'height':1000})
   assert page.locator('body').evaluate('(e)=>getComputedStyle(e).backgroundColor')=='rgb(11, 14, 19)'
   page.click('[data-tab=settings]')
   switches=page.locator('[data-audio-prayer],#fajrAnnouncementToggle,#audioEnable,#duaToggle,#silentAdhanToggle')
   assert switches.count()==9
   for switch in switches.all():
    original=switch.evaluate('(e)=>e instanceof HTMLInputElement?e.checked:e.getAttribute("aria-checked")==="true"')
    for enabled,color in [(False,'rgb(21, 24, 29)'),(True,'rgb(35, 104, 196)')]:
     switch.evaluate('(e,v)=>{if(e instanceof HTMLInputElement)e.checked=v;else{e.setAttribute("aria-checked",String(v));e.classList.toggle("is-on",v);}}',enabled)
     page.wait_for_timeout(100)
     actual=switch.evaluate('(e)=>getComputedStyle(e).backgroundColor')
     if actual!=color:
      detail=switch.evaluate('(e)=>({tag:e.outerHTML.slice(0,210),parent:e.parentElement?.parentElement?.className,body:document.body.className,inline:e.getAttribute("style")})')
      raise AssertionError((width,switch.get_attribute('id'),switch.get_attribute('data-audio-prayer'),enabled,actual,detail))
    switch.evaluate('(e,v)=>{if(e instanceof HTMLInputElement)e.checked=v;else{e.setAttribute("aria-checked",String(v));e.classList.toggle("is-on",v);}}',original)
   for key in ['previewFajrPhrase','previewAdhan','previewDua','audioStop','resetPrayerAdjustments','applyPrayerAdjustments','cancelPrayerAdjustments','locationPickerOpen','methodPickerOpen']:
    actual=page.locator('#'+key).evaluate('(e)=>getComputedStyle(e).backgroundColor')
    assert actual not in ['rgb(35, 104, 196)','rgb(47, 121, 218)'],(width,key,actual)
   page.locator('#previewFajrPhrase').scroll_into_view_if_needed()
   page.screenshot(path=str(out/f'settings-{width}.png'))
   page.click('[data-tab=mushaf]')
   page.wait_for_function('document.querySelector("#qSurah").options.length>=114')
   assert page.locator('#qTransport').evaluate('(e)=>getComputedStyle(e,"::before").backgroundColor')=='rgb(35, 104, 196)'
   stop=page.locator('#qStop')
   assert not stop.is_visible(),'Idle stop control must be hidden'
   stop.evaluate('(e)=>e.disabled=false')
   assert stop.evaluate('(e)=>getComputedStyle(e).backgroundColor')=='rgb(35, 104, 196)'
   stop.evaluate('(e)=>e.disabled=true')
   for key in ['qRepeat','qAutoNext']:
    el=page.locator('#'+key)
    for enabled,color in [(False,'rgb(21, 24, 29)'),(True,'rgb(35, 104, 196)')]:
     el.evaluate('(e,v)=>e.checked=v',enabled)
     actual=el.evaluate('(e)=>getComputedStyle(e).backgroundColor')
     assert actual==color,(width,key,enabled,actual)
   assert page.locator('.mushaf-emblem').evaluate('(e)=>getComputedStyle(e).opacity')=='1'
   page.locator('.reference-player').screenshot(path=str(out/f'player-{width}.png'))
   for tab in ['times','mushaf','dhikr','qibla','tasbih','settings']:
    page.click(f'[data-tab={tab}]')
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,tab)
    nav=page.locator('header>.site-nav .nav-icon-button').evaluate_all('(es)=>es.map(e=>getComputedStyle(e).backgroundColor)')
    assert all(c not in ['rgb(35, 104, 196)','rgb(47, 121, 218)'] for c in nav),nav
   checks.append({'width':width,'switches':9,'checkboxes':2,'blue_only_for_on_switches_and_audio':True,'horizontal_overflow':False})
  assert not errors,errors
  browser.close()
 (out/'checks.json').write_text(json.dumps({'result':'PASS','cases':checks,'physical_device_tested':False},indent=2)+'\n')
 print('PASS: screenshot charcoal, blue ON switches and Quran transport, neutral settings, 6 tabs, 2 widths.')
finally:
 s.shutdown()
