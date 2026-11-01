#!/usr/bin/env python3
"""No-deploy visual acceptance for Salati screenshot corrections.
Loads the real dist bundle (not reconstructed HTML) in Chromium.
"""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
report = root / "reports" / "reader-below-ui-20261101"
report.mkdir(parents=True, exist_ok=True)

# The home-screen provider can request width but cannot remove launcher margins.
a="{http://schemas.android.com/apk/res/android}"
info=ET.parse(root/"android/app/src/main/res/xml/prayer_widget_info.xml").getroot()
assert info.get(a+"targetCellWidth")=="5"
assert info.get(a+"resizeMode")=="horizontal|vertical"
widget=(root/"android/app/src/main/res/layout/prayer_widget.xml").read_text()
controller=(root/"android/app/src/main/java/com/salati/prayer/PrayerWidget.java").read_text()
assert 'android:id="@+id/widget_root" android:layout_width="match_parent"' in widget
assert 'android:id="@+id/widget_scenery" android:layout_width="match_parent"' in widget
assert 'android:scaleType="centerCrop"' in widget
assert 'android:paddingLeft="6dp"' in widget and 'android:paddingRight="6dp"' in widget
assert 'compact?3:6' in controller and 'int inset=height<220?3:6' in controller
assert "views.setViewPadding(R.id.widget_card,inset,inset,inset,0)" in controller

class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass

srv=ThreadingHTTPServer(("127.0.0.1",0),partial(Quiet,directory=str(root/"dist")))
Thread(target=srv.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path="/usr/bin/chromium",args=["--no-sandbox"])
  for width,height in ((320,740),(360,780),(390,844),(412,915),(480,900),(760,960),(900,900)):
   page=browser.new_page(viewport={"width":width,"height":height},service_workers="block")
   faults=[]
   page.on("pageerror",lambda err:faults.append(str(err)))
   page.add_init_script("""localStorage.setItem('salati',JSON.stringify({lat:23.588,lon:58.3829,zone:'Asia/Muscat',method:'Oman',madhab:'Shafi',name:'مسقط',locationSet:true,locationMode:'manual',lang:'ar'}));""")
   response=page.goto(f"http://127.0.0.1:{srv.server_port}/",wait_until="domcontentloaded")
   assert response and response.ok,(width,"cannot load Salati app")
   page.wait_for_function("document.querySelectorAll('#prayers .prayer').length===6")
   cards=page.locator('#prayers .prayer').evaluate_all("""es=>es.map(e=>{const r=e.getBoundingClientRect(),n=e.querySelector('span'),t=e.querySelector('strong'),s=getComputedStyle(e);return {x:r.left,right:r.right,y:r.top,bottom:r.bottom,bg:s.backgroundColor,border:s.borderTopWidth,radius:s.borderTopLeftRadius,label:n.textContent,time:t.textContent,ns:n.scrollWidth,nc:n.clientWidth,ts:t.scrollWidth,tc:t.clientWidth}})""")
   if width<=760:
    assert len({round(c["y"]) for c in cards})==1,(width,"six prayers must share a row",cards)
    assert all(c["x"]>=-1 and c["right"]<=width+1 for c in cards),(width,"prayer overflow",cards)
    assert all(c["bg"]=="rgba(0, 0, 0, 0)" for c in cards),(width,"individual prayer cards still visible",cards)
    assert all(c["border"]=="0px" and c["radius"]=="0px" for c in cards),(width,"individual prayer borders/corners still visible",cards)
    assert all(c["ts"]<=c["tc"]+2 and c["ns"]<=c["nc"]+2 for c in cards),(width,"prayer label or clock clipped",cards)
    container=page.locator("#prayers").evaluate("e=>getComputedStyle(e).backgroundColor")
    assert container=="rgb(36, 36, 36)",(width,"missing shared matte strip",container)
   page.screenshot(path=str(report/f"home-{width}.png"))

   page.locator("[data-tab=mushaf]").click()
   page.wait_for_function("document.querySelector('#qVerses')?.textContent?.trim().length>35",timeout=20000)
   js="""()=>{
    const el=id=>document.getElementById(id);
    const rect=id=>{const r=el(id).getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height}};
    const v=el('qVerses'),p=el('mushafPlayerSlot'),q=el('qSheet');
    const n=document.querySelector('header>.site-nav').getBoundingClientRect();
    return {reader:rect('qVerses'),player:rect('mushafPlayerSlot'),sheet:rect('qSheet'),
      seek:rect('qSeek'),transport:rect('qTransport'),elapsed:rect('qElapsed'),duration:rect('qDuration'),
      pos:getComputedStyle(p).position,display:getComputedStyle(v).overflowY,scrollHeight:v.scrollHeight,clientHeight:v.clientHeight,
      order:v.compareDocumentPosition(p),navTop:n.top,scriptErrors:[]};
   }"""
   before=page.evaluate(js)
   assert before["order"] & 4,(width,"player must follow reading area in DOM",before)
   assert before["pos"] not in ("fixed","sticky","absolute"),(width,"player may not float over Quran",before)
   assert before["reader"]["bottom"]<=before["player"]["top"]+1,(width,"player overlaps Quran",before)
   if width<=760:
    assert before["display"]=="auto",(width,"reader must scroll independently",before)
    assert before["scrollHeight"]>before["clientHeight"]+10,(width,"verses should scroll",before)
   page.locator("#mushafPlayerSlot").scroll_into_view_if_needed()
   # Navigation is a fixed footer. Scroll the app shell enough for the player
   # to be fully visible above its top without requiring any Quran text overlay.
   page.evaluate("""()=>{
    const p=document.getElementById('mushafPlayerSlot').getBoundingClientRect();
    const nav=document.querySelector('header>.site-nav').getBoundingClientRect();
    if(p.bottom>nav.top-8){const main=document.querySelector('main');if(main){main.scrollTop+=p.bottom-nav.top+18}else window.scrollBy(0,p.bottom-nav.top+18)}
   }""")
   page.wait_for_timeout(120)
   after=page.evaluate(js)
   assert after["reader"]["bottom"]<=after["player"]["top"]+1,(width,"player covers verses after scroll",after)
   assert after["player"]["left"]>=-1 and after["player"]["right"]<=width+1,(width,"player horizontal clipping",after)
   for key in ("seek","transport","elapsed","duration"):
    r=after[key];pr=after["player"]
    assert r["width"]>0 and r["height"]>0,(width,key,"player control invisible",after)
    assert r["left"]>=pr["left"]-2 and r["right"]<=pr["right"]+2,(width,key,"player control clipped sideways",after)
   if width<=760:
    assert after["seek"]["width"]>=50,(width,"seek bar crushed",after)
    assert after["elapsed"]["right"]+4<=after["duration"]["left"],(width,"player clocks overlap",after)
   page.screenshot(path=str(report/f"reader-player-{width}.png"))
   if width<=760:
    page.evaluate("document.getElementById('qVerses').scrollTop=230")
    page.wait_for_timeout(160)
    state=page.evaluate("({top:document.getElementById('qVerses').scrollTop,range:document.getElementById('qVerses').scrollHeight-document.getElementById('qVerses').clientHeight})")
    assert state["range"]>10 and 10<state["top"]<=state["range"]+2,(width,"Quran scrollport must move and remain within its range",state)
   assert not faults,(width,"JavaScript runtime errors",faults)
   page.close()
   print("PASS",width,"no prayer-card boxes; Quran player below separate scrollport; all player controls fit")
  browser.close()
finally:
 srv.shutdown()
