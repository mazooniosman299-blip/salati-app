#!/usr/bin/env python3
"""Real mobile Chromium screen proof for SINGLE full Mushaf leaf, not an app card.

Requires source PDF leaves from the prior SHA-256 validated publisher archive.
Never claims stylistic identity to the user's selected web image #5.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
out=root/'reports/official-green-fullpage'
out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')))
Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for w,h in [(320,740),(390,844),(412,915),(768,960)]:
   page=browser.new_page(viewport={'width':w,'height':h},device_scale_factor=1,service_workers='block')
   errors=[]
   page.on('pageerror',lambda e:errors.append(str(e)))
   page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual'}))")
   response=page.goto(f'http://127.0.0.1:{server.server_port}/?mushaf-preview=official-green&layout=immersive',
                      wait_until='domcontentloaded')
   assert response and response.ok
   # The preview is a branch-only mode inside the real Salati tab, never a separate app.
   page.locator('header>.site-nav button[data-tab=mushaf]').click()
   page.wait_for_function("() => document.body.classList.contains('salati-mushaf-fullpage-review')",timeout=30000)
   page.wait_for_function("() => document.getElementById('qTrack')?.textContent?.includes('البقرة') && document.getElementById('qPageNumber')?.value==='17'",timeout=20000)
   a=page.evaluate("""() => {
      const r=id=>document.getElementById(id).getBoundingClientRect();
      const sheet=document.getElementById('qSheet');
      const preview=document.getElementById('qGreenOriginalReview');
      const img=preview.querySelector('img');
      const elementRect=img.getBoundingClientRect();
      return {
        frame:{top:r('qSheet').top,bottom:r('qSheet').bottom,left:r('qSheet').left,right:r('qSheet').right},
        page:{top:r('qGreenOriginalReview').top,bottom:r('qGreenOriginalReview').bottom,width:r('qGreenOriginalReview').width},
        playerTop:r('mushafPlayerSlot').top,
        playerBottom:r('mushafPlayerSlot').bottom,
        playerColor:getComputedStyle(document.getElementById('mushafPlayerSlot')).backgroundColor,
        transport:{w:r('qTransport').width,h:r('qTransport').height},
        seek:{w:r('qSeek').width,h:r('qSeek').height},
        img:{top:elementRect.top,bottom:elementRect.bottom,naturalWidth:img.naturalWidth,naturalHeight:img.naturalHeight,
             fit:getComputedStyle(img).objectFit,ratio:img.naturalWidth/img.naturalHeight},
        frameStyle:{radius:getComputedStyle(sheet).borderRadius,overflow:getComputedStyle(sheet).overflowY},
        hiddenNav:document.querySelector('header>.site-nav').getBoundingClientRect().bottom<=r('qSheet').bottom,
        hasSourcePage:!!document.querySelector('#qGreenOriginalReview span')?.textContent?.includes('20'),
        stop:!!document.getElementById('qStop'),
        exit:!!document.getElementById('salatiImmersivePageExit'),
        fullWidth:document.documentElement.scrollWidth<=innerWidth+1
      };
   }""")
   assert abs(a['frame']['left'])<=1 and abs(a['frame']['right']-w)<=1,(w,'full page width',a)
   assert abs(a['frame']['top'])<=1 and abs(a['frame']['bottom']-h)<=1,(w,'full screen reader',a)
   assert abs(a['page']['top'])<=1 and abs(a['page']['bottom']-a['playerTop'])<=1,(w,'complete page immediately ABOVE audio player',a)
   assert a['playerBottom']<=h+1,(w,'player must be fully visible without covering Quran or bottom tabs',a)
   assert a['playerColor']=='rgb(24, 25, 29)',(w,'existing Salati charcoal player palette changed',a)
   assert a['transport']['w']>=40 and a['transport']['h']>=40,(w,'audio button too small',a)
   assert a['seek']['w']>75 and a['seek']['h']>12,(w,'timeline clipped',a)
   assert a['page']['width']>=w-1 and a['img']['naturalWidth']>250,(w,'source page missing',a)
   assert a['img']['fit']=='contain' and a['img']['top']>=-1 and a['img']['bottom']<=h+1,(w,'source cropped',a)
   assert a['frameStyle']['radius']=='0px',(w,'old rounded card remains',a)
   assert a['playerTop']>=a['img']['bottom']-1,(w,'player overlays original Quran image',a)
   assert a['hasSourcePage'] and a['stop'] and a['exit'] and a['fullWidth'],(w,'reader controls/source missing',a)
   assert not errors,(w,errors)
   page.screenshot(path=str(out/f'salati-mushaf-ONE-FULL-PAGE-{w}.png'),full_page=False)
   # Tapping the Quran image hides the player, allowing an unbroken full-height
   # page. A second tap restores the controls without resetting audio state.
   page.locator('#qGreenOriginalReview img').click(position={'x':w//2,'y':min(150,h//3)})
   assert not page.locator('#mushafPlayerSlot').is_visible(),(w,'tap did not dismiss player')
   assert abs(page.locator('#qGreenOriginalReview').bounding_box()['height']-h)<=1
   page.screenshot(path=str(out/f'salati-mushaf-FULL-PAGE-PLAYER-HIDDEN-{w}.png'),full_page=False)
   page.locator('#qGreenOriginalReview img').click(position={'x':w//2,'y':min(150,h//3)})
   assert page.locator('#mushafPlayerSlot').is_visible(),(w,'tap did not restore player')
   page.locator('#mushafPlayerSlot').scroll_into_view_if_needed()
   player=page.locator('#mushafPlayerSlot')
   assert player.is_visible(),(w,'cannot access approved audio controls')
   assert page.locator('#qSeek').is_visible(),(w,'audio seek bar missing')
   page.screenshot(path=str(out/f'salati-mushaf-player-below-page-{w}.png'),full_page=False)
   page.close()
  clean=browser.new_page(service_workers='block')
  clean.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
  clean.click('header>.site-nav button[data-tab=mushaf]')
  clean.wait_for_function("() => document.querySelector('#qVerses [data-ayah]')")
  assert clean.locator('#qGreenOriginalReview').count()==0
  assert clean.locator('#salatiImmersivePageExit').count()==0
  assert clean.locator('#mushafPlayerSlot').count()==1
  clean.close()
  browser.close()
 print('PASS complete uncropped source leaf plus charcoal/blue Salati player, both visible in one viewport, tap toggle, at 320/390/412/768px; no change to default app')
finally:
 server.shutdown()
