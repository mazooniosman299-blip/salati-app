"""Eight user-screenshot regressions. Real Chromium layout, not CSS string heuristics."""
import json
from pathlib import Path
from threading import Thread
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from functools import partial
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
out=root/'reports/eight-mobile-20261101'
out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')))
Thread(target=server.serve_forever,daemon=True).start()
results=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for width,height in [(360,740),(390,844),(412,915),(768,1024),(1440,900)]:
   page=browser.new_page(viewport={'width':width,'height':height},service_workers='block')
   saved={'lat':23.588,'lon':58.3829,'name':'مسقط','zone':'Asia/Muscat',
          'locationSet':True,'locationMode':'manual','method':'Auto','madhab':'Shafi'}
   page.add_init_script(f"localStorage.setItem('salati',JSON.stringify({json.dumps(saved,ensure_ascii=False)}))")
   errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
   r=page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
   assert r.ok,(width,r.status)
   page.click('[data-tab=times]')
   page.wait_for_function("document.querySelectorAll('#prayers .prayer').length===6")
   active=page.locator('#times #prayers .prayer.active')
   active.wait_for(state='visible',timeout=12000)
   pill=active.evaluate("""e=>({radius:getComputedStyle(e).borderTopLeftRadius,
       bg:getComputedStyle(e).backgroundColor,border:getComputedStyle(e).borderTopColor})""")
   assert pill=={'radius':'8px','bg':'rgba(0, 0, 0, 0.72)','border':'rgb(131, 135, 139)'},(width,pill)
   assert page.locator('.hero-picture img').get_attribute('src')=='images/mosque-reference-original.png'
   if width==390:page.locator('#times .prayer-overview').screenshot(path=str(out/'home-390.png'))

   page.click('[data-tab=settings]')
   cancel=page.locator('#cancelPrayerAdjustments')
   c=cancel.evaluate("""e=>({color:getComputedStyle(e).color,bg:getComputedStyle(e).backgroundColor,
        opacity:getComputedStyle(e).opacity,border:getComputedStyle(e).borderTopWidth})""")
   assert c['color']=='rgb(255, 255, 255)' and c['opacity']=='1' and c['border']!='0px',(width,c)
   assert cancel.is_visible()
   if width==390:cancel.screenshot(path=str(out/'cancel-390.png'))

   page.click('[data-tab=qibla]')
   assert page.locator('#headingValue').count()==0
   btn=page.locator('#qibla .qibla-reading #compassEnable')
   assert btn.count()==1 and btn.is_visible(),(width,'button moved')
   assert page.locator('#qibla .compass-actions button').count()==1
   assert 'اتجاه هاتفك' not in page.locator('#qibla').inner_text()
   if width==390:page.locator('#qibla .qibla-reading').screenshot(path=str(out/'bearing-390.png'))

   page.click('[data-tab=mushaf]')
   page.wait_for_function("document.querySelector('#qSurah').options.length===114")
   # Native select is intentionally hidden behind the accessible custom surah
   # picker. Trigger the same change event that picker sends to the select.
   page.locator('#qSurah').evaluate("e=>{e.value='67';e.dispatchEvent(new Event('change',{bubbles:true}))}")
   page.wait_for_function("""() => !!document.querySelector('#qVerses [data-ayah="67:1"]')""")
   await_initial=page.locator('#qVerses [data-ayah="67:1"]').count()
   assert await_initial>=1,(width,'surah 67 first verse missing')
   text=page.locator('#qVerses').inner_text()
   assert not any(ch in text for ch in tuple(chr(n) for n in (0x06DD,0x06DE,0x06DF,0x06E0))),(width,'font-dependent black dot survives')
   if width==390:page.locator('#qSheet').screenshot(path=str(out/'quran-390.png'))
   # Simulate a genuine user reading mid-surah then moving to another tab.
   page.evaluate("""() => {
     const main=document.querySelector('main');
     if(innerWidth<=760)main.scrollTop=main.scrollHeight/2;
     else window.scrollTo(0,1400);
   }""")
   page.click('[data-tab=times]')
   page.click('[data-tab=mushaf]')
   page.wait_for_function("""() => !!document.querySelector('#qVerses [data-ayah="67:1"]')""")
   assert page.locator('#qSurah').input_value()=='67',(width,'selected surah lost')
   assert page.locator('#qVerses [data-ayah="67:1"]').count()>0,(width,'not first verse')
   assert page.locator('#qBookmark').count()==1,(width,'bookmarks must survive')

   if width<=760:
    geometry=page.evaluate("""() => {
     const main=document.querySelector('main').getBoundingClientRect();
     const nav=document.querySelector('header>.site-nav').getBoundingClientRect();
     return {mainBottom:main.bottom,navTop:nav.top,scrollable:getComputedStyle(document.querySelector('main')).overflowY,
       bodyOverflow:getComputedStyle(document.body).overflowY,viewport:innerHeight};
    }""")
    assert geometry['mainBottom']<=geometry['navTop']-5,(width,'nav must not cover Quran even mid-scroll',geometry)
    assert geometry['scrollable']=='auto',(width,'main must scroll without covering nav',geometry)
   assert not errors,(width,'uncaught JS errors',errors[:7])
   results.append({'width':width,'height':height,'activeBadge':pill,'quranRestart':True,'hiddenGlyphsRemoved':True,'browserErrors':0})
   page.close()
  browser.close()
 (out/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print('PASS: eight screenshot-driven user repairs at five viewport sizes',results)
finally:
 server.shutdown()
