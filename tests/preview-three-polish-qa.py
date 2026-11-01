#!/usr/bin/env python3
"""No-deploy screenshot regression: actual Salati site / preview APK web assets.
Verifies 3 requested improvements at 320-480 CSS px, incl clipped seek/timer.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright
import xml.etree.ElementTree as ET

root=Path(__file__).resolve().parents[1]
out=root/'reports/three-polish-20261101'
out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')))
Thread(target=srv.serve_forever,daemon=True).start()
try:
 # Native widget: five available home-screen columns; no crop inside its bounds.
 info=ET.parse(root/'android/app/src/main/res/xml/prayer_widget_info.xml').getroot()
 attrs=info.attrib
 a='{http://schemas.android.com/apk/res/android}'
 assert attrs[a+'targetCellWidth']=='5', 'Full-width native widget request must use five launcher columns'
 assert attrs[a+'resizeMode']=='horizontal|vertical', 'Launcher must allow manual width adjustment'
 layout=(root/'android/app/src/main/res/layout/prayer_widget.xml').read_text()
 assert 'android:id="@+id/widget_root" android:layout_width="match_parent"' in layout
 assert 'android:id="@+id/widget_scenery" android:layout_width="match_parent"' in layout
 assert 'android:scaleType="centerCrop"' in layout
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for width,height in ((320,740),(360,780),(390,844),(412,915),(480,900)):
   page=browser.new_page(viewport={'width':width,'height':height},service_workers='block')
   errors=[]
   page.on('pageerror',lambda exc:errors.append(str(exc)))
   page.add_init_script("""localStorage.setItem('salati',JSON.stringify({lat:23.588,lon:58.3829,zone:'Asia/Muscat',method:'Oman',madhab:'Shafi',name:'مسقط',locationSet:true,locationMode:'manual',lang:'ar'}))""")
   r=page.goto('http://127.0.0.1:%s/'%srv.server_port,wait_until='domcontentloaded')
   assert r and r.ok,(width,'site load')
   page.wait_for_function("document.querySelectorAll('#prayers .prayer').length === 6")
   prayer=page.locator('#prayers .prayer').evaluate_all("""es=>es.map(e=>{
    const b=e.getBoundingClientRect(), name=e.querySelector('span'), time=e.querySelector('strong');
    return {x:b.left,r:b.right,y:b.top,btm:b.bottom,label:name.textContent,
    fontsize:parseFloat(getComputedStyle(name).fontSize),timeFont:parseFloat(getComputedStyle(time).fontSize),
    labelWidth:name.scrollWidth,labelClient:name.clientWidth,
    clockWidth:time.scrollWidth,clockClient:time.clientWidth};
   })""")
   assert len(prayer)==6,(width,'six prayers')
   assert len({round(c['y']) for c in prayer})==1,(width,'single row',prayer)
   assert all(c['x']>=-1 and c['r']<=width+1 for c in prayer),(width,'prayer card cut off',prayer)
   assert all(c['fontsize']>=11 and c['timeFont']>=12 for c in prayer),(width,'font still too small',prayer)
   assert all(c['labelWidth']<=c['labelClient']+2 for c in prayer),(width,'cropped prayer name',prayer)
   assert all(c['clockWidth']<=c['clockClient']+2 for c in prayer),(width,'cropped clock',prayer)
   overview=page.locator('#times .prayer-overview').evaluate("e=>e.getBoundingClientRect().bottom")
   assert overview-prayer[0]['btm']>=-2 and overview-prayer[0]['btm']<=17,(width,'prayer row must sit low in widget',overview,prayer)
   page.screenshot(path=str(out/f'prayers-{width}.png'))
   page.locator('[data-tab=mushaf]').click()
   page.wait_for_function("document.querySelector('#qVerses')?.textContent?.trim().length>35",timeout=20000)
   rect=page.evaluate("""()=>{
    const ids=['mushafPlayerSlot','qStop','qTransport','qSeek','qElapsed','qDuration'];
    const all={};
    for(const id of ids){
     const e=document.getElementById(id),r=e.getBoundingClientRect();
     all[id]={l:r.left,t:r.top,r:r.right,b:r.bottom,w:r.width,h:r.height};
    }
    const timeline=document.querySelector('#mushafPlayerSlot .recitation-timeline');
    all.display=getComputedStyle(timeline).display;
    all.nav=document.querySelector('header>.site-nav').getBoundingClientRect().top;
    return all;
   }""")
   slot=rect['mushafPlayerSlot']
   assert rect['display']=='flex',(width,'timeline contents causes clipped controls',rect)
   assert slot['l']>=0 and slot['r']<=width+1,(width,'player outside phone',rect)
   assert slot['b']<=rect['nav']+2,(width,'player overlaps app nav',rect)
   for id in ('qStop','qTransport','qSeek','qElapsed','qDuration'):
    r=rect[id]
    assert r['w']>0 and r['h']>0,(width,id,'invisible',rect)
    assert r['l']>=slot['l']-1 and r['r']<=slot['r']+1,(width,id,'clipped sideways',rect)
    assert r['t']>=slot['t']-1 and r['b']<=slot['b']+1,(width,id,'clipped vertically',rect)
   assert rect['qSeek']['w']>=50,(width,'seek track was crushed',rect)
   assert rect['qStop']['r']+2<=rect['qTransport']['l'],(width,'buttons overlap',rect)
   assert rect['qTransport']['r']+2<=rect['qSeek']['l'],(width,'buttons cover seek track',rect)
   page.screenshot(path=str(out/f'player-{width}.png'))
   assert not errors,(width,'javascript errors',errors)
   page.close()
   print('PASS',width,'legible lower prayer row, player buttons/timeline fully visible, 5-column native widget manifest')
  browser.close()
finally:
 srv.shutdown()
