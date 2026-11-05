"""Real responsive acceptance for the user's scoped5Nov corrections; no mocked UI."""
from pathlib import Path
from functools import partial
from threading import Thread
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from datetime import datetime,timezone
from playwright.sync_api import sync_playwright
import json,sys,os

root=Path(__file__).resolve().parents[1]
baseline='--baseline' in sys.argv
out=Path(os.environ.get('SALATI_POLISH_QA_OUT',root/'reports/scoped-polish-authentic'))/('before' if baseline else 'after')
out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')))
Thread(target=server.serve_forever,daemon=True).start()
results=[]
def metric(page,selector):
 return page.locator(selector).evaluate('''e=>{const s=getComputedStyle(e),b=e.getBoundingClientRect();return {color:s.color,background:s.backgroundColor,shadow:s.boxShadow,border:s.border,width:b.width,height:b.height,font:parseFloat(s.fontSize)}}''')
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  for w,h in [(1440,900),(320,740),(390,844),(455,900)]:
   for lang in ['ar','en']:
    page=browser.new_page(viewport={'width':w,'height':h},service_workers='block',reduced_motion='reduce')
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.clock.set_fixed_time(datetime(2026,11,5,9,0,tzinfo=timezone.utc))
    state={'lang':lang,'lat':23.588,'lon':58.3829,'zone':'Asia/Muscat','name':'مسقط، عُمان','locationSet':True,'locationMode':'manual','method':'Oman','count':0}
    page.add_init_script('localStorage.setItem("salati",'+json.dumps(json.dumps(state))+')')
    page.goto(f'http://127.0.0.1:{server.server_port}/');page.wait_for_selector('#prayers .prayer');page.evaluate('document.fonts.ready')
    row={'width':w,'lang':lang,'home_name':metric(page,'#nextName'),'home_time':metric(page,'#nextTime')}
    row['verse']=page.locator('#times .verse>span').evaluate('''e=>{const r=document.createRange();r.selectNodeContents(e);return {text:e.textContent,lines:new Set([...r.getClientRects()].map(b=>Math.round(b.top))).size,inkWidth:r.getBoundingClientRect().width,available:e.getBoundingClientRect().width}}''')
    if not baseline:
     row['photo_points']=page.locator('.home-mosque').evaluate('''e=>{const b=e.getBoundingClientRect(),h=e.closest('.home-hero').getBoundingClientRect(),s=getComputedStyle(e),p=s.objectPosition.split(' ').map(v=>parseFloat(v)/100),scale=Math.max(b.width/e.naturalWidth,b.height/e.naturalHeight);return [[496,206],[774,205],[660,440],[250,335]].map(([x,y])=>({x:b.x+(b.width-e.naturalWidth*scale)*p[0]+x*scale,y:b.y+(b.height-e.naturalHeight*scale)*p[1]+y*scale,left:Math.max(b.left,h.left),right:Math.min(b.right,h.right),top:Math.max(b.top,h.top),bottom:Math.min(b.bottom,h.bottom)}))}''')
     assert all(p['left']<=p['x']<=p['right'] and p['top']+2<=p['y']<=p['bottom'] for p in row['photo_points']),('Real minaret tips/dome/sunset clipped',w,row['photo_points'])
     assert row['home_name']['font']==(32 if w<=760 else 44),row
     assert row['home_time']['font']==(28 if w<=760 else 36),row
     edges=page.locator('.home-next>*').evaluate_all('es=>es.map(e=>{const r=document.createRange();r.selectNodeContents(e);return r.getBoundingClientRect().right})')
     assert max(edges)-min(edges)<=1,edges
     assert row['verse']['lines']==1 and row['verse']['inkWidth']<=row['verse']['available']+1,row['verse']
     assert row['verse']['text']=='﴿ إِنَّ الصَّلَاةَ كَانَتْ عَلَى الْمُؤْمِنِينَ كِتَابًا مَوْقُوتًا ﴾'
    page.screenshot(path=str(out/f'{lang}-times-{w}.png'))
    page.locator('[data-tab=settings]').click();page.locator('#method').select_option('Auto',force=True)
    row['adjust']=metric(page,'[data-adjust=fajr][data-step="1"]')
    row['save']=metric(page,'button[form=preferences][type=submit]')
    row['method_info']={'text':page.locator('#automaticMethodInfo').inner_text(),'visible':page.locator('#automaticMethodInfo').is_visible()}
    if not baseline:
     assert row['adjust']['background']=='rgb(37, 99, 235)',row['adjust']
     assert row['adjust']['width']==row['adjust']['height']==44,row['adjust']
     assert 'inset' in row['save']['shadow'] and '1px' in row['save']['shadow'],row['save']
     assert not row['method_info']['visible'] and not row['method_info']['text'],row['method_info']
     page.locator('[data-adjust=fajr][data-step="1"]').click()
     assert page.locator('#adjust-fajr').input_value()=='1'
     page.locator('#cancelPrayerAdjustments').click();assert page.locator('#adjust-fajr').input_value()=='0'
     page.locator('button[form=preferences][type=submit]').click()
     assert page.evaluate('JSON.parse(localStorage.salati).method')=='Auto'
    page.locator('button[form=preferences][type=submit]').scroll_into_view_if_needed();page.screenshot(path=str(out/f'{lang}-settings-{w}.png'))
    page.locator('[data-tab=tasbih]').click()
    row['counter']=metric(page,'#counter');row['caption']=metric(page,'#tasbih .eyebrow')
    row['guide_heading']=page.get_by_text('طريقة التسبيح',exact=True).count() if lang=='ar' else page.get_by_text('How to count',exact=True).count()
    if not baseline:
     assert row['counter']['background']=='rgb(37, 99, 235)',row['counter']
     assert row['caption']['color']=='rgb(255, 255, 255)',row['caption']
     assert row['guide_heading']==0,row
     assert '٥٩٧' in page.locator('.tasbih-guide').inner_text() or '597' in page.locator('.tasbih-guide').inner_text()
     for _ in range(3):page.locator('#counter').click()
     assert page.locator('#tasbihCount').inner_text()=='3'
     page.locator('#reset').click();assert page.locator('#tasbihCount').inner_text()=='0'
    page.mouse.move(0,0);page.screenshot(path=str(out/f'{lang}-tasbih-{w}.png'))
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(w,lang)
    assert not errors,errors
    results.append(row);page.close()
  if not baseline:
   page=browser.new_page(viewport={'width':390,'height':844},service_workers='block',reduced_motion='no-preference')
   page.goto(f'http://127.0.0.1:{server.server_port}/');page.wait_for_selector('.site-nav.has-glass-navigation')
   motion=page.evaluate('''async()=>{const frame=()=>new Promise(r=>requestAnimationFrame(r));let max=0;for(const tab of ['qibla','tasbih','times','settings','dhikr','times']){document.querySelector('[data-tab='+tab+']').click();await frame();await frame();const all=[...document.querySelectorAll('.nav-symbol')].flatMap(e=>e.getAnimations()).filter(a=>a.playState==='running');max=Math.max(max,all.length);if(all.some(a=>a.effect.getTiming().duration!==180))throw Error('Unexpected icon animation');}return {max,active:document.querySelector('.site-nav button.active').dataset.tab}}''')
   assert motion=={'max':1,'active':'times'},motion
   page.emulate_media(reduced_motion='reduce')
   page.wait_for_function("[...document.querySelectorAll('.nav-symbol')].every(e=>!e.getAnimations().some(a=>a.playState==='running'))")
   page.locator('[data-tab=qibla]').click()
   assert page.locator('.nav-symbol').evaluate_all("es=>es.every(e=>e.getAnimations().length===0)"),'Reduced motion must suppress real icon animation'
   page.close()
  browser.close()
finally:
 server.shutdown()
 (out/'metrics.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print('CAPTURED baseline' if baseline else 'PASS scoped home/settings/tasbih actual colors, type, brace layout, saved actions and responsive geometry',len(results))
