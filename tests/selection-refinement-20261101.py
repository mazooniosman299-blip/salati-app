"""Pixel/DOM acceptance for exactly the user-requested 2026-11-01 refinements."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright
import json

root=Path(__file__).resolve().parents[1]
evidence=root/'reports/selection-refinement-20261101'
evidence.mkdir(parents=True,exist_ok=True)
class Silent(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Silent,directory=str(root/'dist')))
Thread(target=server.serve_forever,daemon=True).start()
checks=[]
try:
  with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width in (360,390,768,1440):
      page=browser.new_page(viewport={'width':width,'height':920},service_workers='block')
      page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual'}))")
      errors=[]
      page.on('pageerror',lambda e:errors.append(str(e)))
      response=page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
      assert response and response.ok
      assert page.locator('link[href="selection-refinement-20261101.css"]').count()==1
      assert page.locator('body.dark').count()==1

      # Navigation: only selected tab is blue, without white card outline.
      nav=page.locator('header>.site-nav .nav-icon-button')
      assert nav.count()==6
      for tab in ['times','mushaf','qibla','dhikr','tasbih','settings']:
        page.click(f'[data-tab={tab}]')
        page.wait_for_timeout(25)
        items=nav.evaluate_all("""es=>es.map(e=>({
          active:e.classList.contains('active'),
          bg:getComputedStyle(e).backgroundColor,
          outline:getComputedStyle(e).outlineWidth,
          outlineColor:getComputedStyle(e).outlineColor,
          border:getComputedStyle(e).borderTopWidth
        }))""")
        assert sum(x['active'] for x in items)==1 and sum(x['bg']=='rgb(29, 78, 216)' for x in items)==1,(width,tab,items)
        assert (next(x for x in items if x['active'])['outline']=='0px' or next(x for x in items if x['active'])['outlineColor']=='rgb(37, 99, 235)'),(width,tab,'no white outline')
      page.locator('header>.site-nav').screenshot(path=str(evidence/f'nav-{width}.png'))

      # Prayer chips, including Isha, have translucent dark square-corner tiles.
      page.click('[data-tab=times]')
      page.locator('#prayers .prayer').first.wait_for(state='visible')
      tiles=page.locator('#prayers .prayer')
      assert tiles.count()>=5
      for i in range(tiles.count()):
        data=tiles.nth(i).evaluate("""e=>({
          radius:getComputedStyle(e).borderRadius,
          bg:getComputedStyle(e).backgroundColor,
          active:e.classList.contains('active')
        })""")
        assert data['radius']=='24px',(width,i,data)
        assert data['bg']==('rgb(53, 74, 103)' if data['active'] else 'rgb(45, 61, 86)'),(width,i,data)
      assert page.locator('#times .card.verse p').evaluate("e=>getComputedStyle(e).color")=='rgb(255, 255, 255)'
      assert page.locator('#times .hero-prayer>span').evaluate("e=>getComputedStyle(e).color")=='rgb(255, 255, 255)'
      page.locator('#times .prayer-overview').screenshot(path=str(evidence/f'prayers-{width}.png'))

      # Quran: existing surah ornament is scaled down, reciting outline replaced.
      page.click('[data-tab=mushaf]')
      page.wait_for_function("document.querySelector('#qSurah').options.length>=114")
      title=page.locator('#qVerses .quran-surah-title').first
      title.wait_for(state='visible',timeout=15000)
      info=title.evaluate("""e=>({
        height:e.getBoundingClientRect().height,
        width:e.getBoundingClientRect().width,
        image:getComputedStyle(e).backgroundImage
      })""")
      expected_height=54 if width<=600 else 60
      assert abs(info['height']-expected_height)<1 and info['width']<=721,(width,'surah title scaled',info)
      assert 'quran-surah-ornament.svg' in info['image']
      follow=page.locator('#qFollowToggle')
      assert follow.evaluate("e=>getComputedStyle(e).accentColor")=='rgb(37, 99, 235)',(width,'follow ayah blue')
      verse=page.locator('#qVerses .quran-text [data-ayah]').first
      verse.evaluate("e=>e.classList.add('is-reciting')")
      frame=verse.evaluate("""e=>({
        shadow:getComputedStyle(e).boxShadow,
        border:getComputedStyle(e).borderTopWidth,
        radius:getComputedStyle(e).borderRadius
      })""")
      assert frame['border']=='0px' and frame['radius']=='0px' and '187, 153, 83' in frame['shadow'],(width,'verse highlight',frame)
      verse.evaluate("e=>e.classList.remove('is-reciting')")
      page.locator('#qSheet').screenshot(path=str(evidence/f'quran-{width}.png'))

      # Selected row retains original waveform and exactly one left-hand tick.
      page.click('[data-tab=settings]')
      page.locator('#audioVoice').evaluate("""e=>{e.value='nufais';e.dispatchEvent(new Event('change',{bubbles:true}))}""")
      page.click('#voicePickerOpen')
      marks=page.locator('#voicePickerList .voice-option').evaluate_all("""es=>es.map(e=>{
 const a=e.getBoundingClientRect(),c=e.querySelector('.voice-check'),cr=c.getBoundingClientRect();
 const w=e.querySelector('.voice-symbol svg'),wr=w.getBoundingClientRect();
 return {value:e.dataset.voiceOption,active:e.getAttribute('aria-pressed')==='true',
   checkCount:e.querySelectorAll('.voice-check').length,
   checkDisplay:getComputedStyle(c).display,
   generated:getComputedStyle(e.querySelector('.voice-symbol'),'::after').content,
   waveform:getComputedStyle(w).display,
   left:cr.left-a.left,checkWidth:cr.width,checkMidY:cr.top+cr.height/2-a.top-a.height/2,
   waveRight:a.right-wr.right};
})""")
      assert sum(x['active'] for x in marks)==1 and sum(x['checkDisplay']=='flex' for x in marks)==1,(width,'one selected tick',marks)
      selected=next(x for x in marks if x['active'])
      assert selected['value']=='nufais' and selected['checkDisplay']=='flex' and 8<=selected['left']<=27,(width,'selected tick left',marks)
      assert all(x['checkCount']==1 and x['generated'] in ('none','normal') and x['waveform']!='none' for x in marks),(width,'no double checks and keep waveform',marks)
      page.locator('#voicePickerList').screenshot(path=str(evidence/f'voices-{width}.png'))
      page.click('#voicePickerClose')
      assert page.locator('#settings .audio-card>.eyebrow').evaluate("e=>getComputedStyle(e).color")=='rgb(255, 255, 255)'
      page.click('#locationPickerOpen')
      choice=page.locator('#locationAutomaticOption')
      choice.wait_for(state='visible',timeout=10000)
      alignment=choice.evaluate("""e=>{
        const icon=e.querySelector('.location-icon').getBoundingClientRect();
        const title=e.querySelector('.choice-option-text');
        const b=title.getBoundingClientRect(),line=parseFloat(getComputedStyle(title).lineHeight);
        return {offset:icon.top+icon.height/2-b.top-line/2};
      }""")
      page.locator('#locationAutomaticOption').screenshot(path=str(evidence/f'location-{width}.png'))
      assert abs(alignment['offset'])<4,(width,'centered pin',alignment)
      page.keyboard.press('Escape')
      for tab in ['times','mushaf','qibla','dhikr','tasbih','settings']:
        page.click(f'[data-tab={tab}]')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,tab,'overflow')
      assert not errors,(width,'browser errors',errors)
      checks.append({'width':width,'six_tabs_blue_only':True,'prayer_tiles_reference_capsules':True,'notes_white':True,
        'small_surah_ornament':True,'recitation_no_box':True,'follow_checkbox_blue':True,
        'one_left_voice_tick':True,'location_icon_centered':True,'runtime_errors':0})
      page.close()
    browser.close()
  (evidence/'results.json').write_text(json.dumps({'passed':True,'checks':checks},ensure_ascii=False,indent=2)+'\n')
  print('PASS: user-requested refinements at 360, 390, 768 and 1440 pixels')
finally:
  server.shutdown()
