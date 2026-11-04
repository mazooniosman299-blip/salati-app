"""Actual integrated Salati reader; fixture audio verifies behavior, not listening quality."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
import io,wave,json,os
root=Path(__file__).resolve().parents[1];out=Path(os.environ.get('SALATI_QA_OUT',root/'reports/mushaf1441'));out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')));Thread(target=server.serve_forever,daemon=True).start()
buffer=io.BytesIO()
with wave.open(buffer,'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(8000);w.writeframes(b'\0'*14400000)
recording=buffer.getvalue();results=[]
def media(route):
 body=recording;headers={'Accept-Ranges':'bytes','Access-Control-Allow-Origin':'*'};status=200;value=route.request.headers.get('range','')
 if value.startswith('bytes='):
  first,last=value[6:].split('-',1);start=int(first or 0);end=min(int(last) if last else len(body)-1,start+65535,len(body)-1);headers['Content-Range']=f'bytes {start}-{end}/{len(body)}';body=body[start:end+1];status=206
 headers['Content-Length']=str(len(body));route.fulfill(status=status,content_type='audio/wav',body=body,headers=headers)
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
  for width,height in [(320,740),(390,844),(593,1000),(1440,1000)]:
   for lang in ['ar','en']:
    page=browser.new_page(viewport={'width':width,'height':height},service_workers='block',reduced_motion='reduce');errors=[];sources=[];page.on('pageerror',lambda e:errors.append(str(e)));page.route('https://**/*.mp3',media);page.on('request',lambda r:sources.append(r.url) if r.url.endswith('.mp3') else None)
    page.add_init_script("""if(!localStorage.getItem('qa-seeded')){localStorage.setItem('salati',JSON.stringify({lang:'%s',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',method:'Oman',locationSet:true,locationMode:'manual'}));localStorage.setItem('salati-quran',JSON.stringify({page:564,activeSurah:68,reciter:'afasy',bookmark:121,repeat:false,autoNext:false,follow:false,layoutVersion:2,size:26}));localStorage.setItem('qa-seeded','yes')}"""%lang)
    page.goto(f'http://127.0.0.1:{server.server_port}/');page.evaluate('document.fonts.ready')
    for tab in ['times','qibla','dhikr','tasbih','settings','mushaf']:
     page.locator(f'[data-tab="{tab}"]').click();assert page.locator('#'+tab).is_visible();assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');page.screenshot(path=str(out/f'{width}-{lang}-{tab}.png'))
    page.wait_for_selector('[data-reading-page="1"].original-printed-page');assert page.locator('#qSurah').input_value()=='1'
    page.locator('#qSurah').evaluate("e=>{e.value='68';e.dispatchEvent(new Event('change',{bubbles:true}))}")
    page.wait_for_selector('[data-reading-page="564"].original-printed-page');assert page.locator('#verseActions,#verseReciterMenu').count()==0
    assert page.locator('#qTrackTitle').inner_text()==('سورة القلم' if lang=='ar' else 'Surah Al-Qalam')
    assert page.locator('#qTrackTitle').evaluate('(e)=>getComputedStyle(e).color')=='rgb(255, 255, 255)'
    q=page.locator('#qVerses').bounding_box();dock=page.locator('#mushafPlayerSlot').bounding_box();assert q['x']==0 and q['width']==width;assert q['y']+q['height']<=dock['y']+1;assert dock['y']+dock['height']<=height
    if width<=760:assert dock['y']+dock['height']<=page.locator('.site-nav').bounding_box()['y']+1
    # Exact original word location in p564. SVG multi-line bounding-box centers
    # can belong to another ayah, so use this native-image coordinate instead.
    # A deliberate Qalam choice scrolls to its mid-page first verse. Settle
    # that real animation before scrolling up to Mulk27 for the pointer test.
    # A no-op scrollTo(0) before the animation starts does not always cancel it.
    stable='e=>new Promise(resolve=>{let last=NaN,steady=0;const frame=()=>{const y=e.scrollTop;steady=Math.abs(y-last)<.01?steady+1:0;last=y;if(steady>=4)resolve();else requestAnimationFrame(frame)};requestAnimationFrame(frame)})'
    page.locator('#qVerses').evaluate(stable)
    page.locator('#qVerses').evaluate("e=>e.scrollTo({top:0,behavior:'instant'})")
    page.locator('#qVerses').evaluate(stable)
    image=page.locator('[data-reading-page="564"] .printed-page-image');box=image.bounding_box();x=box['x']+box['width']*650/1352;y=box['y']+box['height']*110/2170
    hit=page.evaluate('([x,y])=>document.elementFromPoint(x,y)?.closest("[data-ayah]")?.dataset.ayah',[x,y])
    if hit!='67:27':page.screenshot(path=str(out/f'{width}-{lang}-pointer-failure.png'))
    assert hit=='67:27',(width,lang,'pointer must reach the verified original Mulk27 coordinates',hit,box)
    page.mouse.click(x,y)
    page.wait_for_function('document.querySelector("#qAudio").currentSrc.endsWith("/067.mp3")&&!document.querySelector("#qAudio").paused&&document.querySelector("#qAudio").currentTime>=384.234')
    assert page.locator('[data-ayah="67:27"].is-selected').count()==1;assert page.locator('#qDuration').inner_text()=='15:00';assert 'كاملة' not in page.locator('.recitation-caption').inner_text();assert 'المصحف الشريف' not in page.locator('.recitation-caption').inner_text()
    assert page.locator('#qTrackTitle').inner_text()==('سورة الملك' if lang=='ar' else 'Surah Al-Mulk')
    assert page.locator('#qTransport').evaluate('(e)=>getComputedStyle(e,"::before").backgroundColor')=='rgb(37, 99, 235)'
    src=page.locator('#qAudio').evaluate('(e)=>e.currentSrc');page.locator('#qAudio').evaluate('(e)=>{e.currentTime=402;e.dispatchEvent(new Event("timeupdate"))}')
    page.wait_for_selector('[data-ayah="67:28"].is-reciting');page.screenshot(path=str(out/f'{width}-{lang}-playing.png'));assert page.locator('#qAudio').evaluate('(e)=>e.currentSrc')==src;assert page.locator('#qDuration').inner_text()=='15:00';assert not any('everyayah.com' in s for s in sources)
    page.locator('#qTransport').click();assert page.locator('#qAudio').evaluate('(e)=>e.paused');page.locator('#qTransport').click();page.wait_for_function('!document.querySelector("#qAudio").paused')
    page.locator('#qSeek').evaluate('(e)=>{e.value=0;e.dispatchEvent(new Event("input"))}');assert page.locator('#qAudio').evaluate('(e)=>e.currentTime')<2
    # Keyboard path uses the same direct action and preserves full media duration.
    page.locator('[data-ayah="68:1"]').press('Enter');page.wait_for_function('document.querySelector("#qAudio").currentSrc.endsWith("/068.mp3")&&!document.querySelector("#qAudio").paused');page.wait_for_function('document.querySelector("#qDuration").textContent==="15:00"');assert page.locator('#qDuration').inner_text()=='15:00'
    page.locator('#qStop').click();assert page.locator('#qAudio').evaluate('(e)=>e.paused');assert page.locator('#qStop').is_disabled()
    page.locator('.printed-reader-header button').first.click();assert page.locator('#qReaderOptions').is_visible();assert page.locator('#qReciter option').count()==5
    page.locator('#qReciterPickerOpen').click();page.locator('#choiceList [data-value="qatami"]').click();page.locator('#qReaderOptions>button').click();page.reload();page.locator('[data-tab="mushaf"]').click();page.wait_for_selector('.original-printed-page');assert page.locator('#qReciter').input_value()=='qatami';assert page.evaluate("JSON.parse(localStorage.getItem('salati-quran')).bookmark")==120
    # Natural vertical scrolling loads the next original page without flipping.
    before=page.locator('#qVerses').evaluate('(e)=>e.scrollTop');page.locator('#qVerses').evaluate('(e)=>e.scrollTop=e.scrollHeight');page.wait_for_function('document.querySelectorAll(".original-printed-page").length>=2');assert page.locator('#qVerses').evaluate('(e)=>e.scrollTop')>before
    page.screenshot(path=str(out/f'{width}-{lang}-mushaf.png'));assert not errors,errors
    results.append({'width':width,'height':height,'language':lang,'result':'PASS','single_surah_source':src,'duration':'15:00 (fixture)','physical_device':False});page.close()
  browser.close()
 (out/'result.json').write_text(json.dumps({'result':'PASS','cases':results,'audio_fixture':'900-second silent range-enabled WAV; not a human listening test','physical_device':'NOT RUN'},ensure_ascii=False,indent=2)+'\n')
finally:server.shutdown()
print('PASS integrated Mushaf1441: 8 responsive/language cases, 6 tabs, direct mouse/keyboard ayah starts, continuous full-surah duration, controls, options, persistence and unobscured vertical reader')
