#!/usr/bin/env python3
"""Current Salati Chromium instruments: retain navigation, contrast, switches,
Quran, voice choices, settings, tasbih, RTL/LTR, reduced-motion and responsive
regression coverage. Do NOT assert colors/overlays from retired stylesheets.
"""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
import json, re

root=Path(__file__).resolve().parents[1]
out=root/'reports/ui-modern'
out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args): pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')))
Thread(target=server.serve_forever,daemon=True).start()

def rgb(color):
 numbers=[int(n) for n in re.findall(r'\d+',color)[:3]]
 assert len(numbers)==3,('Invalid computed RGB',color)
 return numbers
def contrast(a,b):
 def lum(v):
  vals=[x/255 for x in rgb(v)]
  vals=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in vals]
  return sum(x*w for x,w in zip(vals,[.2126,.7152,.0722]))
 hi,lo=sorted([lum(a),lum(b)],reverse=True)
 return (hi+.05)/(lo+.05)

findings=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  for width,height in [(320,740),(360,780),(390,844),(412,915),(600,900),(760,960),(1024,850),(1440,900)]:
   page=browser.new_page(viewport={'width':width,'height':height},service_workers='block',reduced_motion='reduce')
   page.add_init_script("""localStorage.setItem('salati',JSON.stringify({
     lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',
     method:'Oman',name:'مسقط',locationSet:true,locationMode:'manual'
   }))""")
   errors=[]
   page.on('pageerror',lambda err:errors.append(str(err)))
   response=page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded',timeout=30000)
   assert response and response.ok and page.locator('body.dark').count()==1,(width,'dark boot')
   assert page.locator('link[rel=stylesheet]').evaluate_all('xs=>xs.map(x=>x.getAttribute("href"))')==['salati-ui.css'],(width,'canonical CSS')
   assert page.locator('#fajrAnnouncementToggle,#previewFajrPhrase').count()==0,(width,'retired controls')
   page.wait_for_function("document.querySelectorAll('#prayers .prayer').length===6",timeout=15000)
   assert contrast('rgb(255,255,255)','rgb(11,14,19)')>=15
   for tab in ('times','mushaf','qibla','dhikr','tasbih','settings'):
    selector=f'header>.site-nav button[data-tab="{tab}"]'
    page.locator(selector).click()
    page.wait_for_function("(tab)=>document.querySelector('header>.site-nav button.active')?.dataset.tab===tab",arg=tab)
    assert page.locator('header>.site-nav button.active').count()==1,(width,tab,'multiple selected tabs')
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(width,tab,'overflow')
    active=page.locator(selector)
    assert active.evaluate('e=>getComputedStyle(e).color')=='rgb(255, 255, 255)',(width,tab,'active label contrast')
    assert active.locator('.nav-symbol').evaluate('e=>getComputedStyle(e).color')=='rgb(255, 255, 255)',(width,tab,'icon not white')
    nav=page.locator('header>.site-nav').evaluate("""e=>{const r=e.getBoundingClientRect();return {
      left:r.left,right:r.right,bottom:r.bottom,position:getComputedStyle(e).position}}""")
    assert nav['left']>=-2 and nav['right']<=width+2,(width,tab,'clipped nav',nav)
    if width<=760:
     assert nav['position']=='fixed' and abs(nav['bottom']-height)<=2,(width,tab,'nav not anchored',nav)
    if tab=='mushaf':
     page.wait_for_selector('#qVerses .quran-reading-page',timeout=20000)
     assert page.locator('#mushafPlayerSlot').count()==1,(width,'player outside Quran')
     q=page.locator('#qVerses')
     state=q.evaluate("""e=>({height:e.clientHeight,scrollHeight:e.scrollHeight,
       overflow:getComputedStyle(e).overflowY,tabindex:e.getAttribute('tabindex')})""")
     assert state['height']>100 and state['scrollHeight']>=state['height'],(width,'reader clipped',state)
     assert state['overflow'] in ('auto','scroll') and state['tabindex']=='0',(width,'Quran not scrollable',state)
     assert q.locator('button[data-next],button[data-prev]').count()==0,(width,'retired next/prev pages')
     for sid in ('qRepeat','qAutoNext'):
      control=page.locator('#'+sid)
      assert control.count()==1,(width,'missing Quran switch',sid)
      appearances=[]
      for checked in (False,True):
       control.evaluate("""(e,value)=>{e.checked=value}""",checked)
       appearances.append(control.evaluate("""e=>({bg:getComputedStyle(e).backgroundColor,
          thumb:getComputedStyle(e,'::before').transform,duplicate:getComputedStyle(e,'::after').content})"""))
      assert appearances[0]['thumb']!=appearances[1]['thumb'],(width,sid,'switch stuck',appearances)
      assert all(t['duplicate']=='none' for t in appearances),(width,sid,'duplicate switch thumb')
     if width==390:
      q.hover()
      for _ in range(10):
       page.mouse.wheel(0,750)
       page.wait_for_timeout(100)
      page.wait_for_function("document.querySelectorAll('#qVerses .quran-reading-page').length>=2",timeout=10000)
    if tab=='tasbih':
     counter=page.locator('#counter')
     assert counter.count()==1 and counter.is_visible(),(width,'counter absent')
    if tab=='dhikr':
     page.wait_for_selector('.adhkar-card',timeout=12000)
     assert page.locator('.adhkar-card').count()>=1,(width,'adhkar missing')
    if tab=='settings':
     assert page.locator('#voicePickerOpen').count()==1,(width,'voice select missing')
    if width in (390,1440):
     page.screenshot(path=str(out/f'{tab}-{width}.png'),full_page=False)
   page.locator('header>.site-nav button[data-tab="tasbih"]').click()
   counter=page.locator('#counter')
   reset=page.locator('#reset')
   reset.click()
   for _ in range(3):counter.click()
   assert page.locator('#tasbihCount').inner_text().strip()=='3',(width,'tasbih count malfunction')
   reset.click()
   assert page.locator('#tasbihCount').inner_text().strip()=='0',(width,'tasbih reset malfunction')
   if width==390:
    page.locator('header>.site-nav button[data-tab="settings"]').click()
    page.click('#voicePickerOpen')
    voices=page.locator('#voicePickerList .voice-check')
    assert voices.count()==4,(width,'muezzin options lost')
    assert page.locator('#voicePickerList [aria-pressed="true"]').count()==1,(width,'voice choice not unique')
    page.click('#voicePickerClose')
    original=page.locator('html').get_attribute('dir')
    page.click('#lang')
    assert page.locator('html').get_attribute('dir')!=original,'RTL/LTR language switch failed'
    page.click('#lang')
    assert page.locator('html').get_attribute('dir')==original,'RTL/LTR restore failed'
    page.emulate_media(reduced_motion='reduce')
    assert page.locator('#counter').evaluate("e=>getComputedStyle(e).transitionDuration")=='0s','Reduced-motion safeguard missing'
   assert not errors,(width,'JavaScript errors',errors[:5])
   findings.append({'viewport':[width,height],'tabs':6,'js_errors':0,'quran_switches':2,'tasbih':'pass'})
   page.close()
  browser.close()
finally:
 server.shutdown()
(out/'verification.json').write_text(json.dumps({'status':'PASS','findings':findings},indent=2)+'\n')
print('PASS modern live UI: dark-only, Quran scroll/switches, voice selection, contrast, tasbih, RTL/LTR, 8 viewports x 6 tabs')
