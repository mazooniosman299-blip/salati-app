"""Static public pages must follow the same saved dark/light theme as the app."""
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
  for saved,dark in [('true',True),('false',True),('corrupt',True)]:
   c=b.new_context(color_scheme='light');page=c.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   page.add_init_script("localStorage.setItem('salati',"+("'{broken'" if saved=='corrupt' else "JSON.stringify({dark:"+saved+"})")+");")
   for path in ['privacy.html','ar/prayer-times/muscat.html','en/prayer-times/index.html','ar/about.html']:
    page.goto(f'http://127.0.0.1:{server.server_port}/'+path,wait_until='domcontentloaded')
    assert page.locator('body').evaluate('(e)=>e.classList.contains("dark")')==dark,(saved,path,'static page ignores saved theme')
    assert page.locator('body').evaluate('(e)=>getComputedStyle(e).color')==('rgb(255, 255, 255)' if dark else 'rgb(0, 0, 0)'),(saved,path)
   assert not errors,errors;c.close()
  b.close()
 print('PASS: privacy, city, directory and about pages remain dark regardless of saved light/dark preference and recover from malformed settings without page errors.')
finally:server.shutdown()
