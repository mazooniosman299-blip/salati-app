"""Real pointer/touch selection and keyboard focus on original Quran SVG targets."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
import io,wave,json
root=Path(__file__).resolve().parents[1];out=root/'reports/ayah-focus';out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')));Thread(target=server.serve_forever,daemon=True).start()
buf=io.BytesIO()
with wave.open(buf,'wb') as wav:wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(8000);wav.writeframes(b'\0'*(900*16000))
recording=buf.getvalue()
def media(route):
 body=recording;headers={'Accept-Ranges':'bytes','Access-Control-Allow-Origin':'*'};status=200;value=route.request.headers.get('range','')
 if value.startswith('bytes='):
  a,z=value[6:].split('-',1);a=int(a or 0);z=min(int(z) if z else len(body)-1,a+65535,len(body)-1);headers['Content-Range']=f'bytes {a}-{z}/{len(body)}';body=body[a:z+1];status=206
 headers['Content-Length']=str(len(body));route.fulfill(status=status,content_type='audio/wav',headers=headers,body=body)
def open_baqara(page):
 page.locator('[data-tab=mushaf]').click();page.wait_for_selector('[data-reading-page="1"].original-printed-page');page.locator('#qSurah').evaluate("e=>{e.value='2';e.dispatchEvent(new Event('change',{bubbles:true}))}");page.wait_for_selector('[data-reading-page="2"].original-printed-page')
def hit(page,touch):
 target=page.locator('.printed-ayah[data-ayah="2:2"]');target.scroll_into_view_if_needed()
 point=target.evaluate('''e=>{const r=e.getBoundingClientRect();for(let y=1;y<8;y++)for(let x=1;x<8;x++){let a=r.x+r.width*x/8,b=r.y+r.height*y/8;if(document.elementFromPoint(a,b)?.closest('[data-ayah]')===e)return{x:a,y:b};}return null}''')
 assert point,'Original calibrated verse must have a real visible hit point'
 if touch:page.touchscreen.tap(point['x'],point['y'])
 else:page.mouse.click(point['x'],point['y'])
 return target
def style(target):return target.evaluate('''e=>{const c=getComputedStyle(e);return {focused:document.activeElement===e,focusVisible:e.matches(':focus-visible'),outline:c.outlineStyle,width:c.outlineWidth,stroke:c.stroke,strokeWidth:c.strokeWidth,fill:c.fill,selected:e.classList.contains('is-selected'),pressed:e.getAttribute('aria-pressed')}}''')
def audio_ready(page):page.wait_for_function('!document.querySelector("#qAudio").paused&&document.querySelector("#qAudio").duration===900&&document.querySelector("#qDuration").textContent==="15:00"&&document.querySelector("#qAudio").currentSrc.endsWith("/002.mp3")')
cases=[]
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  for width,height,lang,touch in [(1440,900,'ar',False),(390,844,'ar',True),(320,740,'en',True),(1440,900,'en',False)]:
   page=b.new_page(viewport={'width':width,'height':height},has_touch=touch,is_mobile=touch,service_workers='block',reduced_motion='reduce');errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.route('https://**/*.mp3',media)
   page.add_init_script("if(!localStorage.getItem('salati-quran'))localStorage.setItem('salati-quran',JSON.stringify({follow:false}));localStorage.setItem('salati',JSON.stringify({lang:%s}))"%json.dumps(lang))
   page.goto(f'http://127.0.0.1:{server.server_port}/');open_baqara(page);target=hit(page,touch);audio_ready(page);pointer=style(target);page.screenshot(path=str(out/f'{width}-{lang}-pointer.png'))
   assert pointer['outline']=='none' and pointer['width']=='0px',('Browser rectangular focus box must be absent after pointer/touch',pointer)
   assert pointer['selected'] and pointer['pressed']=='true' and pointer['fill']=='rgb(155, 120, 62)',pointer
   assert not pointer['focusVisible'] and pointer['stroke']=='none',pointer
   assert page.locator('dialog[open],#qAyahActions,[data-ayah-action]').count()==0
   assert sorted(page.locator('#mushafPlayerSlot button').evaluate_all('es=>es.map(e=>e.id)'))==['qStop','qTransport']
   assert page.locator('#qAutoNext').is_checked()
   # Keyboard users keep a visible brown path indicator, not a black rectangle.
   if touch:target.focus()
   page.keyboard.press('Tab');keyboard=page.locator('.printed-ayah:focus-visible');assert keyboard.count()==1
   key_style=style(keyboard);assert key_style['outline']=='none' and key_style['stroke']=='rgb(138, 102, 50)' and float(key_style['strokeWidth'].removesuffix('px'))>0,key_style
   selected=keyboard.get_attribute('data-ayah');page.keyboard.press('Enter');audio_ready(page);assert page.locator('[data-ayah="'+selected+'"]').get_attribute('aria-pressed')=='true'
   page.screenshot(path=str(out/f'{width}-{lang}-keyboard.png'));page.locator('#qTransport').click();page.wait_for_function('document.querySelector("#qAudio").paused');page.locator('#qStop').click()
   page.locator('#qReaderBack').click();open_baqara(page);assert style(hit(page,touch))['outline']=='none';page.locator('#qStop').click()
   page.reload();open_baqara(page);target=hit(page,touch);audio_ready(page);assert style(target)['outline']=='none';page.locator('#qStop').click();assert not errors,errors
   cases.append({'viewport':[width,height],'language':lang,'touch':touch,'pointer':pointer,'keyboard':key_style,'result':'PASS'});page.close()
  b.close()
finally:server.shutdown();server.server_close()
(out/'result.json').write_text(json.dumps({'result':'PASS','cases':cases,'physical_phone':'NOT RUN','audio':'900-second deterministic ranged WAV fixture'},ensure_ascii=False,indent=2)+'\n');print('PASS4 real pointer/touch/keyboard AR/EN cases, no black outline, preserved full audio/selection/autoNext/controls, tab return and reload')
