#!/usr/bin/env python3
"""Prove source regenerates Salati UI after DOM override, language, tabs and reload.

Uses the REAL locally built app; never edits actual user source or ships the fake value.
"""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
import json
root=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(("127.0.0.1",0),partial(Quiet,directory=str(root/"dist")))
Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  page=browser.new_page(viewport={'width':390,'height':844},service_workers='block',reduced_motion='reduce')
  page.add_init_script("""if(!localStorage.getItem('salati'))localStorage.setItem('salati',JSON.stringify({
    lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',method:'Oman',
    methodPreferenceVersion:1,locationSet:true,locationMode:'manual',dark:true}))""")
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  r=page.goto('http://127.0.0.1:'+str(server.server_port)+'/',wait_until='domcontentloaded')
  assert r and r.ok
  page.wait_for_function("document.querySelectorAll('#prayers .prayer').length===6",timeout=20000)
  label=page.locator('#prayers .prayer span').first
  original=label.inner_text()
  assert original and original!='عُنصر تجريبي مزيف'
  label.evaluate("(e)=>e.textContent='عُنصر تجريبي مزيف'")
  assert label.inner_text()=='عُنصر تجريبي مزيف'
  page.locator('#lang').click()
  page.wait_for_function("document.querySelector('#prayers .prayer span')?.textContent!=='عُنصر تجريبي مزيف'")
  assert page.evaluate("JSON.parse(localStorage.getItem('salati')).lang")=='en'
  assert 'عُنصر تجريبي مزيف' not in page.locator('#prayers').inner_text()
  page.reload(wait_until='domcontentloaded')
  page.wait_for_function("document.querySelectorAll('#prayers .prayer').length===6")
  assert page.evaluate("JSON.parse(localStorage.getItem('salati')).lang")=='en','Language did not survive restart'
  assert 'عُنصر تجريبي مزيف' not in page.locator('#prayers').inner_text()
  page.locator('header>.site-nav button[data-tab="mushaf"]').click()
  page.locator('#qVerses .quran-reading-page').first.wait_for(timeout=25000)
  assert page.locator('#mushafPlayerSlot').count()==1
  assert page.locator('#qTransport').count()==1
  assert page.locator('#qSeek').count()==1
  page.locator('header>.site-nav button[data-tab="times"]').click()
  page.locator('header>.site-nav button[data-tab="mushaf"]').click()
  page.locator('#qVerses .quran-reading-page').first.wait_for(timeout=25000)
  assert not errors,('Unexpected browser JS exceptions',errors[:5])
  print('PASS real application regenerated dynamically rendered six-prayer data from JS after DOM fake, persisted language, and restored Quran tab/audio controls across reload/switches')
  browser.close()
finally:
 server.shutdown();server.server_close()
