#!/usr/bin/env python3
"""Actual app-only proof for image from user's own screenshot, not a mockup."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
import json
from PIL import Image
root=Path(__file__).resolve().parents[1]
out=root/'reports/page-number-book';out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')))
Thread(target=server.serve_forever,daemon=True).start()
cases=[]
reference_photo={}
def ink_bbox(path):
    picture=Image.open(path).convert('RGB')
    pts=[(x,y) for y in range(7,picture.height-7) for x in range(7,picture.width-7)
        if max(picture.getpixel((x,y)))<120]
    assert len(pts)>=9,('No real dark numeral ink visible in screenshot',str(path))
    return ((min(x for x,y in pts)+max(x for x,y in pts))/2,
            (min(y for x,y in pts)+max(y for x,y in pts))/2,
            len(pts))
def outside_book_match(a,b):
    i1=Image.open(a).convert('RGB');i2=Image.open(b).convert('RGB')
    assert i1.size==i2.size
    total=0;errors=0
    for y in range(i1.height):
      for x in range(i1.width):
        if 13<=x<=43 and 12<=y<=41: continue
        total+=3
        u=i1.getpixel((x,y));v=i2.getpixel((x,y))
        errors+=sum(abs(u[k]-v[k]) for k in range(3))
    return errors/total
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
  for width,height in [(390,844),(1440,900)]:
   for number,surah in [(1,1),(50,3),(564,68),(604,114)]:
    page=browser.new_page(viewport={'width':width,'height':height},service_workers='block',reduced_motion='reduce')
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.add_init_script("""localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual'}));""")
    page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
    page.locator('[data-tab="mushaf"]').click()
    page.wait_for_selector('[data-reading-page="1"].original-printed-page',timeout=40000)
    if number!=1:
     page.locator('#qSurah').evaluate("""(el,n)=>{el.value=String(n);el.dispatchEvent(new Event('change',{bubbles:true}));}""",surah)
    leaf=page.locator(f'[data-reading-page="{number}"].original-printed-page')
    leaf.wait_for(state='visible',timeout=40000)
    label=leaf.locator('.printed-page-index')
    label.scroll_into_view_if_needed(timeout=20000)
    page.wait_for_timeout(300)
    expected=str(number).translate(str.maketrans('0123456789','٠١٢٣٤٥٦٧٨٩'))
    assert label.inner_text().strip()==expected,(number,'wrong bottom number')
    digits=label.locator('.printed-page-index-digits')
    assert digits.count()==1 and digits.inner_text().strip()==expected
    data=label.evaluate("""e=>{
     const b=e.getBoundingClientRect(),s=getComputedStyle(e),g=e.querySelector('.printed-page-index-digits'),d=g.getBoundingClientRect(),v=getComputedStyle(g),p=getComputedStyle(e,'::before');
     const sc=document.querySelector('#qVerses').getBoundingClientRect(),dock=document.querySelector('#mushafPlayerSlot').getBoundingClientRect();
     return {w:b.width,h:b.height,src:p.backgroundImage,flip:p.transform,background:s.backgroundColor,
      centered:Math.abs((d.left+d.width/2)-(b.left+b.width/2)),
      centeredY:Math.abs((d.top+d.height/2)-(b.top+b.height/2)),
      digitW:d.width,digitH:d.height,opacity:v.opacity,inkBackground:v.backgroundColor,
      font:v.fontFamily,bookBottom:b.bottom,readerBottom:sc.bottom,playerTop:dock.top,
      overflow:document.documentElement.scrollWidth-innerWidth};
    }""")
    image='user-book-page1.webp'
    assert image in data['src'],(width,number,'not identical photographic original',data)
    if number!=1:
     assert 'user-book-digit-seam.webp' in data['src'],(width,number,'missing photo-sourced seam repair',data)
    else:
     assert 'user-book-digit-seam.webp' not in data['src'],(width,number,'overlaid original page-one digit',data)
    assert data['flip']=='none',(width,number,'exact screenshot was mirrored',data)
    assert data['background'] in ('transparent','rgba(0, 0, 0, 0)')
    assert data['inkBackground'] in ('transparent','rgba(0, 0, 0, 0)'),(width,number,'opaque badge hiding original book')
    assert abs(data['w']-56)<1 and abs(data['h']-51)<1,(width,number,'wrong approved size',data)
    assert data['centered']<1.05,(width,number,'folio glyph not horizontally centered',data)
    assert 4.5<data['centeredY']<6.5,(width,number,'visible Amiri glyph baseline should be optically centered, NOT its CSS box',data)
    assert data['opacity']==('0' if number==1 else '1'),(width,number,'duplicate page one glyph',data)
    assert 'AmiriQuran' in data['font']
    assert data['digitW']<=data['w']-3,(width,number,'digits extend outside book')
    assert data['bookBottom']<=data['readerBottom']+1 and data['readerBottom']<=data['playerTop']+1,(width,number,'player overlap')
    assert data['overflow']<=1,(width,number,'horizontal overflow')
    resp=page.request.get(f'http://127.0.0.1:{server.server_port}/quran/printed-1441/ornaments/{image}')
    assert resp.status==200 and resp.headers['content-type'].startswith('image/webp'),(width,number,'photographic book missing')
    if number!=1:
     patch=page.request.get(f'http://127.0.0.1:{server.server_port}/quran/printed-1441/ornaments/user-book-digit-seam.webp')
     assert patch.status==200 and patch.headers['content-type'].startswith('image/webp'),(width,number,'source-derived seam repair not loading')
    assert leaf.locator('.printed-page-artwork .printed-page-image').count()==1
    assert leaf.locator('.printed-ayah-regions [data-ayah]').count()>0
    saved=out/f'{width}-page{number}-book-only.png'
    label.screenshot(path=str(saved))
    actual=ink_bbox(saved)
    if number==1:
     reference_photo[width]=(saved,actual)
    else:
     ref_path,ref_ink=reference_photo[width]
     assert abs(actual[0]-ref_ink[0])<=2.6 and abs(actual[1]-ref_ink[1])<=2.6,(width,number,'VISUAL ink differs from original centered ١',actual,ref_ink)
     pixel_error=outside_book_match(saved,ref_path)
     assert pixel_error<2.0,(width,number,"VISUAL book cover differs from user reference",pixel_error)
    page.screenshot(path=str(out/f'{width}-page{number}-actual-app.png'),full_page=False)
    assert not errors,(width,number,errors)
    cases.append({'viewport':[width,height],'page':number,'digits':expected,'source_image':image,'visible_ink_bbox_center':list(actual[:2]),'status':'PASS'})
    page.close()
  browser.close()
 (out/'results.json').write_text(json.dumps({'status':'PASS','cases':cases,'physically_tested':False,'published':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
finally:
 server.shutdown()
print('PASS '+str(len(cases))+' REAL Salati screenshots, original photo number-one centered, zero mirroring, eight untampered printed pages')
