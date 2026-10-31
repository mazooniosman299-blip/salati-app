"""Chromium acceptance test for the supplied dark three-tile navigation and Quran player reference."""
from pathlib import Path
from functools import partial
from threading import Thread
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
import json

root=Path(__file__).resolve().parents[1]
out=root/'reports/design-restoration-2026-10-31'
out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')))
Thread(target=server.serve_forever,daemon=True).start()
rgbblue='rgb(37, 99, 235)'
checks=[]
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  page=b.new_page(service_workers='block',viewport={'width':390,'height':940})
  errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual'}))")
  response=page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
  page.wait_for_timeout(1300)
  diagnostics={'status':response.status if response else None,'errors':errors,'links':page.locator('link[rel=stylesheet]').count(),'script':page.locator('script[src]').count(),'nav_selection':page.locator('.nav-selection').count(),'ready':page.evaluate('document.readyState')}
  assert not errors and diagnostics['nav_selection']==1,('Bootstrap failed',diagnostics)
  assert page.locator('html').get_attribute('dir')=='rtl'
  assert page.locator('link[href="design-restoration-v1.0.113.css"]').count()==1
  page.click('[data-tab=mushaf]')
  page.wait_for_function("document.querySelector('#qSurah').options.length>=114")
  for width in (390,1440):
   page.set_viewport_size({'width':width,'height':1000})
   assert page.locator('body').evaluate('(e)=>getComputedStyle(e).backgroundColor')=='rgb(11, 14, 19)'
   nav=page.locator('header>.site-nav .nav-icon-button')
   assert nav.count()==6
   tiles=nav.evaluate_all("""els=>els.map(e=>{let s=getComputedStyle(e);return {bg:s.backgroundColor,gradient:s.backgroundImage,border:s.borderTopColor,text:s.color,opacity:s.opacity}})""")
   assert all(t['text']=='rgb(255, 255, 255)' and t['opacity']=='1' for t in tiles),(width,tiles)
   assert sum(t['bg']=='rgb(29, 78, 216)' for t in tiles)==1 and all(t['bg'] in ('rgb(11, 14, 19)','rgb(29, 78, 216)') for t in tiles),(width,tiles)
   page.click('[data-tab=mushaf]')
   assert page.locator('#mushaf .reference-player').is_visible()
   player=page.locator('#mushaf .reference-player')
   styles=player.evaluate("""e=>{const s=getComputedStyle(e);return {bg:s.backgroundColor,gradient:s.backgroundImage,border:s.borderTopColor,opacity:s.opacity}}""")
   assert styles['bg']=='rgb(4, 5, 9)' and 'linear-gradient' in styles['gradient'] and '0.16' in styles['border'],(width,styles)
   seek=page.locator('#qSeek').evaluate("""e=>{
     let s=getComputedStyle(e);
     const selector='body.dark #mushaf .recitation-player.reference-player #qSeek::-webkit-slider-runnable-track';
     const rule=[...document.styleSheets].flatMap(sheet=>[...sheet.cssRules]).find(rule=>rule.selectorText===selector);
     return {cssTrack:s.getPropertyValue('--progress-track').trim(),
       mediaTrack:s.getPropertyValue('--media-track').trim(),
       trackRuleColor:rule?.style.backgroundColor,
       trackRuleHeight:rule?.style.height,
       visibleSliderHeight:e.getBoundingClientRect().height};
   }""")
   assert seek['cssTrack']=='#4B5767' and seek['mediaTrack']=='#4B5767' and seek['trackRuleColor'] in ('#4b5767','rgb(75, 87, 103)') and seek['trackRuleHeight']=='4px',(width,'reference progress mismatch',seek)
   page.locator('#qSeek').screenshot(path=str(out/f'quran-progress-{width}.png'))

   assert page.locator('#qTransport').is_visible()
   transport=page.locator('#qTransport').evaluate("(e)=>getComputedStyle(e,'::before').backgroundColor")
   assert transport==rgbblue,(width,'play/pause must be vivid blue',transport)
   stop=page.locator('#qStop')
   assert not stop.is_visible(),'Idle stop must remain hidden'
   stop.evaluate('(e)=>e.disabled=false')
   assert stop.evaluate('(e)=>getComputedStyle(e).backgroundColor')==rgbblue,(width,'stop',stop.evaluate('(e)=>getComputedStyle(e).backgroundColor'))
   stop.evaluate('(e)=>e.disabled=true')
   assert page.locator('.recitation-caption>strong').inner_text()=='المصحف الشريف'
   assert page.locator('.recitation-caption .quran-track').evaluate('(e)=>getComputedStyle(e).opacity')=='1'
   player.screenshot(path=str(out/f'player-reference-{width}.png'))
   checks.append({'width':width,'nav':'charcoal six navigable tiles','player':'deep charcoal','play_stop':'strong blue'})
   cases=[('mushaf','qSurahPickerOpen','choicePicker'),('settings','locationPickerOpen','locationMenu'),('settings','voicePickerOpen','voicePicker'),('dhikr','adhkarCategoryPickerOpen','adhkarCategoryMenuDialog')]
   for tab,trigger,menuid in cases:
    page.click(f'[data-tab={tab}]')
    page.click('#'+trigger)
    d=page.locator('#'+menuid)
    d.wait_for(state='visible',timeout=10000)
    actual=d.evaluate("""e=>{let c=getComputedStyle(e);return{bg:c.backgroundColor,border:c.borderTopWidth,color:c.color}}""")
    assert actual=={'bg':'rgb(4, 5, 9)','border':'0px','color':'rgb(255, 255, 255)'},(width,menuid,actual)
    page.mouse.move(0,0)
    page.wait_for_timeout(320)
    opts=d.locator('button.choice-option,button.voice-option,button.menu-option')
    assert opts.count()>0,(width,menuid,'missing choices')
    details=opts.evaluate_all("""es=>es.slice(0,8).filter(e=>getComputedStyle(e).display!=='none').map(e=>{let s=getComputedStyle(e);return{bg:s.backgroundColor,border:s.borderTopWidth,color:s.color}})""")
    assert details and all(x['border']=='0px' and x['color']=='rgb(255, 255, 255)' and x['bg'] in ['rgb(11, 14, 19)','rgb(21, 24, 29)','rgb(18, 21, 26)'] for x in details),(width,menuid,details)
    d.screenshot(path=str(out/f'{menuid}-{width}.png'))
    page.keyboard.press('Escape')
    assert not d.is_visible(),(width,menuid,'Escape must dismiss')
   for tab in ('times','mushaf','qibla','dhikr','tasbih','settings'):
    page.click('[data-tab='+tab+']')
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,tab,'horizontal overflow')
   page.click('[data-tab=settings]')
   command=page.locator('#previewFajrPhrase')
   assert command.evaluate('(e)=>getComputedStyle(e).backgroundColor')!='rgb(37, 99, 235)',(width,'ordinary button must not be blue')
  assert not errors,errors
  b.close()
 (out/'reference-acceptance.json').write_text(json.dumps({'result':'PASS','checks':checks,'page_errors':errors,'physical_device_tested':False},ensure_ascii=False,indent=2)+'\\n')
 print('PASS: real Chromium reference at 390/1440, vivid blue play/stop, uniform borderless menu, no overflow and no browser exceptions')
finally:server.shutdown()
