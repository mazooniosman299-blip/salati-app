"""Regress the user's short/wide opening-page screenshot on the actual app."""
from pathlib import Path
from functools import partial
from threading import Thread
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
from PIL import Image
import json
root=Path(__file__).resolve().parents[1];out=root/'reports/mushaf-opening-whitespace';out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')));Thread(target=server.serve_forever,daemon=True).start();cases=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  for width,height in [(935,325),(844,390),(1440,700),(390,844),(320,740)]:
   for surah,n in [(1,1),(2,2)]:
    page=browser.new_page(viewport={'width':width,'height':height},service_workers='block',reduced_motion='reduce');errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.add_init_script("localStorage.setItem('salati-quran',JSON.stringify({activeSurah:%d,page:%d,printedEdition:'1441',follow:false,size:26,layoutVersion:2}))"%(surah,n))
    page.goto(f'http://127.0.0.1:{server.server_port}/');page.locator('[data-tab=mushaf]').click();page.wait_for_selector(f'[data-reading-page="{n}"].original-printed-page')
    node=page.locator(f'[data-reading-page="{n}"] .printed-page-image');image=Image.open(root/f'dist/quran/printed-1441/pages/{n}.png').convert('RGBA');bbox=image.getchannel('A').getbbox();box=node.bounding_box();reader=page.locator('#qVerses').bounding_box();dock=page.locator('#mushafPlayerSlot').bounding_box()
    region=json.loads((root/f'dist/quran/printed-1441/regions/{n}.json').read_text());x,y,w,h=region['displayViewport']
    assert x<=bbox[0] and y<=bbox[1] and x+w>=bbox[2] and y+h>=bbox[3],'Display crop must retain every nontransparent Quran pixel'
    ink_top=box['y']+bbox[1]*box['width']/image.width
    assert reader['y']-1<=ink_top<=reader['y']+32,(width,height,n,'Blank top margin hides Quran text',ink_top,reader)
    assert reader['y']+reader['height']<=dock['y']+1,'Player overlaps reader'
    assert node.evaluate('(e)=>e.naturalWidth')==image.width
    # Image and hit layer must keep the SAME full-image geometry after trimming.
    overlay=page.locator(f'[data-reading-page="{n}"] .printed-ayah-regions').bounding_box()
    assert abs(overlay['y']-box['y'])<1 and abs(overlay['height']-box['height'])<1,(box,overlay)
    targets=page.locator(f'[data-reading-page="{n}"] [data-ayah]');assert targets.count()==7 if n==1 else targets.count()==5
    target=targets.first;hitbox=target.bounding_box();hit=page.evaluate('([x,y])=>document.elementFromPoint(x,y)?.closest("[data-ayah]")?.dataset.ayah',[hitbox['x']+hitbox['width']/2,hitbox['y']+hitbox['height']/2]);assert hit==target.get_attribute('data-ayah'),'Ayah hit testing drifted after margin trim'

    page.screenshot(path=str(out/f'{width}x{height}-p{n}.png'));assert not errors,errors
    cases.append({'viewport':[width,height],'page':n,'first_ink_y':ink_top,'reader_top':reader['y'],'result':'PASS'});page.close()
  browser.close()
 (out/'result.json').write_text(json.dumps({'result':'PASS','cases':cases},indent=2)+'\n')
finally:server.shutdown()
print('PASS original opening pages: text immediately visible at five viewports, no pixel changes or clipped ink, hit layer remains aligned, player separate')
