"""Visual acceptance: 5 requested repairs tested against real Chromium DOM."""
from pathlib import Path
from functools import partial
from threading import Thread
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
out=root/'reports/design-restoration-2026-10-31'
out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args): pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')))
Thread(target=server.serve_forever,daemon=True).start()
def bg(locator):
 return locator.evaluate("(e)=>getComputedStyle(e).backgroundColor")
def rgb(h):
 return f'rgb({int(h[1:3],16)}, {int(h[3:5],16)}, {int(h[5:7],16)})'
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  page=browser.new_page(service_workers='block',viewport={'width':390,'height':940})
  errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual'}))")
  page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
  assert page.locator('body').evaluate('(e)=>getComputedStyle(e).backgroundColor')==rgb('#0B0E13')
  # Golden underline follows the SAME animated selection overlay, not a static tab border.
  indicator=page.locator('header>.site-nav .nav-selection')
  indicator.wait_for(state='visible')
  golden=indicator.evaluate("""(e)=>{const c=getComputedStyle(e,'::after');return{content:c.content,background:c.backgroundColor,height:c.height,position:c.position,z:getComputedStyle(e).zIndex}}""")
  assert golden['content']=='""' and golden['background']==rgb('#C6A66B') and golden['position']=='absolute' and golden['z']=='3',('Gold indicator missing',golden)
  page.click('[data-tab=mushaf]')
  page.wait_for_timeout(450)
  start=indicator.bounding_box()['x']
  page.click('[data-tab=qibla]')
  page.wait_for_timeout(65)
  midway=indicator.bounding_box()['x']
  page.wait_for_timeout(430)
  end=indicator.bounding_box()['x']
  assert start!=end and min(start,end)<midway<max(start,end),('Gold underline must animate between tabs',start,midway,end)
  for width in [390,1366]:
   page.set_viewport_size({'width':width,'height':940})
   page.click('[data-tab=settings]')
   toggles=page.locator('[data-audio-prayer],#fajrAnnouncementToggle,#audioEnable,#duaToggle,#silentAdhanToggle')
   assert toggles.count()==9
   for toggle in toggles.all():
    original=toggle.evaluate("(e)=>e instanceof HTMLInputElement?e.checked:e.getAttribute('aria-checked')==='true'")
    for on,expected in [(False,'#15181D'),(True,'#2368C4')]: 
     toggle.evaluate("""(e,v)=>{if(e instanceof HTMLInputElement)e.checked=v;else {e.setAttribute('aria-checked',String(v));e.classList.toggle('is-on',v);}}""",on)
     page.wait_for_timeout(340)
     color=bg(toggle)
     assert color==rgb(expected),(width,toggle.get_attribute('id'),toggle.get_attribute('data-audio-prayer'),on,color,expected)
    toggle.evaluate("""(e,v)=>{if(e instanceof HTMLInputElement)e.checked=v;else{e.setAttribute('aria-checked',String(v));e.classList.toggle('is-on',v);}}""",original)
   toggles.evaluate_all("""(es)=>es.forEach(e=>{if(e instanceof HTMLInputElement)e.checked=true;else{e.setAttribute('aria-checked','true');e.classList.add('is-on')}})""")
   if width<761:
    page.locator('#settings .prayer-switches').evaluate("(e)=>e.scrollIntoView({block:'center',behavior:'instant'})")
    page.wait_for_timeout(80)
    boxes=page.evaluate("""() => {const s=document.querySelector('#settings .prayer-switches').getBoundingClientRect(),n=document.querySelector('header>.site-nav').getBoundingClientRect();return {switchBottom:s.bottom,navTop:n.top}}""")
    assert boxes['switchBottom']+8<=boxes['navTop'],('Mobile navigation must not cover prayer toggles',boxes)
   page.screenshot(path=str(out/f'blue-switches-{width}.png'))
   page.click('[data-tab=mushaf]')
   page.wait_for_function('document.getElementById("qSurah").options.length>=114')
   page.wait_for_selector('.quran-reading-page',state='visible',timeout=12000)
   reader=page.locator('.quran-reading-page').first
   assert bg(reader)==rgb('#141C25'),(width,'reader',bg(reader))
   player=page.locator('#mushaf .reference-player')
   assert bg(player)==rgb('#0B1017'),(width,'player',bg(player))
   assert page.locator('#qVerses').inner_text().strip(),'Quran text must not disappear'
   assert page.locator('#qTransport').is_visible(),'Audio player play/pause control must remain visible'
   for key in ['qRepeat','qAutoNext']:
    checkbox=page.locator('#'+key)
    checkbox.evaluate('(e)=>e.checked=true')
    page.wait_for_timeout(340)
    assert bg(checkbox)==rgb('#2368C4'),(width,key,bg(checkbox))
    checkbox.evaluate('(e)=>e.checked=false')
    page.wait_for_timeout(340)
   page.locator('.quran-reading-page').first.screenshot(path=str(out/f'quran-page-{width}.png'))
   player.screenshot(path=str(out/f'quran-player-{width}.png'))
   page.click('#qSurahPickerOpen')
   dialog=page.locator('#choicePicker')
   dialog.wait_for(state='visible')
   row=dialog.locator('.choice-option').first
   assert bg(row) in [rgb('#131B25'),rgb('#1D2A38')],(width,'surah row',bg(row))
   assert page.locator('#choiceList .choice-option').count()>=114,'All 114 surahs must remain selectable'
   dialog.screenshot(path=str(out/f'surah-picker-{width}.png'))
   page.keyboard.press('Escape')
   assert not dialog.is_visible()
   page.click('[data-tab=qibla]')
   compass=page.locator('#qiblaDial')
   assert compass.is_visible()
   image=compass.evaluate("(e)=>getComputedStyle(e).backgroundImage")
   assert 'radial-gradient' in image,(width,'qibla surface',image)
   assert bg(page.locator('#qibla .qibla-card'))==rgb('#101720')
   page.locator('#qibla .qibla-card').screenshot(path=str(out/f'qibla-{width}.png'))
   for tab in ['times','mushaf','dhikr','qibla','tasbih','settings']:
    page.click(f'[data-tab={tab}]')
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,tab,'overflow')
  assert not errors,errors
  browser.close()
 print('PASS: blue ON switches (9), Quran reading panels, audio player, 114-surah modal, qibla dial, no overflow on phone/desktop.')
finally:
 server.shutdown()
