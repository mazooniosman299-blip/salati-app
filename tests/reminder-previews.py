"""Exercise real browser audio decoding, preview buttons and offline cached clips."""
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import functools,threading,json
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(root/'dist')))
threading.Thread(target=server.serve_forever,daemon=True).start()
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 context=browser.new_context(viewport={'width':390,'height':844})
 context.add_init_script("localStorage.setItem('salati',JSON.stringify({lat:24.7136,lon:46.6753,zone:'Asia/Riyadh',name:'الرياض',locationSet:true,locationMode:'manual',audio:{enabled:false,volume:1}}));")
 page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 base=f'http://127.0.0.1:{server.server_port}/'
 page.goto(base,wait_until='domcontentloaded');page.locator('[data-tab="settings"]').click()
 assert page.locator('#nativeSpeechSettings').count()==0
 for button in ['previewApproach','previewFajrPhrase']:
  page.locator('#'+button).click()
  try:page.wait_for_function("document.getElementById('announcementStatus').textContent.includes('جارٍ تشغيل')",timeout=8000)
  except Exception:
   print('PREVIEW DEBUG',button,page.locator('#announcementStatus').text_content(),errors);raise
  page.wait_for_function("document.getElementById('announcementStatus').textContent.includes('انتهى')",timeout=8000)
 # Install and take control before testing offline; this tests the actual service-worker fetch path.
 page.evaluate("async()=>{await navigator.serviceWorker.ready;if(!navigator.serviceWorker.controller)await new Promise(resolve=>navigator.serviceWorker.addEventListener('controllerchange',resolve,{once:true}));}")
 context.set_offline(True)
 for filename in ['approach-fajr','approach-dhuhr','approach-asr','approach-maghrib','approach-isha','fajr-phrase']:
  assert page.evaluate("async name=>{const response=await fetch('audio/reminders/'+name+'.mp3');return response.ok&&(await response.arrayBuffer()).byteLength>1000}",filename)
 page.locator('#previewFajrPhrase').click()
 page.wait_for_function("document.getElementById('announcementStatus').textContent.includes('انتهى')",timeout=8000)
 assert not errors,errors
 (root/'reports/ui-modern/reminder-previews.json').write_text(json.dumps({'result':'PASS','real_browser_previews':2,'offline_cached_clips':6,'offline_fajr_preview':True,'page_errors':errors},indent=2)+'\n')
 browser.close()
server.shutdown()
print('PASS: both real reminder previews finish, all six clips served offline, offline Fajr preview completes without installed speech voices.')
