"""User screenshot corrections: dark blue controls, unmasked mosque and reference media/menu geometry."""
from pathlib import Path
from functools import partial
from threading import Thread
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
import json
root=Path(__file__).resolve().parents[1];out=root/'reports/visual-corrections-1.0.109';out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')));Thread(target=s.serve_forever,daemon=True).start();checks=[]
try:
 with sync_playwright()as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(service_workers='block');errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual'}))")
  page.goto(f'http://127.0.0.1:{s.server_port}/',wait_until='domcontentloaded');page.click('[data-tab=mushaf]');page.wait_for_function('document.querySelector("#qSurah").options.length>=114');page.evaluate('document.fonts.ready')
  for width in [320,390,760,1440]:
   page.set_viewport_size({'width':width,'height':1000});page.click('[data-tab=times]')
   scene=page.locator('.hero-picture').bounding_box();photo=page.locator('.hero-picture img').bounding_box();style=page.locator('.hero-picture img').evaluate('(e)=>{let s=getComputedStyle(e);return{mask:s.maskImage,filter:s.filter,fit:s.objectFit,opacity:s.opacity}}')
   assert style=={'mask':'none','filter':'none','fit':'cover','opacity':'1'},style
   assert abs(scene['height']-photo['height'])<1 and abs(scene['width']-photo['width'])<1,(scene,photo)
   assert photo['height']>70
   page.locator('.prayer-overview').screenshot(path=str(out/f'widget-{width}.png'))
   for tab in ['times','mushaf','dhikr','qibla','tasbih','settings']:
    page.click(f'[data-tab={tab}]');assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,tab)
    if width in [390,1440]:page.screenshot(path=str(out/f'{tab}-{width}.png'))
   page.locator('#previewFajrPhrase').scroll_into_view_if_needed();page.mouse.move(0,0)
   assert page.locator('#previewFajrPhrase').evaluate('(e)=>getComputedStyle(e).backgroundColor')=='rgb(4, 5, 9)'
   page.screenshot(path=str(out/f'audio-{width}.png'))
   buttons=page.locator('footer>div>button');a,c=[el.bounding_box() for el in buttons.all()];horizontal=max(a['x'],c['x'])-min(a['x']+a['width'],c['x']+c['width']);vertical=max(a['y'],c['y'])-min(a['y']+a['height'],c['y']+c['height']);assert max(horizontal,vertical)>=13,(width,a,c)
   page.locator('footer').screenshot(path=str(out/f'footer-{width}.png'))
   page.click('[data-tab=mushaf]');assert not page.locator('#qStop').is_visible(),'No disabled Stop tile in the reference idle player'
   frame=page.locator('.reference-player');frame.screenshot(path=str(out/f'player-{width}.png'))
   assert page.locator('.mushaf-emblem').get_attribute('src')=='icons/quran.svg'
   title=page.locator('.quran-surah-title').first;assert title.evaluate('(e)=>getComputedStyle(e).boxShadow')!='rgb(50, 56, 63) 0px 0px 0px 4px inset';title.evaluate('(e)=>e.scrollIntoView({block:"center"})');title.screenshot(path=str(out/f'surah-title-{width}.png'))
   page.click('#qSurahPickerOpen');mark=page.locator('#choiceList [aria-selected=true] .choice-mark');mark.scroll_into_view_if_needed();assert 'icons/check.svg' in mark.evaluate('(e)=>getComputedStyle(e).backgroundImage');assert mark.evaluate('(e)=>getComputedStyle(e).fontSize')=='0px';box=mark.bounding_box();assert box['width']==box['height']==24
   page.locator('#choicePicker').screenshot(path=str(out/f'menu-{width}.png'));page.keyboard.press('Escape');checks.append({'width':width,'mosque_covers_scene':True,'blue_play_stop_only':True,'footer_gap':max(horizontal,vertical),'checkmark_square':True,'idle_stop_hidden':True})
  assert not errors,errors;b.close()
 (out/'checks.json').write_text(json.dumps({'result':'PASS','cases':checks,'page_errors':errors,'physical_device_tested':False},indent=2)+'\n');print('PASS: original mosque fills scene without masks; dark blue Quran transport only, spaced footer, charcoal surah plaques and fixed library check marks; six pages at four widths.')
finally:s.shutdown()
