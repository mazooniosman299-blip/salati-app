#!/usr/bin/env python3
"""Capture REAL Salati browser tabs in both languages; no imagined visuals.

Evidence screenshots + computed DOM metrics, not a claim of pixel equality
with the latest user image (which must be registered separately).
"""
from pathlib import Path
from functools import partial
from threading import Thread
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
from datetime import datetime, timezone
import json, os, re

ROOT=Path(os.environ.get("SALATI_PROJECT_ROOT",str(Path(__file__).resolve().parents[1]))).resolve()
DIST=ROOT/"dist"
OUT=Path(os.environ.get("SALATI_VISUAL_OUT",str(ROOT/"reports/current-design-visual-proof")))
OUT.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
SERVER=ThreadingHTTPServer(("127.0.0.1",0),partial(Quiet,directory=str(DIST)))
Thread(target=SERVER.serve_forever,daemon=True).start()
SELECTORS=["#mushaf","body","header>.site-nav","#prayers","#times .prayer-overview","#times","#mushafPlayerSlot #qTrack","#qibla .eyebrow","#androidDownload>p",
 "#mushaf #qSheet","#mushaf #qVerses","#mushafPlayerSlot","#mushaf #qTransport",
 "#qibla",".qibla-reading","#dhikr","#tasbih","#settings"]
SIZES=[(320,740),(390,844),(768,1024),(1280,850)]
TABS=["times","mushaf","qibla","dhikr","tasbih","settings"]
EVIDENCE=[]
# The current request owns interaction states even when ROOT points at a
# detached production baseline. Both captures must exercise the SAME state.
POLICY=json.loads((Path(__file__).resolve().parents[1]/'docs/requests/ACTIVE_CHANGE.json').read_text())
CAPTURE_STATES=POLICY.get('visual_capture_states',[])
assert len({s['tab'] for s in CAPTURE_STATES})==len(CAPTURE_STATES),'One requested state per tab'
for state in CAPTURE_STATES:
 assert state['tab']=='mushaf' and state['interaction']=='pointer'
 assert re.fullmatch(r'\.printed-ayah\[data-ayah=[\"\x27]\d+:\d+[\"\x27]\]',state['selector'])
 assert isinstance(state['surah'],int) and 1<=state['surah']<=114
for region in POLICY.get('visual_allowed_regions',[]):
 if region['selector'] not in SELECTORS:SELECTORS.append(region['selector'])
def exercise_state(page,state):
 page.locator('[data-reading-page="1"].original-printed-page').wait_for()
 page.locator('#qSurah').evaluate("(e,s)=>{e.value=String(s);e.dispatchEvent(new Event('change',{bubbles:true}))}",state['surah'])
 target=page.locator(state['selector']);target.wait_for();target.scroll_into_view_if_needed()
 point=target.evaluate('''e=>{const r=e.getBoundingClientRect();for(let y=1;y<8;y++)for(let x=1;x<8;x++){let a=r.x+r.width*x/8,b=r.y+r.height*y/8;if(document.elementFromPoint(a,b)?.closest('[data-ayah]')===e)return{x:a,y:b};}return null}''')
 assert point,'Requested original ayah has no visible pointer hit'
 page.mouse.click(point['x'],point['y'])
 # This is visual-state evidence, not an audio audition. Aborted media must
 # finish handling before either snapshot; dedicated media suites remain.
 page.wait_for_function("/تعذر|Could not/.test(document.querySelector('#qAudioStatus').textContent)")
 assert target.evaluate('e=>document.activeElement===e&&e.classList.contains("is-selected")')
 # Navigation may still be smoothly scrolling or awaiting the next leaf.
 # Align the same original page after media handling; never compare two
 # different reading positions or broaden the permitted visual region.
 next_page=target.evaluate('e=>Number(e.closest("[data-reading-page]").dataset.readingPage)+1')
 if next_page<=604:page.locator(f'[data-reading-page="{next_page}"].original-printed-page').wait_for()
 target.evaluate("e=>{const c=document.querySelector('#qVerses'),p=e.closest('[data-reading-page]');c.scrollTo({top:c.scrollTop+p.getBoundingClientRect().top-c.getBoundingClientRect().top,behavior:'instant'})}")
 # Pointer coordinates from before scrolling can now hover a different ayah.
 # Compare focus/selection with the pointer over neutral header padding.
 page.mouse.move(4,4)
 assert page.locator('.printed-ayah:hover').count()==0
 assert target.evaluate('e=>document.activeElement===e&&!e.matches(":focus-visible")')
