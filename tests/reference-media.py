"""Mushaf-only media controls retain one audio owner across navigation; media output is mocked."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')));Thread(target=s.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(service_workers='block',viewport={'width':390,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.add_init_script('''localStorage.setItem('salati',JSON.stringify({lang:'ar',dark:true,lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual'}));
  Object.defineProperty(HTMLMediaElement.prototype,'paused',{get(){return this._reviewPaused!==false;}});
  Object.defineProperty(HTMLMediaElement.prototype,'currentTime',{get(){return this._reviewTime||0;},set(value){this._reviewTime=value;this.dispatchEvent(new Event('timeupdate'));}});
  Object.defineProperty(HTMLMediaElement.prototype,'duration',{get(){return 120;}});
  HTMLMediaElement.prototype.play=function(){this._reviewStarts=(this._reviewStarts||0)+1;this._reviewPaused=false;this.dispatchEvent(new Event('play'));this.dispatchEvent(new Event('playing'));return Promise.resolve();};
  HTMLMediaElement.prototype.pause=function(){this._reviewPaused=true;this.dispatchEvent(new Event('pause'));};HTMLMediaElement.prototype.load=function(){};''')
  page.goto(f'http://127.0.0.1:{s.server_port}/',wait_until='domcontentloaded');page.wait_for_selector('.nav-selection')
  assert page.locator('#homeMedia').count()==0
  assert page.locator('#times .recitation-player').count()==0
  assert page.locator('.recitation-player').count()==1
  page.click('header [data-tab=mushaf]');page.wait_for_selector('#mushaf #qTransport')
  page.wait_for_function('document.querySelector("#qTrack").textContent.includes("الجزء")')
  page.evaluate('window.originalControls=document.querySelector(".recitation-player");window.originalAudio=document.getElementById("qAudio")')
  page.click('#qTransport');page.wait_for_function('document.getElementById("qAudio").getAttribute("src")!==null')
  page.evaluate('originalAudio.currentTime=37')
  page.click('header [data-tab=times]')
  assert not page.locator('#qTransport').is_visible()
  assert page.locator('#mushaf .recitation-player').count()==1
  assert page.evaluate('originalAudio.currentTime')==37
  page.click('header [data-tab=mushaf]');page.wait_for_selector('#qTransport')
  assert page.evaluate('originalControls===document.querySelector(".recitation-player")&&originalAudio===document.getElementById("qAudio")&&originalAudio._reviewStarts===1')
  page.click('#qTransport');assert page.evaluate('originalAudio.paused')
  page.click('#qTransport');assert not page.evaluate('originalAudio.paused')
  page.click('#qStop');assert page.locator('#qAudio').get_attribute('src') is None
  for width in [320,390,760,1440]:
   page.set_viewport_size({'width':width,'height':1000})
   for dark in [True]:
    page.evaluate('(dark)=>document.body.classList.toggle("dark",dark)',dark)
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  page.locator('.reading-page-sentinel').scroll_into_view_if_needed()
  page.wait_for_selector('#qVerses [data-ayah="2:1"]')
  page.evaluate('getSelection()?.removeAllRanges()')
  page.locator('#qVerses [data-ayah="2:1"]').scroll_into_view_if_needed()
  page.wait_for_timeout(350)
  page.locator('#qVerses [data-ayah="2:1"]').press('Enter')
  page.locator('#verseReciterMenu [data-reciter=afasy]').click()
  page.wait_for_function('document.getElementById("qAudio").getAttribute("src")?.includes("Alafasy")')
  caption=page.locator('#qTrack').inner_text();credit=page.locator('#qTrack').get_attribute('title');stream=page.locator('#qAudio').get_attribute('src')
  page.click('#lang');page.click('#lang')
  assert page.locator('#qTrack').inner_text()==caption and page.locator('#qTrack').get_attribute('title')==credit,'Refresh must retain actual verse/reciter metadata rather than reading selection'
  page.click('#qTransport');page.click('#lang')
  assert 'Al-Baqara' in page.locator('#qTrack').inner_text() and 'Mishary' in page.locator('#qTrack').get_attribute('title')
  assert page.locator('#qAudio').get_attribute('src')==stream and page.evaluate('originalAudio.paused')
  failed=b.new_page(service_workers='block',viewport={'width':390,'height':844})
  failed.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',dark:true,lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual'}));")
  failed.route('**/quran/data.json',lambda route:route.abort())
  failed.goto(f'http://127.0.0.1:{s.server_port}/',wait_until='domcontentloaded')
  failed.click('header [data-tab=mushaf]')
  failed.wait_for_function('document.getElementById("qTrack").textContent.includes("أعد المحاولة")')
  assert failed.locator('#qTransport').is_disabled()
  failed.click('#lang');failed.click('#lang')
  assert 'أعد المحاولة' in failed.locator('#qTrack').inner_text(),'Theme changes must not turn a load error into endless loading'
  failed.wait_for_selector('#qRetry')
  failed.unroute('**/quran/data.json');failed.click('#qRetry')
  failed.wait_for_function('!document.getElementById("qTransport").disabled')
  failed.click('header [data-tab=times]');assert not failed.locator('#qTransport').is_visible()
  assert 'الجزء' in failed.locator('#qTrack').inner_text()
  failed.close()
  assert not errors,errors;b.close()
 print('PASS: Mushaf-only controls, no home player, dynamic surah/juz, one player and audio owner, navigation preserves playback, pause/resume/stop, permanent dark responsive layout. Media output mocked.')
finally:s.shutdown()
