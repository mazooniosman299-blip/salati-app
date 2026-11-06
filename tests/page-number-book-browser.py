#!/usr/bin/env python3
"""Actual Salati reader screenshots: ONLY the bottom page-number open-book frame."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
import json
root=Path(__file__).resolve().parents[1]
out=root/'reports/page-number-book'
out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')))
Thread(target=server.serve_forever,daemon=True).start()
# The bottom folio uses the owner's original Eastern Arabic printed numerals;
# Quran ayah numbers and original page artwork remain entirely untouched.
cases=[]
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
  for width,height in [(390,844),(1440,900)]:
   for number,surah in [(1,1),(50,3),(564,68),(604,114)]:
    page=browser.new_page(viewport={'width':width,'height':height},service_workers='block',reduced_motion='reduce')
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.add_init_script("""localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',method:'Oman',locationSet:true,locationMode:'manual'}));""")
    page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
    page.locator('[data-tab="mushaf"]').click()
    page.wait_for_selector('[data-reading-page="1"].original-printed-page',timeout=40000)
    if number!=1:
     page.locator('#qSurah').evaluate("""(element,surah)=>{element.value=String(surah);element.dispatchEvent(new Event('change',{bubbles:true}))}""",surah)
    leaf=page.locator(f'[data-reading-page="{number}"].original-printed-page')
    leaf.wait_for(state='visible',timeout=40000)
    label=leaf.locator('.printed-page-index')
    label.scroll_into_view_if_needed(timeout=20000)
    page.wait_for_timeout(300)
    expected=str(number).translate(str.maketrans('0123456789','٠١٢٣٤٥٦٧٨٩'))
    value=label.inner_text().strip()
    assert value==expected,(width,number,'wrong Eastern Arabic page digit',value,expected)
    computed=label.evaluate("""e=>{
      const s=getComputedStyle(e),r=e.getBoundingClientRect(),reader=document.querySelector('#qVerses').getBoundingClientRect(),
       dock=document.querySelector('#mushafPlayerSlot').getBoundingClientRect();
      return {bg:s.backgroundImage,width:r.width,height:r.height,font:s.fontSize,fontFamily:s.fontFamily,fontWeight:s.fontWeight,fontLoaded:document.fonts.check('19px AmiriQuran'),color:s.color,
       top:r.top,bottom:r.bottom,readerBottom:reader.bottom,dockTop:dock.top,space:document.documentElement.scrollWidth-innerWidth};
    }""")
    assert 'page-book-from-reference.png' in computed['bg'],(width,number,'book missing',computed)
    digits=label.locator('.printed-page-index-digits')
    assert digits.count()==1,(width,number,'missing independent digit plate')
    assert digits.inner_text().strip()==expected,(width,number,'wrong folio plate text')
    rects=digits.evaluate("""e=>{
      const b=e.closest('.printed-page-index').getBoundingClientRect(),r=e.getBoundingClientRect(),s=getComputedStyle(e);
      return {parentX:b.x,parentY:b.y,parentW:b.width,parentH:b.height,
        glyphX:r.x,glyphY:r.y,glyphW:r.width,glyphH:r.height,
        background:s.backgroundColor,stroke:s.webkitTextStrokeWidth};
    }""")
    assert abs((rects['glyphX']+rects['glyphW']/2)-(rects['parentX']+rects['parentW']/2))<1.1,(width,number,'digit off horizontal book center',rects)
    assert abs((rects['glyphY']+rects['glyphH']/2)-(rects['parentY']+rects['parentH']*.48))<1.1,(width,number,'digit off vertical book center',rects)
    assert rects['background']!='rgba(0, 0, 0, 0)' and rects['background']!='transparent',(width,number,'original book spine still visible through digit')
    assert rects['glyphW']<=rects['parentW']-2 and rects['glyphH']<=rects['parentH']-3,(width,number,'folio ink outside book')
    assert 'AmiriQuran' in computed['fontFamily'] and computed['font']=='19px' and computed['fontWeight']=='400' and computed['fontLoaded'],(width,number,'print glyph font missing',computed)
    assert 45<=computed['width']<=47 and 41<=computed['height']<=43,(width,number,'compact 46x42 book dimensions',computed)
    assert computed['bottom']<=computed['readerBottom']+1,(width,number,'below reader',computed)
    assert computed['readerBottom']<=computed['dockTop']+1,(width,number,'player overlap',computed)
    assert computed['space']<=1,(width,number,'horizontal overflow',computed)
    image=page.request.get(f'http://127.0.0.1:{server.server_port}/quran/printed-1441/ornaments/page-book-from-reference.png')
    assert image.status==200 and image.headers['content-type'].startswith('image/png'),(width,number,'actual book image unavailable')
    assert leaf.locator('.printed-page-artwork .printed-page-image').count()==1
    assert leaf.locator('.printed-ayah-regions [data-ayah]').count()>0
    label.screenshot(path=str(out/f'{width}-page{number}-book-only.png'))
    digits.screenshot(path=str(out/f'{width}-page{number}-digit-detail.png'))
    page.screenshot(path=str(out/f'{width}-page{number}-actual-app.png'),full_page=False)
    assert not errors,(width,number,errors)
    cases.append({'viewport':[width,height],'printed_page':number,'eastern_arabic_digits':value,'book_size':[computed['width'],computed['height']],'status':'PASS'})
    page.close()
  browser.close()
 (out/'results.json').write_text(json.dumps({'result':'PASS','count':len(cases),'cases':cases,'real_browser':True,'physical_device':False,'production_published':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
finally:
 server.shutdown()
print('PASS actual Salati reader '+str(len(cases))+' real screenshots with original user book, immutable Quran text, unblocked player/nav, authentic Eastern Arabic page labels in embedded Amiri Quran font')