def capture_metrics(page):
 return page.evaluate("""selectors => Object.fromEntries(selectors.map(selector => {
  const el=document.querySelector(selector);
  if(!el) return [selector,{exists:false}];
  const b=el.getBoundingClientRect(),c=getComputedStyle(el);
  return [selector,{exists:true,visible:b.width>0&&b.height>0&&c.visibility!=='hidden'&&c.display!=='none',
   x:b.x,y:b.y,width:b.width,height:b.height,right:b.right,bottom:b.bottom,
   color:c.color,background:c.backgroundColor,font:c.fontFamily,
   fontSize:c.fontSize,display:c.display,position:c.position,overflowX:c.overflowX,
   overflowY:c.overflowY,marginTop:c.marginTop,paddingBottom:c.paddingBottom}];
 }))""",SELECTORS)
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path="/usr/bin/chromium",args=["--no-sandbox"],headless=True)
  for language in ["ar","en"]:
   for width,height in SIZES:
    page=browser.new_page(viewport={"width":width,"height":height},service_workers="block",reduced_motion="reduce")
    if CAPTURE_STATES:page.route('https://**/*.mp3',lambda route:route.abort())
    page.clock.set_fixed_time(datetime(2026,11,3,10,15,tzinfo=timezone.utc))
    errors=[]
    page.on("pageerror",lambda e:errors.append(str(e)))
    page.add_init_script("if(!localStorage.getItem('salati')){localStorage.setItem('salati', JSON.stringify({"
      + "lang:" + json.dumps(language) + ",lat:23.588,lon:58.3829,zone:'Asia/Muscat',"
      + "name:'مسقط',method:'Oman',locationSet:true,locationMode:'manual',dark:true"
      + "}));}")
    resp=page.goto(f"http://127.0.0.1:{SERVER.server_port}/",wait_until="domcontentloaded",timeout=35000)
    assert resp and resp.ok,(language,width,"browser homepage failed")
    page.wait_for_function("document.querySelectorAll('#prayers .prayer').length===6",timeout=20000)
    assert page.locator("header>.site-nav button[data-tab]").count()==6
    assert page.locator('link[href="salati-ui.css"]').count()==1
    assert page.evaluate("getComputedStyle(document.body).backgroundColor")=="rgb(11, 14, 19)",(language,width,"dark-only body changed")
    page.evaluate('()=>document.fonts.ready')
    for tab in TABS:
     if tab!='mushaf' and width>760 and page.locator('#qReaderBack').is_visible():page.locator('#qReaderBack').click()
     page.locator(f'header>.site-nav button[data-tab="{tab}"]').click()
     page.wait_for_function("(name) => document.querySelector('header>.site-nav button.active')?.dataset.tab===name",arg=tab)
     assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+2"),(language,width,tab,"unexpected horizontal page scroll")
     nav=page.locator("header>.site-nav").evaluate("""e=>{const b=e.getBoundingClientRect();return {x:b.x,right:b.right,bottom:b.bottom}}""")
     assert nav["x"]>=-2 and nav["right"]<=width+2,(language,width,tab,"bottom navigation outside viewport",nav)
     if width<=760:assert abs(nav["bottom"]-height)<3,(language,width,tab,"navigation not anchored at bottom",nav)
     if tab=="mushaf":
      page.locator("#qVerses .quran-reading-page").first.wait_for(timeout=25000)
      if page.locator("#mushaf.printed-reader").count():page.locator(".original-printed-page").first.wait_for(timeout=25000)
      assert page.locator("#mushafPlayerSlot").count()==1,(language,width,"Quran audio dock missing")
      assert page.locator("#qTransport").count()==1 and page.locator("#qSeek").count()==1
      assert page.evaluate("!document.querySelector('#qVerses').contains(document.querySelector('#mushafPlayerSlot'))")
      q=page.locator("#qVerses").evaluate("""e=>({pages:e.querySelectorAll('.quran-reading-page').length,overflow:getComputedStyle(e).overflowY,height:e.clientHeight})""")
      assert q["pages"]>0 and q["height"]>50 and q["overflow"] in ("auto","scroll"),(language,width,q)
     for state in CAPTURE_STATES:
      if state['tab']==tab:exercise_state(page,state)
     page.evaluate('()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(()=>requestAnimationFrame(resolve))))')
     name=f"{language}-{tab}-{width}.png"
     page.screenshot(path=str(OUT/name),animations="disabled")
     EVIDENCE.append({"language":language,"tab":tab,"viewport":[width,height],
       "image":name,"computed":capture_metrics(page),"page_errors":list(errors)})
    assert not errors,(language,width,"JS exceptions",errors[:6])
    if width==390:
     page.locator("#lang").click()
     new="en" if language=="ar" else "ar"
     page.wait_for_function("(expected) => JSON.parse(localStorage.getItem('salati')).lang===expected",arg=new)
     page.reload(wait_until="domcontentloaded")
     page.wait_for_function("(expected) => JSON.parse(localStorage.getItem('salati')).lang===expected",arg=new)
     assert page.locator("#lang").count()==1
    page.close()
  browser.close()
finally:
 SERVER.shutdown()
 SERVER.server_close()
(OUT/"metrics.json").write_text(json.dumps({"source":"real local Chromium; production app assets",
 "matched_external_reference":False,"reference_status":"unverified until exact original image is available",
 "screenshots":EVIDENCE},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
assert len(EVIDENCE)==len(TABS)*len(SIZES)*2
print("PASS actual Salati Chromium: "+str(len(EVIDENCE))+" actual screenshots, 6 tabs, 2 languages, 4 viewport sizes, language persistence; NO pixel-match claim")
