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

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/"dist"
OUT=Path(os.environ.get("SALATI_VISUAL_OUT",str(ROOT/"reports/current-design-visual-proof")))
OUT.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
SERVER=ThreadingHTTPServer(("127.0.0.1",0),partial(Quiet,directory=str(DIST)))
Thread(target=SERVER.serve_forever,daemon=True).start()
SELECTORS=["body","header>.site-nav","#prayers","#times .prayer-overview",
 "#mushaf #qSheet","#mushaf #qVerses","#mushafPlayerSlot","#mushaf #qTransport",
 "#qibla",".qibla-reading","#dhikr","#tasbih","#settings"]
SIZES=[(320,740),(390,844),(768,1024),(1280,850)]
TABS=["times","mushaf","qibla","dhikr","tasbih","settings"]
EVIDENCE=[]
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
    page.clock.set_fixed_time(datetime(2026,11,3,10,15,tzinfo=timezone.utc))
    errors=[]
    page.on("pageerror",lambda e:errors.append(str(e)))
    page.add_init_script("localStorage.setItem('salati', JSON.stringify({"
      + "lang:" + json.dumps(language) + ",lat:23.588,lon:58.3829,zone:'Asia/Muscat',"
      + "name:'مسقط',method:'Oman',locationSet:true,locationMode:'manual',dark:true"
      + "}));")
    resp=page.goto(f"http://127.0.0.1:{SERVER.server_port}/",wait_until="domcontentloaded",timeout=35000)
    assert resp and resp.ok,(language,width,"browser homepage failed")
    page.wait_for_function("document.querySelectorAll('#prayers .prayer').length===6",timeout=20000)
    assert page.locator("header>.site-nav button[data-tab]").count()==6
    assert page.locator('link[href="salati-ui.css"]').count()==1
    assert page.evaluate("getComputedStyle(document.body).backgroundColor")=="rgb(11, 14, 19)",(language,width,"dark-only body changed")
    for tab in TABS:
     page.locator(f'header>.site-nav button[data-tab="{tab}"]').click()
     page.wait_for_function("(name) => document.querySelector('header>.site-nav button.active')?.dataset.tab===name",arg=tab)
     assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+2"),(language,width,tab,"unexpected horizontal page scroll")
     nav=page.locator("header>.site-nav").evaluate("""e=>{const b=e.getBoundingClientRect();return {x:b.x,right:b.right,bottom:b.bottom}}""")
     assert nav["x"]>=-2 and nav["right"]<=width+2,(language,width,tab,"bottom navigation outside viewport",nav)
     if width<=760:assert abs(nav["bottom"]-height)<3,(language,width,tab,"navigation not anchored at bottom",nav)
     if tab=="mushaf":
      page.locator("#qVerses .quran-reading-page").first.wait_for(timeout=25000)
      assert page.locator("#mushafPlayerSlot").count()==1,(language,width,"Quran audio dock missing")
      assert page.locator("#qTransport").count()==1 and page.locator("#qSeek").count()==1
      assert page.evaluate("!document.querySelector('#qVerses').contains(document.querySelector('#mushafPlayerSlot'))")
      q=page.locator("#qVerses").evaluate("""e=>({pages:e.querySelectorAll('.quran-reading-page').length,overflow:getComputedStyle(e).overflowY,height:e.clientHeight})""")
      assert q["pages"]>0 and q["height"]>50 and q["overflow"] in ("auto","scroll"),(language,width,q)
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
