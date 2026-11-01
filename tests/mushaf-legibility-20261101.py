"""Mushaf authenticity, legibility, adhkar, voice and footer acceptance."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
out=root/'reports/mushaf-acceptance'
out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')))
Thread(target=server.serve_forever,daemon=True).start()
try:
  with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    for width in (390,1440):
      page=browser.new_page(viewport={'width':width,'height':940},service_workers='block')
      page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual'}))")
      errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
      response=page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
      assert response.ok and page.locator('body.dark').count()
      assert page.locator('link[href="mushaf-legibility-20261101.css"]').count()==1
      assert page.locator('script[src="quran-mushaf-markers-20261101.js"]').count()==1
      assert not page.get_by_text('تُشغَّل عبارة «الصلاة خير من النوم» مرة واحدة',exact=False).count()
      page.click('[data-tab=mushaf]')
      page.wait_for_function("document.querySelector('#qVerses .ayah-number[data-mushaf-ornament]')")
      title=page.locator('#qVerses .quran-surah-title').first
      head=title.evaluate("""e=>({background:getComputedStyle(e).backgroundImage,
        border:getComputedStyle(e).borderTopWidth,
        before:getComputedStyle(e,'::before').display})""")
      assert 'quran-surah-ornament.svg' in head['background'] and head['border']=='0px' and head['before']=='none',(width,'surah ornament',head)
      mark=page.locator('#qVerses .ayah-number').first
      # Quran pages use content-visibility:auto to avoid rendering 604 pages.
      # Scroll into a real reading viewport before checking rendered text.
      mark.scroll_into_view_if_needed()
      mark.wait_for(state='visible')
      number=mark.inner_text().strip()
      style=mark.evaluate("""e=>({background:getComputedStyle(e).backgroundImage,
        color:getComputedStyle(e).color,border:getComputedStyle(e).borderTopWidth})""")
      assert number and all(c in '٠١٢٣٤٥٦٧٨٩' for c in number),(width,'ayah number',number)
      assert 'quran-ayah-rosette.svg' in style['background'] and style['border']=='0px',(width,'rosette',style)
      page_number=page.locator('#qVerses .reading-page-number').first
      page_number.scroll_into_view_if_needed()
      page_number.wait_for(state='visible')
      no=page_number.inner_text().strip()
      page_style=page_number.evaluate("""e=>({color:getComputedStyle(e).color,
        font:getComputedStyle(e).fontSize,border:getComputedStyle(e).borderTopWidth,
        before:getComputedStyle(e,'::before').content})""")
      assert no and all(c in '٠١٢٣٤٥٦٧٨٩' for c in no),(width,'printed folio',no)
      assert page_style['font'] in ('17px','18px') and page_style['border']=='1px' and page_style['before']!='"none"',(width,page_style)
      page.locator('#qSheet').screenshot(path=str(out/f'quran-{width}.png'))
      assert page.locator('#mushaf .mushaf-heading .eyebrow').evaluate('e=>getComputedStyle(e).color')=='rgb(255, 255, 255)'
      page.click('[data-tab=times]')
      active=page.locator('#times #prayers .prayer.active')
      active.wait_for(state='visible',timeout=10000)
      frame=active.evaluate("""e=>({border:getComputedStyle(e).borderTopColor,
         shadow:getComputedStyle(e).boxShadow})""")
      assert frame['border']=='rgb(142, 167, 195)' and '255, 255, 255' in frame['shadow'],(width,'rounded blue-slate reference prayer frame',frame)
      instruction=page.get_by_text('المواقيت محسوبة فلكيًا.',exact=False).first
      assert instruction.evaluate('e=>getComputedStyle(e).color')=='rgb(255, 255, 255)'
      page.click('[data-tab=settings]')
      assert page.get_by_text('غيّر وقت الصلاة بزرّي',exact=False).first.evaluate('e=>getComputedStyle(e).color')=='rgb(255, 255, 255)'
      page.locator('#audioVoice').evaluate("""e=>{e.value='nufais';e.dispatchEvent(new Event('change',{bubbles:true}))}""")
      page.click('#voicePickerOpen')
      selected=page.locator('#voicePickerList [data-voice-option=nufais]')
      assert selected.get_attribute('aria-pressed')=='true'
      assert selected.locator('.voice-symbol').evaluate("e=>getComputedStyle(e).display")=='grid'
      assert page.locator('#voicePickerList .voice-check').count()==4
      assert selected.locator('.voice-check').evaluate("e=>getComputedStyle(e).display")=='flex'
      assert page.locator('#voicePickerList .voice-check').evaluate_all("es=>es.filter(e=>getComputedStyle(e).display!=='none').length")==1
      assert selected.locator('.voice-symbol svg').evaluate("e=>getComputedStyle(e).display")!='none'
      page.screenshot(path=str(out/f'voice-{width}.png'))
      page.click('#voicePickerClose')
      page.click('[data-tab=dhikr]')
      page.wait_for_function("document.querySelectorAll('.adhkar-card').length>=1")
      assert page.locator('#adhkarCount').evaluate("e=>getComputedStyle(e).color")=='rgb(255, 255, 255)'
      for selector in ['.adhkar-card h3','.adhkar-text','.adhkar-note','.adhkar-repeat','.adhkar-source summary','.adhkar-actions button']:
        node=page.locator(selector).first
        if node.count():
          assert node.evaluate('e=>getComputedStyle(e).color')=='rgb(255, 255, 255)',(width,selector)
      page.locator('.adhkar-card').first.screenshot(path=str(out/f'adhkar-{width}.png'))
      footer=page.locator('main>footer')
      assert footer.evaluate('e=>getComputedStyle(e).justifyContent')=='center'
      if width<=600:
        assert footer.evaluate("e=>parseFloat(getComputedStyle(e).paddingBottom)")<=24
      assert footer.locator('#privacy').is_visible()
      footer.screenshot(path=str(out/f'footer-{width}.png'))
      for tab in ['times','mushaf','qibla','dhikr','tasbih','settings']:
        page.click(f'[data-tab={tab}]')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,tab,'overflow')
      assert not errors,(width,'errors',errors)
      page.close()
    browser.close()
  print('PASS: ornate surahs/ayahs/folios, neutral prayer border, notes, one voice check, adhkar, footer at 390/1440')
finally:
  server.shutdown()
