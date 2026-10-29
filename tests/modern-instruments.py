"""Chromium regression coverage for the compact instruments, menu, and navigation."""
import json
import re
import functools
import threading
import subprocess
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
class QuietHandler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(QuietHandler,directory=str(root/'dist')))
threading.Thread(target=server.serve_forever,daemon=True).start()
(root/'reports/ui-modern').mkdir(parents=True,exist_ok=True)
def contrast(foreground,background):
 def luminance(color):
  values=[int(v)/255 for v in re.findall(r"\d+",color)[:3]]
  linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in values]
  return sum(v*w for v,w in zip(linear,[.2126,.7152,.0722]))
 first,second=sorted([luminance(foreground),luminance(background)])
 return (second+.05)/(first+.05)
def neutral(color):
 channels=[int(v) for v in re.findall(r"\d+",color)[:3]]
 return max(channels)-min(channels)<=2
motion_module=subprocess.run(['node','-e',"process.stdout.write(require('esbuild').buildSync({entryPoints:['glass-navigation.js'],bundle:true,write:false,format:'esm',platform:'browser'}).outputFiles[0].text)"],cwd=root,check=True,capture_output=True,text=True).stdout
palette_evidence=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 page=b.new_page(viewport={'width':390,'height':844},device_scale_factor=1,service_workers='block')
 page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:24.7136,lon:46.6753,zone:'Asia/Riyadh',name:'الرياض',locationSet:true,locationMode:'manual',method:'Auto'}));")
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.route('**/__ui/*.js',lambda route:route.fulfill(body=motion_module,content_type='text/javascript') if route.request.url.endswith('/glass-navigation.js') else route.fulfill(path=str(root/route.request.url.split('/')[-1]),content_type='text/javascript'))
 page.goto(f'http://127.0.0.1:{server.server_port}',wait_until='domcontentloaded')
 page.add_script_tag(type='module',content="import {setupReminderIntervalPicker} from '/__ui/reminder-interval-picker.js';if(!document.getElementById('approachMinutesPickerOpen'))window.intervalPicker=setupReminderIntervalPicker(()=>document.documentElement.lang);")
 page.wait_for_selector('#approachMinutesPickerOpen',state='attached')
 page.add_script_tag(type='module',content="import {setupGlassNavigation} from '/__ui/glass-navigation.js';document.querySelector('.nav-selection')?.remove();document.querySelector('.site-nav').classList.remove('has-glass-navigation');setupGlassNavigation();")
 page.wait_for_selector('.nav-selection',state='attached')
 marker=page.locator('.nav-selection');start=marker.bounding_box()['x']
 page.click('[data-tab=settings]');page.wait_for_timeout(50)
 middle=marker.bounding_box()['x'];target=page.locator('[data-tab=settings]').bounding_box()['x']
 assert min(start,target)<middle<max(start,target),(start,middle,target,'Motion should interpolate the glass selection')
 page.wait_for_timeout(300)

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
     assert style['track']==('rgb(68, 68, 68)' if dark else 'rgb(48, 48, 48)'),(switch_id,dark,style)
     assert style['thumb']=='matrix(1, 0, 0, 1, 18, 0)',(switch_id,dark,style)
     assert contrast('rgb(255, 255, 255)',style['track'])>=4.5
  page.screenshot(path=str(root/f'reports/ui-modern/quran-switches-{"dark" if dark else "light"}.png'))

  for tab in ['times','mushaf','tasbih','qibla','settings']:
   page.click(f'[data-tab="{tab}"]')
   page.evaluate('(dark)=>document.body.classList.toggle("dark",dark)',dark)
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(dark,tab,'overflow')
   if tab=='tasbih':assert 44<=page.locator('#counter').bounding_box()['height']<=56
   assert page.locator('header .brand img').evaluate('(e)=>getComputedStyle(e).filter')=='none'
   page.mouse.move(0,0);page.wait_for_timeout(320)
   fill='rgb(68, 68, 68)' if dark else 'rgb(48, 48, 48)'
   ink='rgb(255, 255, 255)' if dark else 'rgb(0, 0, 0)'
   active=page.locator('header>.site-nav .active').evaluate('(e)=>({bg:getComputedStyle(e).backgroundColor,color:getComputedStyle(e).color})')
   assert active['color']==ink,(dark,tab,active)
   marker=page.locator('.nav-selection')
   assert marker.count()==1
   assert neutral(marker.evaluate('(e)=>getComputedStyle(e).backgroundColor'))
   marker_box=marker.bounding_box();active_box=page.locator('header>.site-nav .active').bounding_box()
   assert all(abs(marker_box[key]-active_box[key])<1.5 for key in ['x','y','width','height']),(dark,tab,marker_box,active_box)
   inactive=page.locator('header>.site-nav button:not(.active)').first
   assert inactive.evaluate('(e)=>getComputedStyle(e).color')==ink
   assert page.locator('#countdown').evaluate('(e)=>getComputedStyle(e).color')==ink
   for selector in ['.primary:not(:disabled)','#counter:not(:disabled)','#mushaf #qTransport:not(:disabled)']:
    for style in page.locator(selector).evaluate_all('(es)=>es.map(e=>({id:e.id,color:getComputedStyle(e).color,bg:getComputedStyle(e).backgroundColor}))'):
     assert style['bg']==fill and style['color']=='rgb(255, 255, 255)',(dark,tab,style)
     assert contrast(style['color'],style['bg'])>=4.5,(dark,style)
   if tab=='tasbih':
    button=page.locator('#counter')
    page.keyboard.press('Tab');button.focus()
    focus=button.evaluate('(e)=>({color:getComputedStyle(e).outlineColor,width:getComputedStyle(e).outlineWidth,visible:e.matches(":focus-visible")})')
    assert focus['visible'] and focus['width']=='3px',(dark,focus)
    assert contrast(focus['color'],'rgb(37, 37, 37)' if dark else 'rgb(255, 255, 255)')>=3,(dark,focus)
    button.evaluate('(e)=>e.disabled=true');page.wait_for_timeout(200)
    disabled=button.evaluate('(e)=>({bg:getComputedStyle(e).backgroundColor,color:getComputedStyle(e).color,opacity:getComputedStyle(e).opacity})')
    assert disabled['opacity']=='1' and disabled['bg']!=fill,(dark,disabled)
    assert contrast(disabled['color'],disabled['bg'])>=4.5,(dark,disabled)
    button.evaluate('(e)=>e.disabled=false');button.blur()
    palette_evidence.append({'dark':dark,'controlFill':fill,'whiteTextContrast':round(contrast('rgb(255, 255, 255)',fill),2),'focus':focus,'disabled':disabled})
   page.mouse.move(0,0);page.wait_for_timeout(220)
   page.screenshot(path=str(root/f'reports/ui-modern/{tab}-{"dark" if dark else "light"}.png'),full_page=True)
  page.locator('#approachMinutesPickerOpen').scroll_into_view_if_needed();page.wait_for_timeout(100)
  page.click('#approachMinutesPickerOpen')
  assert page.locator('#approachMinutesOptions').is_visible()
  assert page.locator('#approachMinutesOptions [role=option]').count()==3
  selected=page.locator('#approachMinutesOptions [aria-selected=true]').evaluate('(e)=>({bg:getComputedStyle(e).backgroundColor,color:getComputedStyle(e).color})')
  assert selected=={'bg':fill,'color':'rgb(255, 255, 255)'},(dark,selected)
  assert contrast(selected['color'],selected['bg'])>=4.5
  for style in page.locator('#approachMinutesOptions [aria-selected=false]').evaluate_all('(es)=>es.map(e=>({color:getComputedStyle(e).color}))'):
   assert style['color']==ink,(dark,style)
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
 active_tab=page.locator('header>.site-nav .active').get_attribute('data-tab')
 for expected_direction in ['ltr','rtl']:
  page.click('#lang');page.wait_for_timeout(100)
  assert page.locator('html').get_attribute('dir')==expected_direction
  assert page.locator('header>.site-nav .active').get_attribute('data-tab')==active_tab
  marker_box=page.locator('.nav-selection').bounding_box();active_box=page.locator('header>.site-nav .active').bounding_box()
  assert all(abs(marker_box[key]-active_box[key])<1.5 for key in ['x','y','width','height']),(expected_direction,marker_box,active_box,'Language switch must realign the same active tab')
  if expected_direction=='ltr':assert 'minutes' in page.locator('#approachMinutesPickerOpen').inner_text()
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
 page.click('[data-tab=mushaf]')
 for selector in ['.mushaf-verses','.quran-text']:
  for styles in page.locator(selector).evaluate_all('(es)=>es.map(e=>({filter:getComputedStyle(e).filter,backdrop:getComputedStyle(e).backdropFilter}))'):
   assert styles=={'filter':'none','backdrop':'none'},styles
 for selector in ['#qTransport','#qSmaller','#qLarger']:
  assert page.locator(selector).bounding_box()['height']==44,selector
 cdp=page.context.new_cdp_session(page)
 cdp.send('Emulation.setEmulatedMedia',{'features':[{'name':'prefers-reduced-transparency','value':'reduce'}]})
 assert page.locator('.mushaf-toolbar').evaluate('(e)=>getComputedStyle(e).backdropFilter')=='none'
 assert page.locator('.mushaf-toolbar').evaluate('(e)=>getComputedStyle(e).backgroundColor').startswith('rgb(')
 cdp.send('Emulation.setEmulatedMedia',{'features':[]})
 page.emulate_media(reduced_motion='reduce');page.click('[data-tab=tasbih]')
 assert page.locator('#counter').evaluate('(e)=>getComputedStyle(e).transitionDuration')=='0s'
 marker_box=page.locator('.nav-selection').bounding_box();active_box=page.locator('[data-tab=tasbih]').bounding_box()
 assert all(abs(marker_box[key]-active_box[key])<1.5 for key in ['x','y','width','height']),(marker_box,active_box,'Reduced motion snaps the selection')
 result={'result':'PASS','widths':[320,390,600,760,1024,1440],'tabs':6,'themes':2,'checks':['no horizontal overflow','24px icons','custom menu selection keyboard Escape focus','tasbih count/reset ring','single Quran switch thumb and neutral checked track','Motion sliding glass navigation','same-tab RTL/LTR language realignment','white labels with >=4.5:1 contrast','disabled and focused controls','black/white timer and unselected labels','reduced motion and transparency','crisp Quran text and compact controls'],'pageErrors':errors,'palette':palette_evidence}
 assert not errors,errors
 (root/'reports/ui-modern/verification.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
 b.close()
server.shutdown()
