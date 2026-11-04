"""Saved-state entry regression on actual Salati UI, never a reconstructed reader."""
from pathlib import Path
from functools import partial
from threading import Thread
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import json,io,wave,time
root=Path(__file__).resolve().parents[1];out=root/'reports/mushaf-fatiha-entry';out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
 def do_GET(self):
  if self.path.split('?')[0].endswith('/pages/1.png'):time.sleep(.25)
  super().do_GET()
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')));Thread(target=server.serve_forever,daemon=True).start();results=[]
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  for width,height,lang in [(390,844,'ar'),(1440,900,'en')]:
   for saved in [{'page':2,'activeSurah':2},{'page':42,'activeSurah':2},{'page':564,'activeSurah':68},{}]:
    state={**saved,'bookmark':120,'printedEdition':'1441','reciter':'qatami','follow':False,'repeat':True,'autoNext':False,'size':28,'layoutVersion':2}
    page=b.new_page(viewport={'width':width,'height':height},service_workers='block',reduced_motion='reduce');errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.add_init_script("if(!sessionStorage.getItem('entry-seeded')){localStorage.setItem('salati-quran',JSON.stringify(%s));localStorage.setItem('salati',JSON.stringify({lang:'%s',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',method:'Oman',locationSet:true,locationMode:'manual'}));sessionStorage.setItem('entry-seeded','yes')}"%(json.dumps(state),lang))
    page.goto(f'http://127.0.0.1:{server.server_port}/');page.locator('[data-tab=mushaf]').click();page.wait_for_selector('.original-printed-page')
    first=page.locator('#qVerses [data-reading-page]').first.get_attribute('data-reading-page')
    if first!='1':page.screenshot(path=str(out/'before-fix.png'))
    assert first=='1',(saved,width,'Explicit entry must open Fatiha, not saved chapter',first)
    page.wait_for_selector('[data-reading-page="1"].original-printed-page');page.wait_for_timeout(350)
    assert page.locator('#qSurah').input_value()=='1'
    assert page.locator('#qVerses').evaluate('(e)=>Math.abs(e.scrollTop)<2')
    assert page.locator('[data-reading-page="1"] [data-ayah="1:1"]').count()==1
    # Deliberate navigation works; entering the tab again resets only its reading start.
    page.locator('#qSurah').evaluate("e=>{e.value='67';e.dispatchEvent(new Event('change',{bubbles:true}))}");page.wait_for_selector('[data-reading-page="562"].original-printed-page')
    page.evaluate("document.dispatchEvent(new Event('visibilitychange'))");page.wait_for_timeout(50);assert page.locator('#qSurah').input_value()=='67','Visibility resume must retain the deliberately selected chapter'
    if width>760:page.locator('#qReaderBack').click()
    else:page.locator('[data-tab=times]').click()
    page.locator('[data-tab=mushaf]').click();page.wait_for_selector('[data-reading-page="1"].original-printed-page');assert page.locator('#qSurah').input_value()=='1'
    # A bookmark is explicit navigation, never erased to force the default.
    page.locator('.printed-reader-header button').first.click();page.locator('#qResume').click();page.locator('#qReaderOptions>button').click();page.wait_for_selector('[data-reading-page="120"].original-printed-page')
    page.reload();page.locator('[data-tab=mushaf]').click();page.wait_for_selector('[data-reading-page="1"].original-printed-page')
    persisted=page.evaluate("JSON.parse(localStorage.getItem('salati-quran'))")
    for key in ['bookmark','reciter','size','repeat','autoNext','follow']:assert persisted[key]==state[key],(key,persisted,state)
    page.screenshot(path=str(out/f'{width}-{lang}-fatiha.png'));assert not errors,errors;results.append({'viewport':[width,height],'language':lang,'saved':saved,'result':'PASS'});page.close()
  # Opening the reader must not stop/replace background full-surah playback,
  # nor may its next follow cue immediately drag the entry back to Baqara.
  buf=io.BytesIO()
  with wave.open(buf,'wb') as wav:wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(8000);wav.writeframes(b'\0'*(900*16000))
  recording=buf.getvalue()
  def media(route):
   body=recording;headers={'Accept-Ranges':'bytes','Access-Control-Allow-Origin':'*'};status=200;value=route.request.headers.get('range','')
   if value.startswith('bytes='):
    a,z=value[6:].split('-',1);a=int(a or 0);z=min(int(z) if z else len(body)-1,a+65535,len(body)-1);headers['Content-Range']=f'bytes {a}-{z}/{len(body)}';body=body[a:z+1];status=206
   headers['Content-Length']=str(len(body));route.fulfill(status=status,content_type='audio/wav',headers=headers,body=body)
  page=b.new_page(viewport={'width':390,'height':844},service_workers='block',reduced_motion='reduce');page.route('https://**/*.mp3',media)
  page.goto(f'http://127.0.0.1:{server.server_port}/');page.locator('[data-tab=mushaf]').click();page.wait_for_selector('[data-reading-page="1"].original-printed-page')
  page.locator('#qSurah').evaluate("e=>{e.value='2';e.dispatchEvent(new Event('change',{bubbles:true}))}");page.wait_for_selector('[data-reading-page="2"].original-printed-page');page.locator('#qTransport').click();page.wait_for_function('!document.querySelector("#qAudio").paused&&document.querySelector("#qAudio").duration===900')
  playing=page.locator('#qAudio').evaluate('(e)=>e.currentSrc');assert playing.endswith('/002.mp3'),'Explicit chapter choice must beat pending entry initialization';page.locator('[data-tab=times]').click();page.locator('[data-tab=mushaf]').click();page.wait_for_selector('[data-reading-page="1"].original-printed-page')
  page.locator('#qAudio').evaluate('(e)=>{e.currentTime=80;e.dispatchEvent(new Event("timeupdate"))}');page.wait_for_selector('[data-ayah="2:7"].is-reciting',state='attached',timeout=8000)
  assert page.locator('#qAudio').evaluate('(e)=>!e.paused&&e.currentTime>=80')
  assert page.locator('#qAudio').evaluate('(e)=>e.currentSrc')==playing
  assert page.locator('#qSurah').input_value()=='1','Background cue must not override explicit Fatiha entry'
  assert page.locator('#qVerses [data-reading-page]').first.get_attribute('data-reading-page')=='1'
  assert page.locator('#qVerses').evaluate('(e)=>Math.abs(e.scrollTop)<2'),'Background follow cue must not drag Fatiha entry to Baqara'
  page.locator('#qTransport').click();assert page.locator('#qAudio').evaluate('(e)=>e.paused')
  page.locator('#qTransport').click();page.wait_for_function('!document.querySelector("#qAudio").paused&&document.querySelector("#qVerses").scrollTop>10')
  assert page.locator('#qAudio').evaluate('(e)=>e.currentSrc')==playing,'Explicit resume must restore follow without replacing the recording'
  page.locator('#qStop').click()
  # Merely returning from background during Fatiha playback is NOT a fresh
  # tab entry and must not introduce a new hold on the saved Follow setting.
  page.set_viewport_size({'width':390,'height':390});page.locator('#qSurah').evaluate("e=>{e.value='1';e.dispatchEvent(new Event('change',{bubbles:true}))}");page.locator('#qTransport').click()
  page.wait_for_function('!document.querySelector("#qAudio").paused&&document.querySelector("#qAudio").currentSrc.endsWith("/001.mp3")')
  page.evaluate("document.dispatchEvent(new Event('visibilitychange'))");page.wait_for_timeout(50)
  page.locator('#qAudio').evaluate('(e)=>{e.currentTime=22;e.dispatchEvent(new Event("timeupdate"))}')
  page.wait_for_selector('[data-ayah="1:5"].is-reciting',state='attached');page.wait_for_function('document.querySelector("#qVerses").scrollTop>10')
  assert page.locator('#qFollowToggle').is_checked();page.locator('#qStop').click();page.close();results.append({'viewport':[390,844],'background_audio':'same full-surah source/playhead; entry remains Fatiha after next cue','result':'PASS fixture'})
  b.close()
 (out/'result.json').write_text(json.dumps({'result':'PASS','cases':results,'physical_phone':'NOT RUN','audio_fixture':'900-second silent range-capable WAV; not a human audio audition'},indent=2)+'\n')
finally:server.shutdown()
print('PASS Fatiha entry:8 saved-state browser cases plus continuous background-cue case; explicit choice/bookmark, visibility resume, tab reopen/reload and preferences retained')
