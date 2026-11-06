#!/usr/bin/env python3
"""Review-only screenshots on the real Salati page, never an imitation demo."""
from pathlib import Path
from functools import partial
from threading import Thread
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
import json
root=Path(__file__).resolve().parents[1]
out=root/'reports/surah-frame-review'
out.mkdir(parents=True,exist_ok=True)
index=json.loads((root/'dist/quran/printed-1441/surah-title-regions.json').read_text())
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')))
Thread(target=server.serve_forever,daemon=True).start()
checks=[]
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
  for width,height in [(390,844),(1440,900)]:
   for n,surah in [(1,1),(2,2),(50,3),(187,9),(564,68),(600,101),(602,106),(604,112)]:
    page=browser.new_page(viewport={'width':width,'height':height},service_workers='block',reduced_motion='reduce')
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.add_init_script("""localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual'}));""")
    page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
    page.locator('[data-tab="mushaf"]').click()
    page.wait_for_selector('[data-reading-page="1"].original-printed-page',timeout=30000)
    if n!=1:
     page.locator('#qSurah').evaluate("""(element,surah)=>{element.value=String(surah);element.dispatchEvent(new Event('change',{bubbles:true}));}""",surah)
    frame=page.locator(f'[data-reading-page="{n}"]')
    frame.wait_for(state='visible',timeout=30000)
    page.wait_for_function("""n=>{const e=document.querySelector('[data-reading-page="'+n+'"]');return !!e?.classList.contains('original-printed-page')&&(n<=2||e.querySelectorAll('.printed-reference-surah-heading').length>0);}""",arg=n,timeout=30000)
    leaf=frame.bounding_box()
    reader=page.locator('#qVerses').bounding_box()
    player=page.locator('#mushafPlayerSlot').bounding_box()
    assert reader['y']+reader['height']<=player['y']+1,(n,width,'overlap player')
    assert leaf['width']<=740.5 and leaf['width']<=width+1,(n,width,'wide paper')
    if n<=2:
     assert frame.locator('.printed-opening-title').count()==1
     bg=frame.locator('.printed-opening-title').evaluate('(el)=>getComputedStyle(el).backgroundImage')
     assert 'user-reference-surah-frame.svg' in bg,(n,bg)
    else:
     headings=index['pages'][str(n)]['headings']
     wraps=frame.locator('.printed-reference-surah-heading')
     assert wraps.count()==len(headings),(n,'missing frame',wraps.count())
     for k,h in enumerate(headings):
      item=wraps.nth(k)
      assert item.get_attribute('data-surah-frame')==str(h['surah'])
      # Measure the art and heading in one frame so moving scroll cannot
      # corrupt page-bound positioning assertions.
      rects=item.evaluate("""element=>{
       const a=element.closest('.printed-page-artwork').getBoundingClientRect();
       const b=element.getBoundingClientRect();
       return {top:b.top-a.top,totalHeight:a.height,
         clip:getComputedStyle(element.querySelector('.printed-reference-original-ink')).clipPath};
      }""")
      expected_y=rects['totalHeight']*h['y']/index['pages'][str(n)]['height']
      assert abs(rects['top']-expected_y)<2,(n,width,k,rects,expected_y)
      assert '30%' in rects['clip'],(n,'old heading hairline mask absent',rects)
      img=item.locator('img.printed-reference-surah-decoration')
      assert img.evaluate('(e)=>e.complete&&e.naturalWidth>0'),(n,width,'reference failed to decode')
      assert 'user-reference-surah-frame.svg' in img.get_attribute('src')
      assert item.evaluate('(e)=>getComputedStyle(e).pointerEvents')=='none'
      item.scroll_into_view_if_needed(timeout=15000)
      page.wait_for_timeout(120)
      item.screenshot(path=str(out/f'{width}-page{n}-surah{h["surah"]}-heading.png'))
     # The verse targets remain in the original unmodified plate overlay.
     assert frame.locator('.printed-ayah-regions [data-ayah]').count()>0
    # Capture the actual ornament at the visible position, not while the
    # selected chapter's automatic scroll is still traversing the page.
    target=frame.locator('.printed-opening-title') if n<=2 else frame.locator('.printed-reference-surah-heading').first
    target.scroll_into_view_if_needed(timeout=15000)
    page.wait_for_timeout(150)
    page.screenshot(path=str(out/f'{width}-page{n}-surah{surah}.png'),full_page=False)
    assert not errors,(width,n,errors)
    checks.append({'width':width,'height':height,'page':n,'surah':surah,'expected_frames':1 if n<=2 else len(headings),'pass':True})
    page.close()
  browser.close()
 (out/'results.json').write_text(json.dumps({'status':'PASS','cases':checks,'phone_device_tested':False,'published':False},indent=2)+'\n')
finally:server.shutdown()
print('PASS live Chromium source UI: '+str(len(checks))+' real screenshot cases and framed Al-Qalam/other mixed-page headings')
