"""Browser acceptance for all six user-specified Salati visual fixes."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
import json

root=Path(__file__).resolve().parents[1]
dest=root/'reports/six-visual-fixes'
dest.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')))
Thread(target=server.serve_forever,daemon=True).start()
checks=[]
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for width in [390,1440]:
            page=browser.new_page(viewport={'width':width,'height':940},service_workers='block')
            page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual'}))")
            errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            response=page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
            assert response and response.ok
            assert page.locator('link[href="six-ui-fixes-20261031.css"]').count()==1
            # 6. Active tile distinct from the other five, including on a small phone.
            nav=page.locator('header>.site-nav .nav-icon-button')
            assert nav.count()==6
            page.click('[data-tab=mushaf]')
            selected=page.locator('[data-tab=mushaf]')
            assert 'active' in selected.get_attribute('class')
            active=selected.evaluate("""e=>({shadow:getComputedStyle(e).boxShadow,
                line:getComputedStyle(e,'::after').backgroundColor,
                width:e.getBoundingClientRect().width})""")
            idle=page.locator('[data-tab=times]').evaluate("e=>getComputedStyle(e,'::after').content")
            assert 'rgba(158, 183, 152' in active['shadow'] and active['line']=='rgb(182, 203, 174)' and active['width']>36,(width,'active nav',active)
            assert idle=='none',(width,'idle nav',idle)
            page.wait_for_function("document.querySelector('#qSurah').options.length >=114")
            # 3. Quran contents, not just outer leaf, have a separate readable surface.
            panel=page.locator('#mushaf .quran-reading-page .mushaf-verses').first
            panel.wait_for(state='visible',timeout=15000)
            reading=panel.evaluate("""e=>({background:getComputedStyle(e).backgroundColor,
               border:getComputedStyle(e).borderTopWidth,color:getComputedStyle(e).color})""")
            assert reading=={'background':'rgb(32, 38, 46)','border':'1px','color':'rgb(255, 255, 255)'},(width,'Quran page',reading)
            page.locator('#qSheet').screenshot(path=str(dest/f'quran-{width}.png'))
            # 4. Qibla tick scale and directions must be high-contrast.
            page.click('[data-tab=qibla]')
            dial=page.locator('#qiblaDial').evaluate("""e=>({border:getComputedStyle(e).borderTopWidth,
              ticks:getComputedStyle(e,'::before').backgroundImage,
              cardinal:getComputedStyle(e.querySelector('.cardinal')).color})""")
            assert dial['border']=='2px' and '244, 238, 222' in dial['ticks'] and dial['cardinal']=='rgb(245, 243, 234)',(width,'qibla contrast',dial)
            page.locator('#qibla .qibla-card').screenshot(path=str(dest/f'qibla-{width}.png'))
            # 5. Search starts at the Arabic right edge.
            page.click('[data-tab=dhikr]')
            search=page.locator('#adhkarSearch').evaluate("""e=>({direction:getComputedStyle(e).direction,
                 align:getComputedStyle(e).textAlign,placeholder:getComputedStyle(e,'::placeholder').textAlign})""")
            assert search=={'direction':'rtl','align':'right','placeholder':'right'},(width,'adhkar RTL',search)
            # 1. All five adhan toggles have a centered 20px thumb, including on/off.
            page.click('[data-tab=settings]')
            switches=page.locator('#settings .prayer-switches input[data-audio-prayer]')
            assert switches.count()==5
            geometry=switches.evaluate_all("""es=>es.map(e=>{let s=getComputedStyle(e),t=getComputedStyle(e,'::after'),r=e.getBoundingClientRect();
                return {w:r.width,h:r.height,thumbW:t.width,thumbH:t.height,top:t.top,transform:t.transform}})""")
            assert all(e['w']==46 and e['h']==26 and e['thumbW']=='20px' and e['thumbH']=='20px' for e in geometry),(width,'switch geometry',geometry)
            input1=switches.first
            positions=[]
            for checked in [False,True]:
                input1.evaluate('(e,state)=>{e.checked=state}',checked)
                positions.append(input1.evaluate("e=>getComputedStyle(e,'::after').transform"))
            assert positions[0]!=positions[1] and '20' in positions[1],(width,'switch states',positions)
            page.locator('#settings .prayer-switches').screenshot(path=str(dest/f'adhan-{width}.png'))
            # 2. Current prayer uses warm muted border, not white.
            page.click('[data-tab=times]')
            cells=page.locator('#prayers .prayer')
            cells.first.wait_for(state='visible')
            if page.locator('#prayers .prayer.active').count()==0:
                cells.first.evaluate("e=>e.classList.add('active')")
            active_prayer=page.locator('#prayers .prayer.active').first.evaluate("""e=>({border:getComputedStyle(e).borderTopColor,
                shadow:getComputedStyle(e).boxShadow})""")
            assert active_prayer['border']=='rgba(151, 170, 143, 0.52)' and '255, 255, 255' not in active_prayer['shadow'],(width,'active prayer',active_prayer)
            page.locator('#times .prayer-overview').screenshot(path=str(dest/f'prayers-{width}.png'))
            for tab in ['times','mushaf','qibla','dhikr','tasbih','settings']:
                page.click(f'[data-tab={tab}]')
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),(width,tab,'overflow')
            assert not errors,(width,'page errors',errors)
            checks.append({'viewport':width,'nav':active,'quran':reading,'qibla':dial,'adhkar':search,'adhan':geometry,'active_prayer':active_prayer})
            page.close()
        browser.close()
    (dest/'results.json').write_text(json.dumps({'passed':True,'checks':checks},ensure_ascii=False,indent=2)+'\n')
    print('PASS: six fixes, RTL, 5 toggles, 6 tab navigation, and two Chromium viewports')
finally:
    server.shutdown()
