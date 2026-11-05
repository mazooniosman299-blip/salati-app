"""Real ended events and user-controlled continuation, with no additional actions."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
import io,wave,json,time
root=Path(__file__).resolve().parents[1];out=root/'reports/quran-continuation-actions';out.mkdir(parents=True,exist_ok=True)
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
def enter(page):
 page.goto(f'http://127.0.0.1:{server.server_port}/');page.locator('[data-tab=mushaf]').click();page.wait_for_selector('[data-reading-page="1"].original-printed-page');page.evaluate('document.fonts.ready')
def play(page):
 page.locator('#qTransport').click();page.wait_for_function('!document.querySelector("#qAudio").paused&&document.querySelector("#qAudio").duration===900')
def ready(page):
 page.wait_for_function('!document.querySelector("#qAudio").paused&&document.querySelector("#qAudio").duration===900&&document.querySelector("#qDuration").textContent==="15:00"')
def finish(page,expected):
 page.locator('#qAudio').evaluate('e=>e.currentTime=899.8')
 page.wait_for_function('(id)=>document.querySelector("#qAudio").currentSrc.endsWith("/"+String(id).padStart(3,"0")+".mp3")&&!document.querySelector("#qAudio").paused',arg=expected)
def hit(page,key):
 target=page.locator('.printed-ayah[data-ayah="'+key+'"]');target.scroll_into_view_if_needed()
 point=target.evaluate('''e=>{const r=e.getBoundingClientRect();for(let y=1;y<8;y++)for(let x=1;x<8;x++){let a=r.x+r.width*x/8,b=r.y+r.height*y/8;if(document.elementFromPoint(a,b)?.closest('[data-ayah]')?.dataset.ayah===e.dataset.ayah)return{x:a,y:b};}return null}''')
 assert point,('No genuine visible hit point',key);page.mouse.click(point['x'],point['y'])
results=[]
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  for saved,expected in [({},True),({'autoNext':False,'repeat':False,'bookmark':120,'reciter':'shatri','follow':False},True),({'autoNext':False,'autoNextPolicy':1},False)]:
   page=b.new_page(viewport={'width':390,'height':844},service_workers='block');page.route('https://**/*.mp3',media)
   page.add_init_script("if(!localStorage.getItem('salati-quran'))localStorage.setItem('salati-quran',JSON.stringify(%s))"%json.dumps(saved));enter(page)
   assert page.locator('#qAutoNext').is_checked()==expected,(saved,'legacy/fresh state must continue by default; current explicit opt-out stays off')
   stored=page.evaluate("JSON.parse(localStorage.getItem('salati-quran'))")
   assert stored['autoNextPolicy']==1,stored
   for k in ['bookmark','reciter','follow']:
    if k in saved:assert stored[k]==saved[k],(k,stored)
   play(page)
   if expected:finish(page,2)
   else:
    page.locator('#qAudio').evaluate('e=>e.currentTime=899.8');page.wait_for_function('document.querySelector("#qAudio").paused');assert page.locator('#qAudio').evaluate('e=>e.currentSrc.endsWith("/001.mp3")')
   page.locator('#qStop').click();page.locator('#qAutoNext').evaluate('e=>{e.checked=false;e.dispatchEvent(new Event("change",{bubbles:true}))}');page.reload();page.locator('[data-tab=mushaf]').click();page.wait_for_selector('.original-printed-page');assert not page.locator('#qAutoNext').is_checked(),'Future explicit opt-out must survive reload'
   results.append({'saved':saved,'default':expected,'result':'pass'});page.close()
  # Playback context, not freshly reopened reading Fatiha, determines the next track.
  page=b.new_page(viewport={'width':390,'height':844},service_workers='block');page.route('https://**/*.mp3',media);enter(page);play(page);finish(page,2)
  page.locator('[data-tab=times]').click();page.locator('[data-tab=mushaf]').click();page.wait_for_selector('[data-reading-page="1"].original-printed-page');assert page.locator('#qSurah').input_value()=='1';assert page.locator('#qAudio').evaluate('e=>e.currentSrc.endsWith("/002.mp3")')
  finish(page,3);page.locator('#qStop').click();page.close()
  # Repeat has priority over automatic next; the final surah stops cleanly.
  for surah,repeat in [(1,True),(114,False)]:
   page=b.new_page(viewport={'width':390,'height':844},service_workers='block');page.route('https://**/*.mp3',media);enter(page)
   page.locator('#qSurah').evaluate('(e,id)=>{e.value=String(id);e.dispatchEvent(new Event("change",{bubbles:true}))}',surah)
   page.locator('#qRepeat').evaluate('(e,value)=>{e.checked=value;e.dispatchEvent(new Event("change",{bubbles:true}))}',repeat);play(page)
   page.locator('#qAudio').evaluate('e=>e.currentTime=899.8')
   if repeat:page.wait_for_function('!document.querySelector("#qAudio").paused&&document.querySelector("#qAudio").currentTime<2&&document.querySelector("#qAudio").currentSrc.endsWith("/001.mp3")')
   else:
    page.wait_for_function('document.querySelector("#qAudio").paused&&document.querySelector("#qAudio").getAttribute("src")===null');assert page.locator('#qTrackTitle').inner_text()=='سورة الناس'
   page.locator('#qStop').click();page.close();results.append({'surah':surah,'repeat':repeat,'result':'pass'})
  # A running Android session receives options only: no replay, seek or stop.
  # This tests the actual WebView bridge client, not the Android service itself.
  for policy,expected in [(None,True),(1,False)]:
   page=b.new_page(viewport={'width':390,'height':844},service_workers='block');errors=[];page.on('pageerror',lambda e:errors.append(e.stack))
   def delayed_index(route):
    time.sleep(.85)
    route.fulfill(status=200,content_type='application/json',body=(root/'dist/quran/printed-1441/index.json').read_bytes())
   page.route('**/quran/printed-1441/index.json',delayed_index)
   state={'autoNext':False,'reciter':'shatri','bookmark':120}
   if policy is not None:state['autoNextPolicy']=policy
   page.add_init_script('''localStorage.setItem('salati-quran',JSON.stringify(%s));
    window.nativeCalls=[];window.nativeState={session:'existing-android-session',reciter:'shatri',index:0,active:true,paused:false,position:12,duration:900,status:'playing',repeat:false,autoNext:false};
    window.SalatiNative={quranState:()=>JSON.stringify(window.nativeState),quranQueue:()=>JSON.stringify([{surah:1,url:'https://example.test/001.mp3',continuous:true,cues:[[1,0,900000]]}]),
     quranOptions:(session,repeat,autoNext)=>{nativeCalls.push(['options',session,repeat,autoNext]);nativeState.repeat=repeat;nativeState.autoNext=autoNext;},
     quranPlay:()=>{nativeCalls.push(['restart']);return 'ok'},quranStop:()=>nativeCalls.push(['stop']),quranSeek:()=>nativeCalls.push(['seek'])};'''%json.dumps(state))
   enter(page);assert page.locator('#qAutoNext').is_checked()==expected
   calls=page.evaluate('nativeCalls');assert calls==([['options','existing-android-session',False,True]] if expected else []),calls
   assert page.evaluate('nativeState.position')==12;assert not errors,errors;page.close();results.append({'native_bridge_policy':policy,'options_only':True,'result':'pass'})
  # Latest correction: existing player only, no new ayah dock or actions.
  # Latest scoped5Nov polish supersedes130 colors/fonts/frame/photo only.
  # Keep a full132 source snapshot; retain128/130 historical fixtures.
  assert (root/'dist/salati-ui.css').read_bytes()==(root/'tests/fixtures/salati-v132-approved-ui.css').read_bytes(),'Reader/UI CSS must remain exactly the scoped132 stylesheet'
  for width,height,lang in [(320,740,'ar'),(390,844,'ar'),(1440,900,'en'),(935,325,'ar')]:
   page=b.new_page(viewport={'width':width,'height':height},service_workers='block',reduced_motion='reduce');errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.route('https://**/*.mp3',media)
   page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:%s}))"%json.dumps(lang));enter(page)
   assert page.locator('#qAyahActions,[data-ayah-action],.ayah-action-dock').count()==0,'No unrequested action dock or buttons'
   controls=page.locator('#mushafPlayerSlot button').evaluate_all('es=>es.map(e=>e.id)');assert sorted(controls)==['qStop','qTransport'],controls
   hit(page,'1:2');ready(page);page.wait_for_function('document.querySelector("#qAudio").currentTime>2')
   assert page.locator('dialog[open]').count()==0,'Ayah selection must not open a black modal'
   assert page.locator('[data-ayah="1:2"]').get_attribute('aria-pressed')=='true'
   geo=page.evaluate('''()=>{const r=s=>{const b=document.querySelector(s).getBoundingClientRect();return {top:b.top,bottom:b.bottom,height:b.height,left:b.left,right:b.right}};return{reading:r('#qVerses'),player:r('#mushafPlayerSlot')}}''')
   assert geo['reading']['bottom']<=geo['player']['top']+1 and geo['reading']['height']>=60,(width,geo)
   source=page.locator('#qAudio').evaluate('e=>e.currentSrc')
   # User pause near the natural ending must hold the current file, not auto-advance.
   page.locator('#qAudio').evaluate('e=>e.currentTime=899');page.locator('#qTransport').click();page.wait_for_timeout(1200)
   assert page.locator('#qAudio').evaluate('(e)=>e.paused&&e.currentSrc===%s'%json.dumps(source)),'User pause must prevent automatic progression'
   page.locator('#qTransport').click();finish(page,2);ready(page)
   page.locator('#qAudio').evaluate('e=>e.currentTime=899');page.locator('#qStop').click();page.wait_for_timeout(1200)
   assert page.locator('#qAudio').evaluate('e=>e.paused&&!e.getAttribute("src")'),'User Stop must cancel progression'
   page.locator('#qSurah').evaluate("e=>{e.value='1';e.dispatchEvent(new Event('change',{bubbles:true}))}");page.wait_for_selector('[data-reading-page=\"1\"].original-printed-page')
   hit(page,'1:2');ready(page)
   page.screenshot(path=str(out/f'{width}-{lang}-existing-player.png'));assert not errors,errors;page.locator('#qStop').click();page.close();results.append({'viewport':[width,height],'lang':lang,'existing_ui':geo,'no_new_controls':True,'user_pause_and_stop':True,'result':'pass'})
  b.close()
finally:server.shutdown();server.server_close()
(out/'result.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n');print('PASS migration/default/explicit-off, real ended progression/repeat/final114, native options-only restore and4 actual existing-player viewport/pause/stop scenarios; no added actions')
