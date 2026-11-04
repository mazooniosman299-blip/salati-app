"""Actual integrated reader: original ornaments, bounded single-column ink and no blank lead."""
from pathlib import Path
from functools import partial
from threading import Thread
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
from PIL import Image
import json
root=Path(__file__).resolve().parents[1];out=root/'reports/mushaf-ornaments';out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')));Thread(target=server.serve_forever,daemon=True).start();cases=[]
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True)
  for w,h in [(320,740),(390,844),(844,390),(935,325),(1440,900),(1920,1080),(390,1600)]:
   for n,s in [(1,1),(2,2),(564,68)]:
    page=b.new_page(viewport={'width':w,'height':h},service_workers='block',reduced_motion='reduce');errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.add_init_script("localStorage.setItem('salati-quran',JSON.stringify({activeSurah:%d,page:%d,printedEdition:'1441',follow:false,size:26,layoutVersion:2}))"%(s,n))
    page.goto(f'http://127.0.0.1:{server.server_port}/');page.locator('[data-tab=mushaf]').click();page.wait_for_selector('[data-reading-page="1"].original-printed-page')
    if n!=1:page.locator('#qSurah').evaluate("(e,s)=>{e.value=String(s);e.dispatchEvent(new Event('change',{bubbles:true}))}",s)
    page.wait_for_selector(f'[data-reading-page="{n}"].original-printed-page')
    target=page.locator(f'[data-reading-page="{n}"]')
    target.evaluate("e=>{const c=document.querySelector('#qVerses');c.scrollTo({top:c.scrollTop+e.getBoundingClientRect().top-c.getBoundingClientRect().top,behavior:'instant'})}")
    page.wait_for_function("n=>{const c=document.querySelector('#qVerses'),t=c.querySelector('[data-reading-page=\"'+n+'\"]');return c.scrollHeight-c.clientHeight>=c.scrollTop+t.getBoundingClientRect().top-c.getBoundingClientRect().top-1}",arg=n)
    target.evaluate("e=>{const c=document.querySelector('#qVerses');c.scrollTo({top:c.scrollTop+e.getBoundingClientRect().top-c.getBoundingClientRect().top,behavior:'instant'})}")
    page.wait_for_timeout(100)
    art=page.locator(f'[data-reading-page="{n}"] .printed-page-image');box=art.bounding_box();leaf=page.locator(f'[data-reading-page="{n}"]').bounding_box();read=page.locator('#qVerses').bounding_box();player=page.locator('#mushafPlayerSlot').bounding_box();svg=page.locator(f'[data-reading-page="{n}"] .printed-ayah-regions').bounding_box()
    assert read['y']+read['height']<=player['y']+1
    assert max(abs(box[k]-svg[k]) for k in ['x','y','width','height'])<1
    assert leaf['width']<=740.5 and abs(leaf['x']+leaf['width']/2-w/2)<2
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    im=Image.open(root/f'dist/quran/printed-1441/pages/{n}.png').convert('RGBA');ink=im.getchannel('A').getbbox();top=box['y']+ink[1]*box['width']/im.width

    if top>=player['y']:page.screenshot(path=str(out/'failure.png'))
    assert top<player['y'],(w,h,n,'Quran ink hidden',top,player,leaf)
    if n<=2:
     title=page.locator(f'[data-reading-page="{n}"] .printed-opening-title');title.locator('img').evaluate('(e)=>e.decode()');tb=title.bounding_box();assert title.locator('img').evaluate('(e)=>e.naturalWidth>0')
     assert 0<=top-tb['y']-tb['height']<=32,(w,h,n,top,tb)
     crop=json.loads((root/f'dist/quran/printed-1441/regions/{n}.json').read_text())['displayViewport'];assert crop[1]<=ink[1] and crop[1]+crop[3]>=ink[3]
    else: assert top-read['y']<=50
    style=page.locator(f'[data-reading-page="{n}"]').evaluate('(e)=>getComputedStyle(e).borderImageSource');assert 'floral-border.svg' in style
    label=page.locator(f'[data-reading-page="{n}"] .printed-page-index');assert 'page-cartouche.png' in label.evaluate('(e)=>getComputedStyle(e).backgroundImage')
    page.locator('#qVerses').evaluate('(e)=>e.scrollTop=e.scrollHeight');page.wait_for_function('document.querySelectorAll(".original-printed-page").length>=2');nodes=page.locator('.original-printed-page');one=nodes.nth(0).bounding_box();two=nodes.nth(1).bounding_box();assert one['y']+one['height']<=two['y']+1 and abs(one['x']-two['x'])<1
    if n==1 and h==1600:page.wait_for_function('document.querySelectorAll(".original-printed-page").length>=3',timeout=5000)
    page.locator('#qVerses').evaluate('(e)=>e.scrollTop=0');page.wait_for_timeout(100)
    if (w,n) in [(390,1),(1440,1),(1920,564)]:page.screenshot(path=str(out/f'{w}-ar-p{n}.png'))
    assert not errors,errors;cases.append({'viewport':[w,h],'page':n,'result':'PASS','paper_width':leaf['width'],'first_ink_y':top,'reader_top':read['y']});page.close()
  b.close()
 (out/'result.json').write_text(json.dumps({'result':'PASS','cases':cases,'reference':'Licensed original ornamental slices, not claimed exact AlMosaly art','physical_phone':'NOT RUN','Android':'separate release checks required'},ensure_ascii=False,indent=2)+'\n')
finally:server.shutdown()
print('PASS decorated integrated reader:21 real Chromium cases; original ink, no blank leading block, one bounded vertical column, real ornaments, accurate targets and separate player')
