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
  for width in [390,1366]:
   page.set_viewport_size({'width':width,'height':940})
   # Neutral translucent glass indicator must slide; no gold on any active icon.
   page.click('[data-tab=times]')
   page.wait_for_timeout(320)
   marker=page.locator('header>.site-nav .nav-selection')
   assert marker.is_visible(),(width,'missing sliding selection')
   start=marker.bounding_box()['x']
   page.click('[data-tab=mushaf]')
   page.wait_for_timeout(55)
   mid=marker.bounding_box()['x']
   dest=page.locator('[data-tab=mushaf]').bounding_box()['x']
   assert min(start,dest)<mid<max(start,dest),(width,'charcoal sliding animation missing',start,mid,dest)
   page.wait_for_timeout(290)
   neutral=marker.evaluate("(e)=>({bg:getComputedStyle(e).backgroundColor,border:getComputedStyle(e).borderTopColor,gradient:getComputedStyle(e).backgroundImage})")
   assert neutral['bg']=='rgba(255, 255, 255, 0.035)' and neutral['gradient']=='none',(width,neutral)
   assert page.locator('[data-tab=mushaf]').evaluate("(e)=>getComputedStyle(e).backgroundColor")=='rgb(11, 14, 19)',(width,'active tile must match charcoal')
   tile_gradient=page.locator('[data-tab=mushaf]').evaluate('(e)=>getComputedStyle(e).backgroundImage')
   assert 'rgb(27, 30, 37)' in tile_gradient and 'rgb(4, 5, 9)' in tile_gradient,(width,'tile should use approved neutral charcoal gradient',tile_gradient)
   assert page.locator('[data-tab=mushaf] .nav-symbol').evaluate("(e)=>getComputedStyle(e).color")=='rgb(255, 255, 255)',(width,'active icon must be white')
   assert marker.evaluate("(e)=>getComputedStyle(e,'::after').content")=='none',(width,'unexpected gold underline')
   page.screenshot(path=str(out/f'charcoal-sliding-nav-{width}.png'))
   page.click('[data-tab=settings]')
   toggles=page.locator('[data-audio-prayer],#fajrAnnouncementToggle,#audioEnable,#duaToggle,#silentAdhanToggle')
   assert toggles.count()==9
   for toggle in toggles.all():
    original=toggle.evaluate("(e)=>e instanceof HTMLInputElement?e.checked:e.getAttribute('aria-checked')==='true'")
    for on,expected in [(False,'#15181D'),(True,'#20252B')]:
     toggle.evaluate("""(e,v)=>{if(e instanceof HTMLInputElement)e.checked=v;else {e.setAttribute('aria-checked',String(v));e.classList.toggle('is-on',v);}}""",on)
     color=bg(toggle)
     assert color==rgb(expected),(width,toggle.get_attribute('id'),toggle.get_attribute('data-audio-prayer'),on,color,expected)
    toggle.evaluate("""(e,v)=>{if(e instanceof HTMLInputElement)e.checked=v;else{e.setAttribute('aria-checked',String(v));e.classList.toggle('is-on',v);}}""",original)
   toggles.evaluate_all("""(es)=>es.forEach(e=>{if(e instanceof HTMLInputElement)e.checked=true;else{e.setAttribute('aria-checked','true');e.classList.add('is-on')}})""")
   if width<761:
    page.locator('#settings .prayer-switches').evaluate("(e)=>e.scrollIntoView({block:'center',behavior:'instant'})")
    page.wait_for_timeout(80)
    boxes=page.evaluate("""() => {const s=document.querySelector('#settings .prayer-switches').getBoundingClientRect(),n=document.querySelector('header>.site-nav').getBoundingClientRect();return {switchBottom:s.bottom,navTop:n.top}}""")
    assert boxes['switchBottom']+8<=boxes['navTop'],('Mobile navigation must not cover prayer toggles',boxes)
   page.screenshot(path=str(out/f'matte-switches-{width}.png'))
   page.click('[data-tab=mushaf]')
   page.wait_for_function('document.getElementById("qSurah").options.length>=114')
   page.wait_for_selector('.quran-reading-page',state='visible',timeout=12000)
   reader=page.locator('.quran-reading-page').first
   assert bg(reader)==rgb('#15181D'),(width,'reader',bg(reader))
   player=page.locator('#mushaf .reference-player')
   assert bg(player)==rgb('#040509'),(width,'player',bg(player))
   player_gradient=player.evaluate('(e)=>getComputedStyle(e).backgroundImage')
   assert 'rgb(23, 26, 31)' in player_gradient and 'rgb(4, 5, 9)' in player_gradient,(width,'player should use near-black neutral gradient',player_gradient)
   assert page.locator('#qVerses').inner_text().strip(),'Quran text must not disappear'
   assert page.locator('#qTransport').is_visible(),'Audio player play/pause control must remain visible'
   for key in ['qRepeat','qAutoNext']:
    checkbox=page.locator('#'+key)
    checkbox.evaluate('(e)=>e.checked=true')
    assert bg(checkbox)==rgb('#20252B'),(width,key,bg(checkbox))
    checkbox.evaluate('(e)=>e.checked=false')
   page.locator('.quran-reading-page').first.screenshot(path=str(out/f'quran-page-{width}.png'))
   player.screenshot(path=str(out/f'quran-player-{width}.png'))
   page.click('#qSurahPickerOpen')
   dialog=page.locator('#choicePicker')
   dialog.wait_for(state='visible')
   row=dialog.locator('.choice-option').first
   assert bg(row) in [rgb('#15181D'),rgb('#20252B')],(width,'surah row',bg(row))
   assert page.locator('#choiceList .choice-option').count()>=114,'All 114 surahs must remain selectable'
   # Assert materials rather than a token's mere presence in the CSS file.
   plain=dialog.locator('.choice-option[aria-selected="false"]').first
   selected=dialog.locator('.choice-option[aria-selected="true"]').first
   assert bg(plain)==rgb('#15181D'),(width,'unselected surah material',bg(plain))
   assert 'linear-gradient' in plain.evaluate('(e)=>getComputedStyle(e).backgroundImage'),(width,'unselected material must retain subtle depth')
   if selected.count():
    assert bg(selected)==rgb('#20252B'),(width,'selected surah material',bg(selected))
    assert 'linear-gradient' in selected.evaluate('(e)=>getComputedStyle(e).backgroundImage'),(width,'selected material must retain depth')
   assert bg(dialog)==rgb('#0B0E13'),(width,'modal material',bg(dialog))
   assert bg(dialog.locator('input[type=search]'))==rgb('#15181D'),(width,'search material')
   dialog.screenshot(path=str(out/f'surah-picker-{width}.png'))
   page.keyboard.press('Escape')
   assert not dialog.is_visible()
   page.click('[data-tab=qibla]')
   compass=page.locator('#qiblaDial')
   assert compass.is_visible()
   image=compass.evaluate("(e)=>getComputedStyle(e).backgroundImage")
   assert 'radial-gradient' in image,(width,'qibla surface',image)
   assert bg(page.locator('#qibla .qibla-card'))==rgb('#15181D')
   assert 'rgb(25, 29, 35)' in page.locator('#qibla .qibla-card').evaluate('(e)=>getComputedStyle(e).backgroundImage')
   page.locator('#qibla .qibla-card').screenshot(path=str(out/f'qibla-{width}.png'))
   page.click('[data-tab=times]')
   assert bg(page.locator('#prayers'))==rgb('#040509'),(width,'prayer strip surface')
   chosen=page.locator('#prayers .prayer.active')
   if chosen.count():assert bg(chosen)==rgb('#15181D'),(width,'active prayer material')
   page.click('[data-tab=settings]')
   page.click('#locationPickerOpen')
   loc=page.locator('#locationMenu')
   loc.wait_for(state='visible')
   assert bg(loc)==rgb('#0B0E13'),(width,'location sheet material')
   # Pointer remains over the now-open dialog after clicking the trigger; move
   # away and let the 280ms hover transition settle before checking base fill.
   page.mouse.move(0,0)
   page.wait_for_timeout(360)
   ordinary=loc.locator('.choice-option[aria-selected="false"]:not(:disabled)').first
   ordinary_color=bg(ordinary)
   assert ordinary_color==rgb('#15181D'),(width,'location option material',ordinary_color,ordinary.evaluate('(e)=>({hover:e.matches(":hover"),transition:getComputedStyle(e).transition,gradient:getComputedStyle(e).backgroundImage})'))
   loc.screenshot(path=str(out/f'location-picker-{width}.png'))
   page.keyboard.press('Escape')
   assert not loc.is_visible()
   page.click('[data-tab=dhikr]')
   page.click('#adhkarCategoryPickerOpen')
   adhkar_modal=page.locator('#adhkarCategoryMenuDialog')
   adhkar_modal.wait_for(state='visible')
   assert bg(adhkar_modal)==rgb('#0B0E13'),(width,'adhkar category background')
   page.mouse.move(0,0)
   page.wait_for_timeout(360)
   adhkar_row=adhkar_modal.locator('.choice-option[aria-selected="false"]:not(:disabled)').first
   assert bg(adhkar_row)==rgb('#15181D'),(width,'adhkar category row',bg(adhkar_row))
   adhkar_modal.screenshot(path=str(out/f'adhkar-picker-{width}.png'))
   page.keyboard.press('Escape')
   assert not adhkar_modal.is_visible()
   for tab in ['times','mushaf','dhikr','qibla','tasbih','settings']:
    page.click(f'[data-tab={tab}]')
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,tab,'overflow')
  assert not errors,errors
  browser.close()
 print('PASS: graphite sliding selection (no gold), charcoal ON switches (9), Quran reading panels, audio player, 114-surah modal, qibla dial, no overflow on phone/desktop.')
finally:
 server.shutdown()
