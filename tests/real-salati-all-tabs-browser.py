#!/usr/bin/env python3
"""ALL SIX actual Salati tabs, real Chromium captures, NO GENERATIVE IMAGES.
Works on real repository build; optional signed-source original Quran screenshot.
No publication or APK modification.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
output=root/'reports/complete-salati-app'
output.mkdir(parents=True,exist_ok=True)
tabs=[('times','المواقيت'),('qibla','القبلة'),('dhikr','الأذكار'),
      ('tasbih','المسبحة'),('settings','الإعدادات'),('mushaf','المصحف')]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')))
Thread(target=server.serve_forever,daemon=True).start()

def initialize(page):
 page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual'}))")

def screenshot_tabs(browser,width,height):
 page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1,service_workers='block')
 initialize(page)
 errors=[]
 page.on('pageerror',lambda exc:errors.append(str(exc)))
 origin=f'http://127.0.0.1:{server.server_port}/'
 r=page.goto(origin,wait_until='domcontentloaded')
 assert r and r.ok,(width,'Salati did not load')
 page.wait_for_function("() => document.querySelector('header>.site-nav button[data-tab=\"times\"]')!==null")
 for tab,label in tabs:
  button=page.locator(f'header>.site-nav button[data-tab="{tab}"]')
  button.click()
  page.wait_for_function("(id) => {const tab=document.getElementById(id);return tab&&!tab.hidden}",arg=tab)
  if tab=='mushaf':
   page.wait_for_function("() => !!document.querySelector('#qVerses [data-ayah]')",timeout=30000)
  page.wait_for_timeout(350)
  metadata=page.evaluate("""() => {
   const section=[...document.querySelectorAll('main section.tab')].find(x=>!x.hidden);
   const body=getComputedStyle(document.body);
   return {visible:section?.id, bg:body.backgroundColor,
     dark:document.body.classList.contains('dark'),
     heading:section?.querySelector('h2')?.textContent?.trim().slice(0,80),
     scrollWidth:document.documentElement.scrollWidth,
     viewport:innerWidth};
  }""")
  assert metadata['visible']==tab,(width,tab,'wrong displayed tab',metadata)
  assert metadata['dark'],(width,tab,'accidental light mode')
  assert metadata['scrollWidth'] <= width + 2,(width,tab,'horizontal overflow',metadata)
  file=output/f'ACTUAL-SALATI-{tab.upper()}-{width}-TOP.png'
  page.screenshot(path=str(file),full_page=False)
  # Additional view of scrollable pages (settings/dhikr) verifies lower content.
  if tab in ('settings','dhikr','times'):
   page.mouse.move(width//2,height//2)
   page.mouse.wheel(0,1600)
   page.wait_for_timeout(400)
   page.screenshot(path=str(output/f'ACTUAL-SALATI-{tab.upper()}-{width}-SCROLLED.png'),full_page=False)
   page.mouse.wheel(0,-1900)
   page.wait_for_timeout(200)
  if tab=='mushaf':
   header=page.locator('#qApprovedReadingHeader')
   assert header.is_visible()
   for id in ['qApprovedReaderMenu','qApprovedSettings']:
    use=page.locator(f'#{id} svg use')
    assert use.get_attribute('href')=='icons/navigation.svg#settings',(width,id,'not the ORIGINAL app icon')
   colors=page.evaluate("""() => {
    const r=document.getElementById('qApprovedReadingHeader');
    const label=r.querySelector('label'),select=r.querySelector('select');
    return {header:getComputedStyle(r).backgroundColor,
     label:getComputedStyle(label).backgroundColor,
     text:getComputedStyle(select).color,
     player:getComputedStyle(document.getElementById('mushafPlayerSlot')).backgroundColor}
   }""")
   assert colors['header']=='rgb(24, 25, 29)',(width,'old grey top bar remains',colors)
   assert colors['label']=='rgb(34, 36, 42)',(width,'old grey selector remains',colors)
   assert colors['text']=='rgb(255, 255, 255)',(width,'surah and juz text should be white',colors)
   assert colors['player']=='rgb(24, 25, 29)',(width,'player changed from original charcoal',colors)
   assert page.locator('#qApprovedReaderBack').is_visible()
   page.locator('#qApprovedReaderMenu').click()
   assert page.locator('#qReciter').is_visible(),(width,'true gear did not open player settings')
   page.screenshot(path=str(output/f'ACTUAL-SALATI-MUSHAF-{width}-SETTINGS.png'),full_page=False)
   page.locator('#qApprovedReaderMenu').click()
   assert not page.locator('#qReciter').is_visible()
 assert not errors,(width,'JavaScript runtime errors',errors)
 page.close()

def screenshot_original_full_page(browser,width,height):
 if not (root/'dist/quran-green-proof/manifest.json').exists():
  raise AssertionError('STOP: cannot call screenshot genuine mushaf without verified publisher image files')
 page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1,service_workers='block')
 initialize(page)
 url=f'http://127.0.0.1:{server.server_port}/?quran-page-preview=official-green&page=17'
 r=page.goto(url,wait_until='domcontentloaded')
 assert r and r.ok
 page.locator('header>.site-nav button[data-tab="mushaf"]').click()
 page.wait_for_function("""() => document.getElementById('qApprovedOriginalImage')?.naturalWidth>250
     && document.getElementById('mushaf')?.classList.contains('q-original-source-ready')""",timeout=35000)
 proof=page.evaluate("""() => ({
  originalImageWidth:document.getElementById('qApprovedOriginalImage').naturalWidth,
  selectedPage:document.getElementById('qPageNumber').value,
  originalTextHidden:document.getElementById('qVerses').style.display,
  headerColor:getComputedStyle(document.getElementById('qApprovedReadingHeader')).backgroundColor,
  icon:document.querySelector('#qApprovedReaderMenu svg use')?.getAttribute('href')
 })""")
 assert proof['selectedPage']=='17' and proof['originalTextHidden']=='none',(width,proof)
 assert proof['originalImageWidth']>300 and proof['headerColor']=='rgb(24, 25, 29)',(width,proof)
 assert proof['icon']=='icons/navigation.svg#settings',(width,proof)
 page.screenshot(path=str(output/f'ACTUAL-SALATI-GENUINE-QURAN-PAGE17-{width}-PLAYER.png'),full_page=False)
 page.locator('#qApprovedClose').click()
 page.screenshot(path=str(output/f'ACTUAL-SALATI-GENUINE-QURAN-PAGE17-{width}-PLAYER-HIDDEN.png'),full_page=False)
 page.close()

try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
  for w,h in [(390,844),(412,915)]:
   screenshot_tabs(browser,w,h)
   screenshot_original_full_page(browser,w,h)
  browser.close()
 print('PASS: REAL Salati six tabs, scrolled sections, exact original settings gear and white-on-charcoal Quran header, authentic full page, 390/412 phones')
finally:
 server.shutdown()
