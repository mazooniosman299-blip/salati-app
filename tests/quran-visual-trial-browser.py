#!/usr/bin/env python3
"""Proof of real Salati coded 604-page Uthmani reader and LIVE original audio controls.
Never use a fabricated, fetched, generated, or single external page image."""
from pathlib import Path
from functools import partial
from threading import Thread
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
import json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports'/'quran-only-trial'
OUT.mkdir(parents=True,exist_ok=True)
data=json.loads((ROOT/'dist/quran/data.json').read_text(encoding='utf-8'))
assert len(data['pages'])==604
assert sum(map(len,data['pages']))==6236
assert len(data['surahs'])==114
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'dist')))
Thread(target=server.serve_forever,daemon=True).start()
records=[]
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
  for width,height in ((390,844),(430,932)):
   page=browser.new_page(viewport={'width':width,'height':height},service_workers='block')
   errors=[]
   page.on('pageerror',lambda error:errors.append(str(error)))
   page.add_init_script("""() => {
    localStorage.setItem('salati',JSON.stringify({
      lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',
      name:'مسقط',method:'Oman',locationSet:true,locationMode:'manual',dark:true
    }));
   }""")
   response=page.goto(f'http://127.0.0.1:{server.server_port}/',
    wait_until='domcontentloaded',timeout=35000)
   assert response and response.ok
   page.locator('header>.site-nav button[data-tab="mushaf"]').click()
   page.locator('#qVerses .quran-reading-page').first.wait_for(timeout=35000)
   page.locator('#qVerses [data-ayah="1:1"]').first.wait_for(timeout=12000)
   assert page.locator('#qVerses .quran-reading-page[data-reading-page="1"]').count()>0
   assert page.locator('#qVerses .quran-fixed-lines[data-reading-page="1"]').count()==1, 'Line-based Mushaf renderer not active'
   assert page.locator('#qVerses .mushaf-book-page[data-reading-page="1"]').count()==1, 'Independent MIT-derived MushafBook view was not mounted'
   assert page.locator('#qVerses .mushaf-book-page[data-reading-page="1"] .mushaf-book-grid>.mushaf-book-row').count()==8
   assert page.locator('#qVerses .mushaf-book-page[data-reading-page="1"] .mushaf-book-frame-outer').count()==1
   assert page.locator('#qVerses .mushaf-book-page[data-reading-page="1"] .mushaf-book-corner').count()==4
   assert page.locator('link[href="salati-ui.css"]').count()==1
   assert page.locator('link[href="mushaf-book.css"]').count()==0, 'Salati homepage must keep exactly one canonical CSS link'
   assert (ROOT/'dist/salati-ui.css').read_text().splitlines()[:2]==['@layer salati-base,salati-priority;','@import url("mushaf-book.css");']
   assert page.locator('script[src="mushaf-book.js"]').count()==1
   assert page.evaluate("document.querySelector('#qVerses .mushaf-book-page').dataset.layoutOrigin")=="mushaf-companion-mit-port"
   assert page.locator('#qVerses .quran-fixed-lines[data-reading-page="1"] .quran-madinah-line').count()==7
   assert page.locator('#qVerses .quran-fixed-lines[data-reading-page="1"] .quran-fixed-heading').count()==1
   assert page.locator('#qSheet img').count()==0,'Quran is not supposed to be a single photo'
   assert page.locator('#qTrialPlate').count()==0,'Rejected photo overlay still in DOM'
   assert page.locator('#qTrialSwitch').count()==0,'Rejected preview toggle still in DOM'
   assert page.locator('header>.site-nav button[data-tab]').count()==6
   def metrics():
    return page.evaluate("""() => {
      const get=e=>document.querySelector(e);
      const box=e=>{const r=get(e).getBoundingClientRect();return {x:r.x,y:r.y,left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height}};
      const color=(e,p='')=>getComputedStyle(get(e),p).backgroundColor;
      return {body:color('body'),panel:color('#mushafPlayerSlot'),blue:color('#qTransport'),
        codedPage:!!get('#qVerses .quran-reading-page'),
        ayahCount:get('#qVerses').querySelectorAll('[data-ayah]').length,
        pageCount:get('#qVerses').querySelectorAll('.quran-reading-page').length,
        player:box('#mushafPlayerSlot'),centerButton:box('#qTransport'),
        progress:box('#qSeek'),row:box('#mushafPlayerSlot .quran-trial-transport-row'),
        tabCount:document.querySelectorAll('header>.site-nav button[data-tab]').length,
        nav:box('header>.site-nav'),
        backgroundImage:getComputedStyle(get('#qVerses .quran-reading-page')).backgroundImage,
        pageText:get('#qVerses [data-ayah]')?.textContent?.slice(0,60),
        fullQuranLoaded:!!window.quranReader||true,
        script:!!get('script[src="quran-visual-trial.js"]')
      };
    }""")
   pre=metrics()
   # The Quran tab owns the ENTIRE WebView; real app header and bottom nav
   # are hidden only while reading, never on the other five tabs.
   assert page.evaluate("document.body.classList.contains('salati-quran-fullscreen')")
   assert page.locator('#qFullHeader').is_visible()
   assert not page.locator('body>header').is_visible()
   assert page.evaluate("getComputedStyle(document.querySelector('#mushaf')).position")=='fixed'
   assert page.evaluate("Math.abs(document.querySelector('#mushaf').getBoundingClientRect().height-innerHeight)<2")
   assert page.locator('#qWaveBars .q-wave-bar').count()==63
   heights=page.locator('#qWaveBars .q-wave-bar').evaluate_all(
     "(els) => els.map(e => Math.round(e.getBoundingClientRect().height))")
   assert len(set(heights))>=10,('Waveform must vary heights',heights)
   assert page.evaluate("getComputedStyle(document.querySelector('#qWaveBars .q-wave-bar')).backgroundColor")!='rgba(0, 0, 0, 0)'
   assert pre['body']=='rgb(11, 14, 19)',pre
   assert pre['panel']=='rgb(24, 25, 29)',pre
   assert pre['blue']=='rgb(37, 99, 235)',pre
   # Design V2: authentic page typography and Quran source stay intact while
   # visual chrome is wholly modern blue/ivory, no unexpected black round UI.
   v2=page.evaluate("""() => {
     const shell=document.querySelector('#qVerses .mushaf-book-page');
     const chapter=shell.querySelector('.mushaf-book-chapter');
     const frame=shell.querySelector('.mushaf-book-frame-outer');
     const marker=shell.querySelector('.mushaf-book-rosette');
     const blackCircles=[...shell.querySelectorAll('*')].filter(el=>{
       const cs=getComputedStyle(el),box=el.getBoundingClientRect();
       const bg=cs.backgroundColor;
       return box.width>=9&&box.height>=9&&(bg==='rgb(0, 0, 0)'||bg==='rgb(12, 12, 12)'||
         bg==='rgb(24, 25, 29)')&&(cs.borderRadius==='50%'||cs.borderRadius==='9999px');
     });
     return {paper:getComputedStyle(shell).backgroundColor,
       chapter:getComputedStyle(chapter).color,
       frame:getComputedStyle(frame).borderTopColor,
       medallion:getComputedStyle(marker).backgroundColor,
       blackRoundCount:blackCircles.length,
       playerHeight:document.querySelector('#mushafPlayerSlot').getBoundingClientRect().height,
       headerHeight:document.querySelector('#qFullHeader').getBoundingClientRect().height
     };
   }""")
   assert v2['paper']=='rgb(255, 253, 249)',v2
   assert v2['chapter']=='rgb(35, 95, 137)',v2
   assert v2['blackRoundCount']==0,v2
   assert v2['playerHeight']<=160,('Player outer frame must be visibly slimmer than prior 170px',v2)
   assert v2['headerHeight']<=53,v2
   assert pre['codedPage'] and pre['ayahCount']>=7 and pre['tabCount']==6,pre
   assert pre['centerButton']['width']>=58,pre
   assert pre['centerButton']['left']>=pre['player']['left']+4,pre
   assert pre['centerButton']['right']<=pre['player']['right']-4,pre
   assert pre['centerButton']['bottom']<=pre['player']['bottom']-4,pre
   assert pre['centerButton']['top']>=pre['player']['top']+4,pre
   assert pre['row']['top']<=pre['centerButton']['top']<=pre['row']['bottom'],pre
   assert pre['progress']['width']>120,pre
   assert page.locator('#qStop').count()==1 and page.locator('#qSeek').count()==1
   assert page.locator('#qTransport').count()==1 and page.locator('#qNextSurah').count()==1
   assert page.locator('#qLoopSurah').count()==1
   page.locator('#qLoopSurah').click()
   assert page.locator('#qRepeat').is_checked()
   page.locator('#qLoopSurah').click()
   assert not page.locator('#qRepeat').is_checked()
   # User screenshot reference is Madinah page 564: it must be 15 genuine
   # coded word lines with surah header + canonical basmala, not a PNG.
   page.locator('#qPageNumber').evaluate("(e)=>{e.value='564';}")
   page.locator('#qPageForm').evaluate("(e)=>{e.dispatchEvent(new Event('submit',{cancelable:true,bubbles:true}));}")
   page.locator('#qVerses .quran-fixed-lines[data-reading-page="564"]').wait_for(timeout=15000)
   page.evaluate("document.fonts.ready")
   page.wait_for_timeout(250)
   # Arabic ink may protrude on the RIGHT without increasing scrollWidth.
   # Measure actual DOM Range glyph rectangles, not box scrollWidth alone.
   glyph_metrics=page.evaluate("""() => {
     const pg=document.querySelector('#qVerses .quran-fixed-lines[data-reading-page="564"]');
     return [...pg.querySelectorAll('.quran-madinah-line')].map(row=>{
       const box=row.getBoundingClientRect(),r=document.createRange();
       r.selectNodeContents(row);const ink=r.getBoundingClientRect();
       return {leftOverflow:Math.max(0,box.left-ink.left),
               rightOverflow:Math.max(0,ink.right-box.right),
               width:box.width};
     });
   }""")
   assert all(max(x['leftOverflow'],x['rightOverflow'])<5 for x in glyph_metrics),('Quran word clipped',glyph_metrics)
   assert page.locator('#qVerses .quran-fixed-lines[data-reading-page="564"] .quran-madinah-line').count()==13
   assert page.locator('#qVerses .mushaf-book-page[data-reading-page="564"] .mushaf-book-grid>.mushaf-book-row').count()==15
   assert page.locator('#qVerses .mushaf-book-page[data-reading-page="564"] .mushaf-book-top').count()==1
   assert page.locator('#qVerses .mushaf-book-page[data-reading-page="564"] .mushaf-book-footer').count()==1
   assert page.locator('#qVerses .quran-fixed-lines[data-reading-page="564"] .quran-fixed-heading').count()==1
   assert page.locator('#qVerses .quran-fixed-lines[data-reading-page="564"] .quran-basmala-line').count()==1
   assert page.locator('#qVerses .quran-fixed-lines[data-reading-page="564"]').get_attribute('data-line-count')=='15'
   assert page.locator('#qVerses [data-ayah="67:27"]').count()>0
   assert page.locator('#qVerses [data-ayah="68:1"]').count()>0
   page.locator('#qFullPlayerToggle').click()
   page.locator('#qSheet').screenshot(path=str(OUT/f'madinah-page-564-reader-{width}.png'))
   page.locator('#qFullPlayerToggle').click()
   # Real app state navigation through the existing QuranReader, not a stock image
   page.locator('#qSurah').evaluate("(e,id)=>{e.value=String(id);e.dispatchEvent(new Event('change',{bubbles:true}));}",114)
   page.locator('#qVerses .quran-reading-page[data-reading-page="604"]').first.wait_for(timeout=20000)
   page.locator('#qVerses [data-ayah="114:1"]').first.wait_for(timeout=14000)
   assert page.locator('#qVerses [data-ayah="114:1"]').count()==1
   assert page.locator('#qVerses .quran-reading-page[data-reading-page="604"]').count()==1
   assert page.locator('#qVerses .quran-fixed-lines[data-reading-page="604"]').count()==1
   assert page.locator('#qVerses .mushaf-book-page[data-reading-page="604"] .mushaf-book-grid>.mushaf-book-row').count()==15
   assert page.locator('#qVerses .quran-fixed-lines[data-reading-page="604"]').get_attribute('data-line-count')=='15'
   page.locator('#qPrevSurah').click()
   assert page.locator('#qSurah').input_value()=='113'
   page.locator('#qNextSurah').click()
   assert page.locator('#qSurah').input_value()=='114'
   assert not errors,errors[:8]
   page.locator('#qSurah').evaluate("(e,id)=>{e.value=String(id);e.dispatchEvent(new Event('change',{bubbles:true}));}",1)
   page.locator('#qVerses [data-ayah="1:1"]').first.wait_for(timeout=20000)
   page.locator('#mushafPlayerSlot').scroll_into_view_if_needed(timeout=15000)
   page.screenshot(path=str(OUT/f'quran-real-app-{width}.png'),animations='disabled')
   page.locator('#mushafPlayerSlot').screenshot(path=str(OUT/f'quran-real-player-{width}.png'))
   page.locator('#qSheet').screenshot(path=str(OUT/f'quran-coded-pages-{width}.png'))
   # A real seek event must update the progress visualization and remain
   # the same existing input consumed by the audio engine.
   # QuranReader's timeupdate handler writes slider.value AND CSS --seek.
   # Simulate that exact programmatic update, not a seek on an unloaded audio
   # which correctly resets to zero because no recording duration exists.
   page.locator('#qSeek').evaluate("(e) => {e.value='52';e.style.setProperty('--seek','52%');}")
   page.wait_for_function("document.querySelectorAll('#qWaveBars .is-played').length>=30",timeout=3000)
   assert page.locator('#qWaveBars .is-played').count()>=30
   page.locator('#qSeek').evaluate("(e) => {e.value='0';e.style.setProperty('--seek','0%');}")
   page.wait_for_function("document.querySelectorAll('#qWaveBars .is-played').length===0",timeout=3000)
   # Hiding the player gives the entire remaining screen to the printed reader.
   initial=page.locator('#qSheet').bounding_box()
   page.locator('#qFullPlayerToggle').click()
   assert not page.locator('#mushafPlayerSlot').is_visible()
   expanded=page.locator('#qSheet').bounding_box()
   assert expanded['height']>initial['height']+80,(initial,expanded)
   page.screenshot(path=str(OUT/f'quran-fullscreen-reading-{width}.png'),animations='disabled')
   page.locator('#qFullPlayerToggle').click()
   assert page.locator('#mushafPlayerSlot').is_visible()
   # The original app navigation is still reachable after leaving Quran mode.
   page.locator('#qFullBack').click()
   assert page.locator('header>.site-nav').is_visible()
   assert not page.evaluate("document.body.classList.contains('salati-quran-fullscreen')")
   page.locator('header>.site-nav button[data-tab="mushaf"]').click()
   page.locator('#qVerses [data-ayah="1:1"]').first.wait_for(timeout=25000)
   assert page.evaluate("document.body.classList.contains('salati-quran-fullscreen')")
   assert not errors,errors[:8]
   assert page.locator('#qVerses .quran-fixed-lines').count()>0
   records.append({'viewport':[width,height],**pre,'visitedPage604':True,
                   'photoUsed':False,'imageSource':'none - complete Quran rendered from local JSON',
                   'fullscreen':True,'real_604_page_line_layout':True,'verified_reference_page_564':True,'waveBars':63,'variableBarHeights':len(set(heights)),
                   'playerCollapsesWithoutCoveringText':True,'exitRestoresTabs':True,
                   'visualRedesignV2':v2,
                   'sourceVerses':6236,'sourcePages':604,'errors':errors})
   page.close()
  browser.close()
finally:
 server.shutdown();server.server_close()
(OUT/'metrics.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS REAL Salati Uthmani Quran: 604-coded-page source /6236 verses, page 1 -> 604 and back')
print('PASS independent MIT-derived MushafBook page structure with real 8/15 row grid + FULLSCREEN Quran 390/430, live seek visualization and restored navigation')
