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
palette_evidence=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 page=b.new_page(viewport={'width':390,'height':844},device_scale_factor=1,service_workers='block')
 page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:24.7136,lon:46.6753,zone:'Asia/Riyadh',name:'الرياض',locationSet:true,locationMode:'manual',method:'Auto'}));")
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(f'http://127.0.0.1:{server.server_port}',wait_until='domcontentloaded')
 page.wait_for_selector('#fajrAnnouncementToggle',state='attached')
 page.wait_for_selector('.nav-selection',state='visible')
 marker=page.locator('.nav-selection');start=marker.bounding_box()['x']
 page.click('[data-tab=settings]');page.wait_for_timeout(50)
 middle=marker.bounding_box()['x'];target=page.locator('[data-tab=settings]').bounding_box()['x']
 assert min(start,target)<middle<max(start,target),(start,middle,target,'Motion should interpolate the glass selection')
 page.wait_for_timeout(300)

 for dark in [True]:
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
     assert style['track']=='rgb(21, 24, 29)',(switch_id,dark,style)
     assert abs(float(style['thumb'].split(',')[-2])-18)<.2,(switch_id,dark,style)
     assert contrast('rgb(255, 255, 255)',style['track'])>=4.5
  page.wait_for_function('document.querySelector("#qVerses [data-ayah] .ayah-number")!==null')
  verse=page.locator('#qVerses [data-ayah]').first
  verse.evaluate('(e)=>e.classList.add("is-reciting")')
  badge=verse.locator('.ayah-number').evaluate('(e)=>({color:getComputedStyle(e).color,bg:getComputedStyle(e).backgroundColor})')
  assert contrast(badge['color'],badge['bg'])>=4.5,(dark,'active verse number',badge)
  verse.evaluate('(e)=>e.classList.remove("is-reciting")')
  page.screenshot(path=str(root/f'reports/ui-modern/quran-switches-{"dark" if dark else "light"}.png'))

  for tab in ['times','mushaf','tasbih','qibla','dhikr','settings']:
   page.click(f'[data-tab="{tab}"]')
   page.evaluate('(dark)=>document.body.classList.toggle("dark",dark)',dark)
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(dark,tab,'overflow')
   if tab=='tasbih':
    assert 44<=page.locator('#counter').bounding_box()['height']<=56
    panel=page.locator('.tasbih-panel').evaluate('(e)=>({bg:getComputedStyle(e).backgroundColor,border:getComputedStyle(e).borderTopWidth,padding:getComputedStyle(e).padding})')
    assert panel=={'bg':'rgba(0, 0, 0, 0)','border':'0px','padding':'0px'},(dark,'duplicate tasbih panel',panel)
   if tab=='dhikr':
    shell=page.locator('.adhkar-library').evaluate('(e)=>({bg:getComputedStyle(e).backgroundColor,border:getComputedStyle(e).borderTopWidth,blur:getComputedStyle(e).backdropFilter})')
    assert shell=={'bg':'rgba(0, 0, 0, 0)','border':'0px','blur':'none'},(dark,'duplicate adhkar shell',shell)

   assert page.locator('header .brand img').evaluate('(e)=>getComputedStyle(e).filter')=='none'
   page.mouse.move(0,0);page.wait_for_timeout(320)
   fill=page.evaluate('()=>{const e=document.createElement("span");e.style.color="var(--control-fill)";document.body.append(e);const color=getComputedStyle(e).color;e.remove();return color}')
   ink='rgb(255, 255, 255)' if dark else 'rgb(0, 0, 0)'
   active=page.locator('header>.site-nav .active').evaluate('(e)=>({bg:getComputedStyle(e).backgroundColor,color:getComputedStyle(e).color})')
   assert active['color']=='rgb(255, 255, 255)',(dark,tab,active)
   marker=page.locator('.nav-selection')
   assert marker.count()==1
   assert marker.evaluate('(e)=>getComputedStyle(e).backgroundColor')=='rgba(255, 255, 255, 0.035)','reference selection must be neutral glass, never gold'
   marker_box=marker.bounding_box();active_box=page.locator('header>.site-nav .active').bounding_box()
   assert abs(marker_box['width']-(active_box['width']-8))<1.5 and abs(marker_box['height']-(active_box['height']-8))<1.5 and abs(marker_box['x']-(active_box['x']+4))<1.5 and abs(marker_box['y']-(active_box['y']+4))<1.5,(dark,tab,marker_box,active_box)
   inactive=page.locator('header>.site-nav button:not(.active)').first
   assert inactive.evaluate('(e)=>getComputedStyle(e).color')==ink
   assert page.locator('#countdown').evaluate('(e)=>getComputedStyle(e).color')==ink
   for selector in ['.primary:not(:disabled)','#counter:not(:disabled)','#mushaf #qTransport:not(:disabled)']:
    for style in page.locator(selector).evaluate_all('(es)=>es.map(e=>({id:e.id,cls:e.className,tag:e.outerHTML.slice(0,170),color:getComputedStyle(e).color,bg:getComputedStyle(e,e.id==="qTransport"?"::before":undefined).backgroundColor}))'):
     action_fill=page.evaluate('getComputedStyle(document.body).getPropertyValue("--action-fill").trim()');expected='rgb(11, 14, 19)' if style['id']=='qTransport' else ('rgb(21, 24, 29)' if style['id']=='qPlay' else ('rgb(21, 24, 29)' if style['id']=='compassEnable' else fill))
     assert style['bg']==expected and style['color']=='rgb(255, 255, 255)',(dark,tab,style)
     assert contrast(style['color'],style['bg'])>=4.5,(dark,style)
   if tab=='tasbih':
    button=page.locator('#counter')
    page.keyboard.press('Tab');button.focus()
    focus=button.evaluate('(e)=>({color:getComputedStyle(e).borderTopColor,width:getComputedStyle(e).outlineWidth,visible:e.matches(":focus-visible")})')
    assert focus['visible'] and focus['width']=='0px',(dark,focus)
    assert contrast(focus['color'],'rgb(21, 24, 29)')>=3,(dark,focus)
    button.evaluate('(e)=>e.disabled=true');page.wait_for_timeout(200)
    disabled=button.evaluate('(e)=>({bg:getComputedStyle(e).backgroundColor,color:getComputedStyle(e).color,opacity:getComputedStyle(e).opacity})')
    assert disabled['opacity']=='1' and disabled['color']==ink,(dark,disabled)
    assert contrast(disabled['color'],disabled['bg'])>=4.5,(dark,disabled)
    button.evaluate('(e)=>e.disabled=false');button.blur()
    palette_evidence.append({'dark':dark,'controlFill':fill,'whiteTextContrast':round(contrast('rgb(255, 255, 255)',fill),2),'focus':focus,'disabled':disabled})
   page.mouse.move(0,0);page.wait_for_timeout(220)
   page.screenshot(path=str(root/f'reports/ui-modern/{tab}-{"dark" if dark else "light"}.png'))
  for selector in ['.announcement-settings','.prayer-switches','.minute-adjustments']:
   style=page.locator(selector).evaluate('(e)=>({bg:getComputedStyle(e).backgroundColor,blur:getComputedStyle(e).backdropFilter,shadow:getComputedStyle(e).boxShadow})')
   assert style=={'bg':'rgba(0, 0, 0, 0)','blur':'none','shadow':'none'},(dark,selector,'nested panel',style)
  page.locator('.announcement-settings').scroll_into_view_if_needed();page.wait_for_timeout(100)
  page.screenshot(path=str(root/f'reports/ui-modern/reminder-settings-{"dark" if dark else "light"}.png'))
  for selector in ['#audioEnable','#duaToggle','#silentAdhanToggle']:
   box=page.locator(selector).bounding_box()
   assert box is None or box['height']==38,(dark,selector,'stretched switch',box)
  for selector in ['#previewFajrPhrase','#previewAdhan','#previewDua','#audioStop']:
   style=page.locator(selector).evaluate('(e)=>({bg:getComputedStyle(e).backgroundColor,color:getComputedStyle(e).color,border:getComputedStyle(e).borderColor})')
   assert contrast(style['color'],style['bg'])>=4.5,(dark,selector,style)
  assert page.locator('#approachToggle,#approachMinutes,#previewApproach').count()==0
  toggle=page.locator('#fajrAnnouncementToggle');toggle.check();toggle.uncheck()
  assert page.evaluate('JSON.parse(localStorage.salati).audio.fajrAnnouncement')is False
  toggle.check();assert page.evaluate('JSON.parse(localStorage.salati).audio.fajrAnnouncement')is True
 active_tab=page.locator('header>.site-nav .active').get_attribute('data-tab')
 for expected_direction in ['ltr','rtl']:
  page.click('#lang');page.wait_for_timeout(100)
  assert page.locator('html').get_attribute('dir')==expected_direction
  assert page.locator('header>.site-nav .active').get_attribute('data-tab')==active_tab
  marker_box=page.locator('.nav-selection').bounding_box();active_box=page.locator('header>.site-nav .active').bounding_box()
  assert abs(marker_box['width']-(active_box['width']-8))<1.5 and abs(marker_box['height']-(active_box['height']-8))<1.5 and abs(marker_box['x']-(active_box['x']+4))<1.5 and abs(marker_box['y']-(active_box['y']+4))<1.5,(expected_direction,marker_box,active_box,'Language switch must realign the same active tab')
  if expected_direction=='ltr':assert 'Fajr' in page.locator('#previewFajrPhrase').inner_text()
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
   assert page.locator('header>.site-nav .nav-symbol').evaluate_all("""(icons)=>icons.every(i=>{const s=getComputedStyle(i),r=i.getBoundingClientRect();return s.width==='24px'&&s.height==='24px'&&Math.abs(r.width-24)<1&&Math.abs(r.height-24)<1})"""),(width,tab,'icon sizing must remain 24px')
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
 assert abs(marker_box['width']-(active_box['width']-8))<1.5 and abs(marker_box['height']-(active_box['height']-8))<1.5 and abs(marker_box['x']-(active_box['x']+4))<1.5 and abs(marker_box['y']-(active_box['y']+4))<1.5,(marker_box,active_box,'Reduced motion snaps the selection')
 result={'result':'PASS','widths':[320,390,600,760,1024,1440],'tabs':6,'themes':1,'checks':['no horizontal overflow','24px icons','custom menu selection keyboard Escape focus','tasbih count/reset ring','single Quran switch thumb and high-contrast checked track','Motion sliding glass navigation','same-tab RTL/LTR language realignment','control labels with >=4.5:1 contrast','disabled and focused controls','black/white timer and unselected labels','reduced motion and transparency','crisp Quran text and compact controls'],'pageErrors':errors,'palette':palette_evidence}
 assert not errors,errors
 (root/'reports/ui-modern/verification.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
 b.close()
server.shutdown()
