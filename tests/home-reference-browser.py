"""Actual home reference layout, scoped white labels and unchanged native widget.

Reference455x457 is the user inline screenshot; existing mosque is an explicit
user-approved exception. Geometry is verified here, not claimed pixel equality.
"""
from pathlib import Path
from functools import partial
from threading import Thread
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright
import json, subprocess, os

root=Path(__file__).resolve().parents[1]
out=root/'reports/home-reference';out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')))
Thread(target=server.serve_forever,daemon=True).start()
results=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  for width,height in [(320,740),(390,844),(455,900),(768,1024),(1440,900)]:
   for lang in ['ar','en']:
    page=browser.new_page(viewport={'width':width,'height':height},service_workers='block',reduced_motion='reduce')
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.clock.set_fixed_time(datetime(2026,11,4,0,0,tzinfo=timezone.utc))
    page.add_init_script("if(!localStorage.getItem('salati'))localStorage.setItem('salati',JSON.stringify({lang:%s,lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط، عُمان',locationSet:true,locationMode:'manual',method:'Oman'}))"%json.dumps(lang))
    page.goto(f'http://127.0.0.1:{server.server_port}/');page.wait_for_selector('#prayers .prayer')
    page.evaluate('document.fonts.ready')
    def home():
     data=page.locator('#prayers .prayer').evaluate_all("""es=>es.map(e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return {key:e.dataset.prayer,x:r.x,y:r.y,w:r.width,h:r.height,radius:s.borderRadius,bg:s.backgroundColor,color:s.color,icon:e.querySelector('img').getBoundingClientRect().width,active:e.classList.contains('active'),time:e.querySelector('strong').textContent}})""")
     assert [e['key'] for e in data]==['fajr','sunrise','dhuhr','asr','maghrib','isha'],data
     assert len({round(e['y']) for e in data})==2,data
     assert len({round(e['x']) for e in data})==3,data
     for row in [data[:3],data[3:]]:assert row[0]['x']>row[1]['x']>row[2]['x'],row
     assert len([e for e in data if e['active']])==1,data
     assert all(e['radius']=='12px' and e['icon']==22 and e['color']=='rgb(255, 255, 255)' for e in data),data
     assert all(e['bg']==('rgb(41, 47, 57)' if e['active'] else 'rgb(21, 26, 34)') for e in data),data
     assert all('ص' not in e['time'] for e in data) if lang=='ar' else all(e['time'].endswith(('AM','PM')) for e in data),data
     edges=page.locator('.home-next>*').evaluate_all("es=>es.map(e=>{const r=document.createRange();r.selectNodeContents(e);return r.getBoundingClientRect().right})")
     assert max(edges)-min(edges)<=1,(width,lang,'next label/name/time must share physical right edge',edges)
     assert page.locator('#nextName').inner_text()==('الفجر' if lang=='ar' else 'Fajr')
     assert page.locator('#nextTime').inner_text()==data[0]['time'],'Hero must show actual prayer clock, not countdown or a hardcoded mock time'
     assert page.locator('#locate').evaluate("e=>getComputedStyle(e).borderTopWidth==='0px'&&getComputedStyle(e).backgroundColor==='rgba(0, 0, 0, 0)'")
     assert page.locator('.home-mosque').get_attribute('src')=='images/mosque-reference-original.png'
     assert page.locator('.home-mosque').evaluate('e=>e.complete&&e.naturalWidth===1120')
     assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
     return data
    data=home()
    if width==455:
     box=page.locator('.home-dashboard').bounding_box()
     assert abs(box['width']-455)<1 and abs(box['height']-457)<1,box
     hero=page.locator('.home-hero').bounding_box();panel=page.locator('.home-prayer-panel').bounding_box()
     assert hero['height']==182 and panel['y']-hero['y']==206,(hero,panel)
     assert data[0]['y']-hero['y']==253 and data[3]['y']-data[0]['y']==100,data
    page.locator('.calculation-context>summary').click()
    for sel in ['#gregorianDate','#dateLabel','#countdown','#timeContext']:assert page.locator(sel).is_visible(),sel
    assert ':' in page.locator('#countdown').inner_text()
    page.locator('.calculation-context>summary').click()
    if lang=='ar' and width in [320,390,455,1440]:
     page.locator('.home-dashboard').screenshot(path=str(out/f'{width}-ar-dashboard.png'))
     page.screenshot(path=str(out/f'{width}-ar-screen.png'))
    # Colors survive actual tab creation, font loading, language and reload.
    page.locator('[data-tab=mushaf]').click();page.wait_for_selector('[data-reading-page="1"].original-printed-page')
    assert page.locator('#qTrack').is_visible()
    if width==390 and lang=='ar':page.locator('#mushafPlayerSlot').screenshot(path=str(out/'390-white-juz.png'))
    assert page.locator('#qTrack').evaluate("e=>getComputedStyle(e).color==='rgb(255, 255, 255)'")
    if width>760:page.locator('#qReaderBack').click()
    page.locator('[data-tab=qibla]').click()
    assert page.locator('#qibla .eyebrow').evaluate("e=>getComputedStyle(e).color==='rgb(255, 255, 255)'")
    if width==390 and lang=='ar':page.locator('#qibla .qibla-header').screenshot(path=str(out/'390-white-qibla.png'))
    page.locator('[data-tab=settings]').click()
    assert page.locator('#androidDownload>p').evaluate("e=>getComputedStyle(e).color==='rgb(255, 255, 255)'")
    if width==390 and lang=='ar':page.locator('#androidDownload').screenshot(path=str(out/'390-white-android.png'))
    page.locator('[data-tab=times]').click();home();page.reload();page.wait_for_selector('#prayers .prayer');home()
    page.locator('#lang').click();page.reload();page.wait_for_selector('#prayers .prayer')
    assert page.locator('#homeTimesHeading').inner_text()==('Prayer times' if lang=='ar' else 'مواقيت الصلاة')
    assert not errors,errors
    results.append({'viewport':[width,height],'language':lang,'layout':'3x2','colors':'white','reference_geometry':width==455,'result':'pass'})
    page.close()
  # Fresh/unavailable state must not show fabricated times or clip the message.
  for width in [320,455,1440]:
   page=browser.new_page(viewport={'width':width,'height':844},service_workers='block')
   page.goto(f'http://127.0.0.1:{server.server_port}/');page.wait_for_selector('#prayers .prayer')
   assert page.locator('#nextTime').is_hidden()
   assert page.locator('#prayers .prayer.active').count()==0
   assert page.locator('#prayers .prayer strong').evaluate_all("es=>es.every(e=>e.textContent==='—')")
   name=page.locator('#nextName').bounding_box();hero=page.locator('.home-hero').bounding_box()
   assert name['y']>=hero['y']+36 and name['y']+name['height']<=hero['y']+hero['height']-10,(width,name,hero)
   page.close()
  browser.close()
finally:server.shutdown();server.server_close()
# This request explicitly excludes every Android widget file, including artwork.
base=os.environ.get('SALATI_WIDGET_BASE','5eee10c6bb2839de0b4ec06afc022a3f8c4b5a31')
widget_paths=subprocess.check_output(['git','ls-tree','-r','--name-only',base,'android/app/src/main'],cwd=root,text=True).splitlines()
widget_paths=[f for f in widget_paths if 'widget' in f.lower()]
for f in widget_paths:
 assert (root/f).read_bytes()==subprocess.check_output(['git','show',base+':'+f],cwd=root),f
(out/'result.json').write_text(json.dumps({'cases':results,'empty_states':3,'unchanged_widget_files':len(widget_paths),'pixel_equality_claimed':False},ensure_ascii=False,indent=2)+'\n')
print(f'PASS home reference: {len(results)} real AR/EN responsive/reload/tab cases, 3 empty states; {len(widget_paths)} native widget files byte-identical. No automated pixel-equality claim.')
