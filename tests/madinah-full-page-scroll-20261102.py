#!/usr/bin/env python3
"""Browser test: real continuous pages, no independent Quran viewport or clipping."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
out=root/'reports/madinah-full-page-scroll-20261102';out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')))
Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  b=p.chromium.launch(headless=True,args=['--no-sandbox'])
  for width in (390,760,1280):
   page=b.new_page(viewport={'width':width,'height':850},service_workers='block')
   page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
   page.locator('button[data-tab="mushaf"]').click()
   first=page.locator('#qVerses .quran-reading-page').first
   first.wait_for(timeout=30000)
   state=page.evaluate("""() => {
     const container=document.querySelector('#qVerses'),
       page=container.querySelector('.quran-reading-page'),
       css=getComputedStyle(container),pc=getComputedStyle(page),
       verse=getComputedStyle(page.querySelector('.quran-text')),
       shell=document.querySelector('#qSheet');
     return {height:css.height,scroll:css.overflowY,client:container.clientHeight,
       total:container.scrollHeight,card:pc.borderRadius,frame:pc.outlineStyle,
       pageHeight:page.getBoundingClientRect().height, font:verse.fontFamily,
       top:page.getBoundingClientRect().top,sheetOverflow:getComputedStyle(shell).overflowY,
       windowHeight:window.innerHeight};}""")
   assert state['scroll']=='visible' and state['sheetOverflow']=='visible', (width,state)
   assert state['font'].startswith('SalatiMadinahClassic'),(width,state)
   assert state['pageHeight']>250,(width,state)
   # SVG artwork must load as the DEFAULT print page when online. It is
   # the exact printed plate, not just our Medina-like font fallback.
   plate=page.locator('#qVerses .quran-reading-page .quran-madinah-plate').first
   assert plate.count()==1,(width,'original printed SVG element absent')
   assert '/hafs-kfqc/' in plate.get_attribute('src'),(width,'wrong Mushaf edition')
   try:
    page.wait_for_function("() => !!document.querySelector('#qVerses .quran-print-plate-ready')",timeout=20000)
   except Exception:
    raise AssertionError((width,'KFQC original page did not load. Keep preview unapproved, do not deploy'))
   assert plate.evaluate("e=>e.complete&&e.naturalWidth>0"),(width,'authentic plate image missing')
   state=page.evaluate("""() => {
     const c=document.querySelector('#qVerses .quran-reading-page'),
       s=getComputedStyle(c),a=c.querySelector('.quran-madinah-plate'),i=getComputedStyle(a);
     return {border:s.borderStyle,outline:s.outlineStyle,card:s.borderRadius,art:i.display,
       fallback:getComputedStyle(c.querySelector('.quran-page-interactive-fallback')).display}}""")
   assert state['art']=='block' and state['fallback']=='none' and state['border']=='none',(width,state)
   # Tapping the plate reveals selectable offline verse text; users can
   # return to the original plate using the provided control.
   plate.click()
   assert page.locator('#qVerses .quran-reading-page').first.evaluate("e=>e.classList.contains('quran-plate-text-mode')")
   page.locator('#qVerses .quran-back-to-print').first.click()
   assert not page.locator('#qVerses .quran-reading-page').first.evaluate("e=>e.classList.contains('quran-plate-text-mode')")
   assert not page.locator('.mushaf-pagination button').count()
   # Document/main scrolling must reach the next dynamically appended page.
   page.evaluate("""() => {document.querySelector('#mushaf').scrollIntoView();window.scrollBy(0,1200);
     const main=document.querySelector('main');if(main)main.scrollTop+=1500;}""")
   page.wait_for_function("() => document.querySelectorAll('#qVerses .quran-reading-page').length>=2",timeout=12000)
   page.screenshot(path=str(out/f'madinah-{width}.png'),full_page=False)
   print('PASS:',width,'full-page visible flow, Medina Hafs font, ornamental frame, auto append')
   page.close()
  b.close()
finally:
 server.shutdown();server.server_close()
