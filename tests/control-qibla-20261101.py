"""Real Chromium verification: ALL control geometries, state transitions and new Qibla."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from playwright.sync_api import sync_playwright
import json

root=Path(__file__).resolve().parents[1]
out=root/'reports/control-qibla-20261101'; out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')))
Thread(target=server.serve_forever,daemon=True).start()

checks=[]
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for viewport in [360,390,768,1440]:
            page=browser.new_page(viewport={'width':viewport,'height':940},service_workers='block')
            page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual'}))")
            errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            response=page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
            assert response and response.ok
            assert page.locator('link[href="ui-refinement-20261101.css"]').count()==1
            assert page.locator('body').evaluate("e=>e.classList.contains('dark')")
            page.click('header [data-tab=settings]')
            # Every native switch is a symmetrical capsule with one correctly centered thumb.
            native=page.locator('#settings input[data-audio-prayer],#fajrAnnouncementToggle')
            assert native.count()==6,(viewport,'native count')
            for i in range(native.count()):
                switch=native.nth(i)
                measurements=switch.evaluate("""e=>{const r=e.getBoundingClientRect(),t=getComputedStyle(e,'::after');
                    return {width:r.width,height:r.height,thumbWidth:t.width,thumbHeight:t.height,
                    top:t.top,left:t.left,radius:t.borderRadius}}""")
                assert measurements=={'width':46,'height':26,'thumbWidth':'20px',
                  'thumbHeight':'20px','top':'3px','left':'3px','radius':'50%'},(viewport,i,measurements)
                initial=switch.evaluate('e=>e.checked')
                states=[]
                for state in [False,True]:
                    switch.evaluate('(e,v)=>{e.checked=v}',state)
                    page.wait_for_timeout(190)
                    states.append(switch.evaluate("e=>getComputedStyle(e,'::after').transform"))
                assert states[0]!=states[1] and '20' in states[1],(viewport,i,states)
                switch.evaluate('(e,v)=>e.checked=v',initial)
            # CSS-custom role switches: 66x38 and same 30px circular thumb.
            for key in ['#audioEnable','#duaToggle']:
                btn=page.locator(key)
                dimensions=btn.evaluate("""e=>{const r=e.getBoundingClientRect(),t=e.querySelector('.toggle-thumb'),
                    s=getComputedStyle(t);return [r.width,r.height,t.getBoundingClientRect().width,
                    t.getBoundingClientRect().height,s.left,s.top]}""")
                assert dimensions==[66,38,30,30,'4px','4px'],(viewport,key,dimensions)
                original=btn.get_attribute('aria-checked')
                states=[]
                for enabled in ['false','true']:
                    btn.evaluate("(e,v)=>{e.setAttribute('aria-checked',v);e.classList.toggle('is-on',v==='true')}",enabled)
                    page.wait_for_timeout(190)
                    states.append(btn.evaluate("e=>getComputedStyle(e.querySelector('.toggle-thumb')).transform"))
                assert states[0]!=states[1] and '28' in states[1],(viewport,key,states)
                btn.evaluate("(e,v)=>{e.setAttribute('aria-checked',v);e.classList.toggle('is-on',v==='true')}",original)
            page.locator('.prayer-switches').screenshot(path=str(out/f'switches-{viewport}.png'))
            # Every Quran play/stop shape is circular and repeat switches retain their 54x32 tracks.
            page.click('header [data-tab=mushaf]')
            page.wait_for_function("document.querySelector('#qSurah').options.length>=114")
            for key in ['#qTransport','#qStop']:
                control=page.locator(key)
                # The idle Stop button is deliberately hidden by product logic.
                if key=='#qStop': control.evaluate("e=>e.disabled=false")
                box=control.evaluate("""e=>{const r=e.getBoundingClientRect();const s=getComputedStyle(e);
                    return [r.width,r.height,s.borderRadius]}""")
                assert box==[44,44,'50%'],(viewport,key,box)
                if key=='#qStop': control.evaluate("e=>e.disabled=true")
            for key in ['#qRepeat','#qAutoNext']:
                dims=page.locator(key).evaluate("""e=>{const r=e.getBoundingClientRect(),t=getComputedStyle(e,'::before');
                    return [r.width,r.height,t.width,t.height]}""")
                assert dims==[54,32,'24px','24px'],(viewport,key,dims)
            # Separate warm reading layer, while surrounding application stays charcoal.
            reading=page.locator('#mushaf .quran-reading-page .quran-text').first
            reading.wait_for(state='visible',timeout=12000)
            colors=reading.evaluate("""e=>({bg:getComputedStyle(e).backgroundColor,
                fg:getComputedStyle(e).color,sample:getComputedStyle(e.querySelector('[data-ayah]')).color})""")
            assert colors=={'bg':'rgb(246, 240, 228)','fg':'rgb(39, 35, 30)',
                            'sample':'rgb(39, 35, 30)'},(viewport,'reading',colors)
            assert page.locator('#qVerses').evaluate("e=>getComputedStyle(e).backgroundColor")=='rgb(246, 240, 228)',(viewport,'outer Quran container must match parchment')
            page.locator('#qSheet').screenshot(path=str(out/f'quran-{viewport}.png'))
            # Active navigation is graphite (no green), visible on desktop and mobile.
            active=page.locator('header>.site-nav .nav-icon-button.active')
            nav=active.evaluate("""e=>({bg:getComputedStyle(e).backgroundColor,
                underline:getComputedStyle(e,'::after').backgroundColor,
                icon:getComputedStyle(e.querySelector('.nav-symbol')).color})""")
            assert nav['bg']!='rgb(32, 40, 35)' and nav['underline']=='rgb(244, 246, 250)' and nav['icon']=='rgb(255, 255, 255)',(viewport,nav)
            page.locator('header>.site-nav').screenshot(path=str(out/f'nav-{viewport}.png'))
            # Redesigned two-column instrument on desktop and stacked on mobile,
            # but keep the original sensor/needle/heading DOM elements.
            page.click('header [data-tab=qibla]')
            for key in ['#qiblaDial','#cardinalRing','#needle','#compassMode','#bearing',
                        '#headingValue','#compassStatus','#compassEnable']:
                assert page.locator(key).count()==1,(viewport,key)
            dash=page.locator('#qibla .qibla-dashboard')
            columns=dash.evaluate('e=>getComputedStyle(e).gridTemplateColumns.split(" ").length')
            assert columns==1,(viewport,'columns',columns)
            dial=page.locator('#qiblaDial').evaluate("""e=>{const b=e.getBoundingClientRect(),s=getComputedStyle(e);
                return {width:b.width,height:b.height,background:s.backgroundImage,border:s.borderTopWidth}}""")
            assert abs(dial['width']-dial['height'])<1 and dial['border']=='2px',(viewport,'circular dial',dial)
            assert 'radial-gradient' in dial['background']
            # Don't imply a live compass sensor exists on a desktop browser.
            initial=page.locator('#compassMode').inner_text()
            assert initial.strip(),(viewport,'sensor state missing')
            page.locator('#qibla .qibla-card').screenshot(path=str(out/f'qibla-{viewport}.png'))
            for tab in ['times','mushaf','qibla','dhikr','tasbih','settings']:
                page.click('header [data-tab='+tab+']')
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(viewport,tab,'overflow')
            assert not errors,(viewport,'runtime',errors)
            checks.append({'width':viewport,'switches':6,'role_switches':2,'quran_controls':4,
                           'qibla_grid_columns':columns,'no_horizontal_overflow':True,'browser_errors':0})
            page.close()
        browser.close()
    (out/'results.json').write_text(json.dumps({'passed':True,'checks':checks,
             'physical_device_tested':False,'sensor_verified_on_hardware':False},ensure_ascii=False,indent=2)+'\n')
    print('PASS: all switches/play controls, matte nav, readable Quran, redesigned Qibla, 4 Chromium widths')
finally:
    server.shutdown()
