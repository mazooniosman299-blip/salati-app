"""Chromium regression coverage for the compact instruments, menu, and navigation."""
import json
import functools
import threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
class QuietHandler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(QuietHandler,directory=str(root/'dist')))
threading.Thread(target=server.serve_forever,daemon=True).start()
(root/'reports/ui-modern').mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 page=b.new_page(viewport={'width':390,'height':844},device_scale_factor=1,service_workers='block')
 page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:24.7136,lon:46.6753,zone:'Asia/Riyadh',name:'الرياض',locationSet:true,locationMode:'manual',method:'Auto'}));")
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.route('**/__ui/*.js',lambda route:route.fulfill(path=str(root/route.request.url.split('/')[-1]),content_type='text/javascript'))
 page.goto(f'http://127.0.0.1:{server.server_port}',wait_until='domcontentloaded')
 page.add_script_tag(type='module',content="import {setupReminderIntervalPicker} from '/__ui/reminder-interval-picker.js';if(!document.getElementById('approachMinutesPickerOpen'))window.intervalPicker=setupReminderIntervalPicker(()=>document.documentElement.lang);")
 page.wait_for_selector('#approachMinutesPickerOpen',state='attached')
 for dark in [False,True]:
  page.click('[data-tab=mushaf]')
  page.evaluate('(dark)=>document.body.classList.toggle("dark",dark)',dark)
  for switch_id in ['qRepeat','qAutoNext']:
   switch=page.locator('#'+switch_id)
   for checked in [False,True]:
    switch.evaluate('(e,checked)=>e.checked=checked',checked)
    page.wait_for_timeout(200)
    style=switch.evaluate('(e)=>({after:getComputedStyle(e,"::after").content,before:getComputedStyle(e,"::before").content,track:getComputedStyle(e).backgroundColor,thumb:getComputedStyle(e,"::before").transform})')
    assert style['after']=='none',(switch_id,dark,checked,'duplicate thumb',style)
    assert style['before']=='""',(switch_id,dark,checked,'missing thumb',style)
    if checked:
     assert style['track']==('rgb(23, 62, 118)' if dark else 'rgb(21, 61, 120)'),(switch_id,dark,style)
     assert style['thumb']=='matrix(1, 0, 0, 1, 18, 0)',(switch_id,dark,style)
  page.screenshot(path=str(root/f'reports/ui-modern/quran-switches-{"dark" if dark else "light"}.png'))

  for tab in ['tasbih','qibla','settings']:
   page.click(f'[data-tab="{tab}"]')
   page.evaluate('(dark)=>document.body.classList.toggle("dark",dark)',dark)
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(dark,tab,'overflow')
   if tab=='tasbih':assert 44<=page.locator('#counter').bounding_box()['height']<=64
   assert page.locator('header .brand img').evaluate('(e)=>getComputedStyle(e).filter')=='none'
   page.mouse.move(0,0);page.wait_for_timeout(220)
   page.screenshot(path=str(root/f'reports/ui-modern/{tab}-{"dark" if dark else "light"}.png'),full_page=True)
  page.locator('#approachMinutesPickerOpen').scroll_into_view_if_needed();page.wait_for_timeout(100)
  page.click('#approachMinutesPickerOpen')
  assert page.locator('#approachMinutesOptions').is_visible()
  assert page.locator('#approachMinutesOptions [role=option]').count()==3
  page.screenshot(path=str(root/f'reports/ui-modern/reminder-menu-{"dark" if dark else "light"}.png'))
  page.locator('#approachMinutesOptions [data-value="15"]').click()
  assert page.locator('#approachMinutes').input_value()=='15'
  assert page.locator('#approachMinutesPickerOpen').get_attribute('aria-expanded')=='false'
  assert page.evaluate('document.activeElement.id')=='approachMinutesPickerOpen'
  page.click('#approachMinutesPickerOpen')
  page.keyboard.press('Home');page.keyboard.press('ArrowDown');page.keyboard.press('Enter')
  assert page.locator('#approachMinutes').input_value()=='10'
  assert page.evaluate('JSON.parse(localStorage.salati).audio.approachMinutes')==10
  page.click('#approachMinutesPickerOpen');page.keyboard.press('Escape')
  assert not page.locator('#approachMinutesOptions').is_visible()
 page.click('#lang');page.wait_for_timeout(100)
 assert 'minutes' in page.locator('#approachMinutesPickerOpen').inner_text()
 page.click('#lang');page.wait_for_timeout(100)
 page.click('[data-tab=tasbih]');page.click('#reset')
 for _ in range(34):page.click('#counter')
 assert page.locator('#tasbihCount').inner_text()=='34'
 assert page.locator('#tasbihProgress').get_attribute('aria-valuenow')=='34'
 assert page.evaluate('getComputedStyle(document.querySelector("#tasbihProgress")).backgroundImage').startswith('conic-gradient')
 page.click('#reset');assert page.locator('#tasbihCount').inner_text()=='0'
 for width in [320,390,600,760,1024,1440]:
  page.set_viewport_size({'width':width,'height':900})
  for tab in ['times','mushaf','qibla','dhikr','tasbih','settings']:
   page.click(f'[data-tab="{tab}"]')
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,tab,'overflow')
   assert page.locator('.nav-symbol').evaluate_all('(icons)=>icons.every(i=>i.getBoundingClientRect().width===24&&i.getBoundingClientRect().height===24)'),(width,tab,'icon')
 page.emulate_media(reduced_motion='reduce');page.click('[data-tab=tasbih]')
 assert page.locator('#counter').evaluate('(e)=>getComputedStyle(e).transitionDuration')=='0s'
 result={'result':'PASS','widths':[320,390,600,760,1024,1440],'tabs':6,'themes':2,'checks':['no horizontal overflow','24px icons','custom menu selection keyboard Escape focus','tasbih count/reset ring','single Quran switch thumb and dark blue checked track','reduced motion'],'pageErrors':errors}
 assert not errors,errors
 (root/'reports/ui-modern/verification.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
 b.close()
server.shutdown()
