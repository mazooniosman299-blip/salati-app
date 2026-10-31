"""Regression gate for the exact six issues reported with user screenshots, across all 114 surahs."""
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from threading import Thread
import json
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
out=root/'reports/user-visual-audit-20261101'
out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
  def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')))
Thread(target=server.serve_forever,daemon=True).start()
results=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for width in (320,360,390,600,768,1440):
   page=browser.new_page(viewport={'width':width,'height':920},service_workers='block')
   page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual'}))")
   errors=[]
   page.on('pageerror',lambda e:errors.append(str(e)))
   response=page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
   assert response and response.ok
   assert page.locator('link[href="user-fixes-20261101.css"]').count()==1

   # Surah artwork: every Arabic title, even آل عمران, is ONE LINE, inside white center.
   page.click('[data-tab=mushaf]')
   page.locator('#qVerses .quran-surah-title').first.wait_for(state='visible',timeout=20000)
   page.wait_for_function('document.querySelector("#qSurah").options.length>=114')
   titles=page.evaluate("""async()=>{
      const data=await (await fetch('quran/data.json')).json();
      return data.surahs.map(s=>'سورة '+s.name);
   }""")
   assert len(titles)==114,(width,'must cover whole Quran',len(titles))
   findings=page.locator('#qVerses .quran-surah-title').first.evaluate("""(el,titles)=>{
      let bad=[],s=getComputedStyle(el),ctx=document.createElement('canvas').getContext('2d');
      const original=el.textContent;ctx.font=s.font;
      for(const text of titles){
        el.textContent=text;
        const style=getComputedStyle(el);
        const r=document.createRange();r.selectNodeContents(el);
        const rect=r.getBoundingClientRect(),box=el.getBoundingClientRect();
        const pad=parseFloat(style.paddingLeft)+parseFloat(style.paddingRight);
        const maxWidth=box.width-pad;
        const measured=ctx.measureText(text).width;
        if(style.whiteSpace!=='nowrap'||rect.height>box.height-4||rect.width>maxWidth+2||measured>maxWidth+2)
          bad.push({text,rectWidth:rect.width,rectHeight:rect.height,maxWidth,font:style.fontSize,whiteSpace:style.whiteSpace});
      }
      el.textContent=original;
      return {tested:titles.length,bad,width:el.getBoundingClientRect().width};
   }""",titles)
   assert findings['tested']==114 and not findings['bad'],(width,'surah heading clipped or wrapped',findings['bad'][:12])
   page.locator('#qVerses .quran-surah-title').first.screenshot(path=str(out/f'surah-{width}.png'))

   # Black Kiswah with gold belt and door; keep bearing algorithm unchanged.
   page.click('[data-tab=qibla]')
   fills=page.locator('#qiblaDial .kaaba-icon path').evaluate_all("es=>Object.fromEntries(es.map(e=>[e.getAttribute('class'),getComputedStyle(e).fill]))")
   assert fills['kaaba-roof']=='rgb(5, 5, 5)',(width,fills)
   assert fills['kaaba-left']=='rgb(7, 7, 7)' and fills['kaaba-right']=='rgb(16, 16, 16)',(width,fills)
   assert fills['kaaba-gold-band']=='rgb(182, 149, 78)' and fills['kaaba-door-frame']=='rgb(184, 154, 83)',(width,fills)

   page.click('[data-tab=settings]')
   # All prayer labels and current times are white; do not alter toggle switches.
   adjustment=page.locator('#settings .minute-adjustments .prayer-adjust-row')
   assert adjustment.count()>=6,(width,'adjustment rows',adjustment.count())
   colors=adjustment.evaluate_all("""es=>es.map(e=>({
    label:getComputedStyle(e.querySelector('div:first-child>span')).color,
    time:getComputedStyle(e.querySelector('div:first-child>strong')).color
   }))""")
   assert all(x['label']=='rgb(255, 255, 255)' and x['time']=='rgb(255, 255, 255)' for x in colors),(width,'white prayer labels',colors)

   # One-and-only-one check across all four reciter choices.
   page.click('#voicePickerOpen')
   for voice in ('qatami','nufais','makkah','aqsa'):
    page.evaluate("""v=>{const el=document.querySelector('#audioVoice');el.value=v;el.dispatchEvent(new Event('change',{bubbles:true}))}""",voice)
    options=page.locator('#voicePickerList .voice-option').evaluate_all("""es=>es.map(e=>({
      active:e.getAttribute('aria-pressed')==='true',
      markerDisplay:getComputedStyle(e.querySelector('.voice-check')).display,
      tick:getComputedStyle(e.querySelector('.voice-symbol'),'::after').content,
      waveform:getComputedStyle(e.querySelector('.voice-symbol svg')).display
    }))""")
    assert sum(x['active'] for x in options)==1,(width,voice,'one selected',options)
    assert sum(x['tick']=='"✓"' for x in options)==1,(width,voice,'one tick only',options)
    assert all(x['markerDisplay']=='none' for x in options),(width,voice,'no duplicate check',options)
    assert all((x['tick']=='"✓"')==x['active'] for x in options),(width,voice,'check aligned to selection',options)
    assert all((x['waveform']=='none')==x['active'] for x in options),(width,voice,'waveform not second mark',options)
   page.locator('#voicePickerList').screenshot(path=str(out/f'voices-{width}.png'))
   page.click('#voicePickerClose')

   # All country pins AND the automatic-location pin aligned to vertical midpoint.
   page.click('#locationPickerOpen')
   page.locator('#locationOptions .choice-option').first.wait_for(state='visible')
   offsets=page.locator('#locationOptions .choice-option').evaluate_all("""es=>es.map(e=>{
     const b=e.getBoundingClientRect(),r=e.querySelector('.location-icon').getBoundingClientRect();
     return {text:e.innerText.slice(0,40),offset:r.top+r.height/2-b.top-b.height/2};
   })""")
   assert len(offsets)>15,(width,'countries',len(offsets))
   bad=[x for x in offsets if abs(x['offset'])>2.5]
   assert not bad,(width,'all country pins centered',bad[:8])
   page.locator('#locationOptions').screenshot(path=str(out/f'countries-{width}.png'))
   page.keyboard.press('Escape')

   # Signed APK must download from SAME domain, not navigate to GitHub.
   href=page.locator('#androidDownload .apk-download').get_attribute('href')
   name=page.locator('#androidDownload .apk-download').get_attribute('download')
   assert href=='/downloads/salati-1.0.112.apk' and name=='salati-1.0.112.apk',(width,'same-origin APK',href,name)
   assert not errors,(width,'browser errors',errors)
   results.append({'viewport':width,'surahs':114,'countries':len(offsets),'muezzinChoices':4,
                   'whitePrayerRows':len(colors),'blackKaaba':True,'directDownload':True,'errors':0})
   page.close()
  browser.close()
 print(json.dumps({'result':'PASS','checks':results},ensure_ascii=False,indent=2))
 (out/'results.json').write_text(json.dumps({'passed':True,'checks':results},ensure_ascii=False,indent=2)+'\n')
finally:
 server.shutdown()
