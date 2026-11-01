"""Prove prayer-time location never leaves the device during real browser operations."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args): pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')))
Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  for width in [390,1440]:
   page=browser.new_page(viewport={'width':width,'height':844},service_workers='block')
   outbound=[]
   page.on('request',lambda request: outbound.append(request.url) if request.url.startswith('https://api.aladhan.com/') else None)
   page.add_init_script("""localStorage.setItem('salati', JSON.stringify({lat:23.588,lon:58.3829,zone:'Asia/Muscat',method:'Oman',madhab:'Shafi',lang:'ar',locationSet:true,locationMode:'manual',name:'مسقط'}));
   localStorage.setItem('salati-prayer-calendars-v1',JSON.stringify({'old-private-coordinates':'stale'}));""")
   response=page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
   assert response and response.ok
   page.wait_for_function("document.querySelector('#prayers .prayer')?.textContent?.trim().length>1")
   assert page.locator('#prayers .prayer').count()>=5
   assert page.evaluate("localStorage.getItem('salati-prayer-calendars-v1')") is None, 'Previous precise-coordinate cache must be removed'
   page.reload(wait_until='domcontentloaded')
   page.wait_for_timeout(1200)
   page.click('[data-tab=times]')
   assert not outbound, ('Exact coordinates sent to external provider',outbound)
   assert page.locator('#prayers .prayer').count()>=5
   page.close()
  browser.close()
 print('PASS: local browser prayer times at mobile/desktop, old GPS cache removed, zero AlAdhan requests')
finally:
 server.shutdown()
