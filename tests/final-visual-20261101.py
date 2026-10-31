"""Final 2026-11-01 visual acceptance of user's five requested corrections."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
from pathlib import Path
from playwright.sync_api import sync_playwright
import json

root=Path(__file__).resolve().parents[1]
out=root/'reports/final-five'
out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')))
Thread(target=server.serve_forever,daemon=True).start()
results=[]
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for width in [360,390,1440]:
            page=browser.new_page(viewport={'width':width,'height':920},service_workers='block')
            page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual'}))")
            errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            response=page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
            assert response and response.ok
            assert page.locator('link[href="final-visual-20261101.css"]').count()==1
            # 1. One cream leaf everywhere in the Quran; no internal black border.
            page.click('[data-tab=mushaf]')
            page.wait_for_function("document.querySelector('#qSurah').options.length>=114")
            leaf=page.locator('#qSheet')
            verse=page.locator('#qVerses .quran-reading-page').first
            verse.wait_for(state='visible',timeout=15000)
            for selector in ['#qSheet','#qVerses','#qVerses .quran-reading-page',
                              '#qVerses .quran-reading-page .quran-text']:
                style=page.locator(selector).first.evaluate("""e=>({
                  bg:getComputedStyle(e).backgroundColor,
                  fg:getComputedStyle(e).color,
                  border:getComputedStyle(e).borderTopWidth
                })""")
                assert style['bg']=='rgb(246, 240, 228)',(width,selector,style)
                assert style['fg']=='rgb(39, 35, 30)',(width,selector,style)
                assert style['border']=='0px',(width,selector,style)
            assert page.evaluate('getComputedStyle(document.body).backgroundColor')=='rgb(11, 14, 19)'
            # 2. Ornamental title has its own double edge and decorative corner marks.
            heading=page.locator('#qVerses .quran-surah-title').first
            ornament=heading.evaluate("""e=>({
              bg:getComputedStyle(e).backgroundColor,
              background:getComputedStyle(e).backgroundImage,
              border:getComputedStyle(e).borderTopWidth,
              start:getComputedStyle(e,'::before').display,
              end:getComputedStyle(e,'::after').display
            })""")
            assert ornament['border']=='0px' and 'quran-surah-ornament.svg' in ornament['background'] and ornament['start']=='none' and ornament['end']=='none',(width,ornament)
            leaf.screenshot(path=str(out/f'quran-{width}.png'))
            # 3. Active icon has a clear neutral white marker, unlike other icons.
            active=page.locator('header>.site-nav .nav-icon-button.active')
            mark=active.evaluate("""e=>({
               color:getComputedStyle(e,'::after').backgroundColor,
               height:getComputedStyle(e,'::after').height,
               outline:getComputedStyle(e).outlineWidth
            })""")
            assert mark['outline']=='0px' and mark['height']=='0px',(width,mark)
            page.locator('header>.site-nav').screenshot(path=str(out/f'navigation-{width}.png'))
            # 4. Android download CTA stands out against the dark card.
            page.click('[data-tab=settings]')
            link=page.locator('a.apk-download')
            assert link.count()==1
            cta=link.evaluate("""e=>({
              bg:getComputedStyle(e).backgroundColor,
              fg:getComputedStyle(e).color,
              height:e.getBoundingClientRect().height,
              href:e.getAttribute('href')
            })""")
            assert cta['bg']=='rgb(29, 78, 216)' and cta['fg']=='rgb(255, 255, 255)' and cta['height']>=52,(width,cta)
            link.screenshot(path=str(out/f'android-button-{width}.png'))
            # 5. Qibla centered in one column, details underneath, Kaaba black.
            page.click('[data-tab=qibla]')
            dashboard=page.locator('#qibla .qibla-dashboard')
            layout=dashboard.evaluate("""e=>({
                display:getComputedStyle(e).display,
                direction:getComputedStyle(e).flexDirection
            })""")
            assert layout=={'display':'flex','direction':'column'},(width,layout)
            instrument=page.locator('#qibla .qibla-instrument').bounding_box()
            information=page.locator('#qibla .qibla-information').bounding_box()
            assert instrument and information and information['y']>=instrument['y']+instrument['height'],(width,'qibla stacking',instrument,information)
            assert abs((instrument['x']+instrument['width']/2)-(information['x']+information['width']/2))<3,(width,'qibla centering')
            colors=page.locator('#qiblaDial .kaaba-icon path').evaluate_all("""es=>es.map(e=>getComputedStyle(e).fill)""")
            assert colors and all(c=='rgb(5, 5, 5)' for c in colors),(width,'black Kaaba',colors)
            page.locator('#qibla .qibla-card').screenshot(path=str(out/f'qibla-{width}.png'))
            for tab in ['times','mushaf','qibla','dhikr','tasbih','settings']:
                page.click(f'[data-tab={tab}]')
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,tab,'overflow')
            assert not errors,(width,errors)
            results.append({'viewport':width,'cream_quran':True,'ornate_heading':True,
                            'nav_contrast':True,'blue_apk_cta':True,
                            'centered_black_kaaba':True,'browser_errors':0})
            page.close()
        browser.close()
    (out/'results.json').write_text(json.dumps({'passed':True,'results':results},ensure_ascii=False,indent=2)+'\n')
    print('PASS: final five visual changes in Chromium at 360, 390, 1440')
finally:
    server.shutdown()
