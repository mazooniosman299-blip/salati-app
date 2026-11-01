"""Acceptance: no bottom-nav collision at short handset heights, no saved offsets lost.
Tests the built app with real Chromium and a real legacy localStorage upgrade.
"""
import json
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
out=root/'reports/upgrade-mobile-20261101';out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')))
Thread(target=server.serve_forever,daemon=True).start()
cases=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for width,height in [(360,740),(390,844),(390,667),(412,915)]:
   page=browser.new_page(viewport={'width':width,'height':height},service_workers='block')
   saved={
    'lat':23.588,'lon':58.3829,'zone':'Asia/Muscat','name':'مسقط',
    'locationSet':True,'locationMode':'manual','method':'Auto',
    'methodPreferenceVersion':1,'prayerPreferenceVersion':1,
    'muscatCalibrationVersion':3,'madhab':'Shafi',
    'adjustments':{'fajr':2,'sunrise':-1,'dhuhr':0,'asr':3,'maghrib':-2,'isha':1}
   }
   page.add_init_script(f"localStorage.setItem('salati',JSON.stringify({json.dumps(saved,ensure_ascii=False)}))")
   errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   response=page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
   assert response and response.ok
   state=json.loads(page.evaluate("localStorage.getItem('salati')"))
   assert state['adjustments']==saved['adjustments'],(width,height,'lost old saved prayer corrections',state['adjustments'])
   assert state['muscatCalibrationVersion']==4
   assert state['adjustmentMode']=='manual'
   assert state['prayerPreferenceVersion']==2

   def visible_above_nav(selector):
    rect=page.locator(selector).evaluate("""e=>{
      const r=e.getBoundingClientRect(),n=document.querySelector('header>.site-nav').getBoundingClientRect();
      return {control:[r.top,r.bottom],nav:[n.top,n.bottom],scrollY:scrollY,
        pageHeight:document.documentElement.scrollHeight,viewport:innerHeight};
    }""")
    assert rect['control'][1]<=rect['nav'][0]-8,(width,height,selector,'overlapped bottom navigation',rect)
    assert rect['control'][0]>=0,(width,height,selector,'scrolled control off-screen',rect)
    return rect

   page.click('[data-tab=qibla]')
   page.wait_for_timeout(170)
   qibla=visible_above_nav('#compassEnable')
   page.locator('#compassEnable').screenshot(path=str(out/f'qibla-action-{width}x{height}.png'))
   page.click('[data-tab=mushaf]')
   page.wait_for_timeout(250)
   surah=visible_above_nav('#mushaf .quran-play-options label:last-child')
   page.locator('#mushaf .quran-play-options').screenshot(path=str(out/f'quran-actions-{width}x{height}.png'))
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,height,'horizontal scrolling')
   assert not errors,(width,height,'browser JS errors',errors)
   cases.append({'width':width,'height':height,'qibla':qibla,'quran':surah,'offsets_preserved':True,'js_errors':0})
   page.close()
  browser.close()
 (out/'results.json').write_text(json.dumps({'passed':True,'cases':cases},ensure_ascii=False,indent=2)+'\n')
 print('PASS: mobile nav avoids Quran and Qibla controls, legacy stored adjustments remain unchanged',len(cases),'handsets')
finally:
 server.shutdown()
