"""A controlled offline Chromium navigation must return to a bootable cached shell."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from threading import Thread
from functools import partial
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')))
Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  c=b.new_context();page=c.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:24.7136,lon:46.6753,zone:'Asia/Riyadh',name:'الرياض',locationSet:true,locationMode:'manual'}));")
  url=f'http://127.0.0.1:{server.server_port}/'
  page.goto(url,wait_until='domcontentloaded')
  page.evaluate('async()=>{await navigator.serviceWorker.ready;if(!navigator.serviceWorker.controller)await new Promise(resolve=>navigator.serviceWorker.addEventListener("controllerchange",resolve,{once:true}));}')
  c.set_offline(True)
  for language in ['ar','en']:
   page.goto(url+language+'/prayer-times/never-visited-offline.html',wait_until='domcontentloaded')
   page.wait_for_selector('header .site-nav')
   page.wait_for_function('document.querySelector(".nav-selection")!==null')
   assert page.url==url,(page.url,'offline fallback must change document base through root redirect')
   assert page.locator('#cityLabel').inner_text()=='الرياض'
   page.wait_for_function('document.querySelector(".hero-picture img")?.naturalWidth===1120')
   assert page.locator('.hero-picture img').get_attribute('src')=='images/mosque-reference-original.png'
   page.click('[data-tab=mushaf]');page.wait_for_function('document.querySelector("#mushaf:not([hidden]) .mushaf-verses")?.innerText.trim().length>0')
   assert page.locator('.mushaf-verses').inner_text().strip(),'Bundled Quran data must load offline after nested navigation'
  assert not errors,errors
  b.close()
 print('PASS: real controlled Chromium resolves Arabic/English offline deep links to cached root, boots navigation and loads Quran data.')
finally:server.shutdown()
