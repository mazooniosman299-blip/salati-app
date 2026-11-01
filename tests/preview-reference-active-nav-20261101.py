#!/usr/bin/env python3
"""Reference nav acceptance on the REAL Salati app, never a visual mockup.
The blue tab must follow all six clickable destinations, not only Quran.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
output=root/"reports"/"reference-nav-20261101"
output.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass

server=ThreadingHTTPServer(("127.0.0.1",0),partial(Quiet,directory=str(root/"dist")))
Thread(target=server.serve_forever,daemon=True).start()

tabs=["times","mushaf","qibla","dhikr","tasbih","settings"]
expected_ar=["المواقيت","المصحف","القبلة","الأذكار","المسبحة","الإعدادات"]
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path="/usr/bin/chromium",args=["--no-sandbox"])
  for width,height in [(320,740),(360,780),(390,844),(412,915),(480,900),(760,960)]:
   page=browser.new_page(viewport={"width":width,"height":height},service_workers="block")
   errors=[]
   page.on("pageerror",lambda error: errors.append(str(error)))
   page.add_init_script("""localStorage.setItem('salati',JSON.stringify({lat:23.588,lon:58.3829,zone:'Asia/Muscat',method:'Auto',madhab:'Shafi',name:'مسقط',locationSet:true,locationMode:'manual',lang:'ar'}))""")
   result=page.goto(f"http://127.0.0.1:{server.server_port}/",wait_until="domcontentloaded")
   assert result and result.ok,(width,"page did not load")
   page.wait_for_function("document.querySelectorAll('header>.site-nav button[data-tab]').length===6")
   for index,tab in enumerate(tabs):
    button=page.locator(f'header>.site-nav button[data-tab="{tab}"]')
    button.click(timeout=15000)
    page.wait_for_function("(tab)=>document.querySelector('header>.site-nav button.active')?.dataset.tab===tab",arg=tab)
    measures=page.evaluate("""()=>{
     const nav=document.querySelector('header>.site-nav');
     const r=nav.getBoundingClientRect(),s=getComputedStyle(nav);
     const buttons=[...nav.querySelectorAll('button[data-tab]')].map(button=>{
      const b=button.getBoundingClientRect(),c=getComputedStyle(button);
      const label=button.querySelector('span'),i=button.querySelector('svg');
      const t=label.getBoundingClientRect(),svg=i.getBoundingClientRect();
      return {tab:button.dataset.tab,active:button.classList.contains('active'),
       pressed:button.getAttribute('aria-pressed'),text:label.textContent.trim(),
       background:c.backgroundColor,image:c.backgroundImage,border:c.borderTopWidth,
       x:b.left,right:b.right,top:b.top,bottom:b.bottom,
       labelWidth:label.scrollWidth,labelClient:label.clientWidth,
       textLeft:t.left,textRight:t.right,iconWidth:svg.width,iconHeight:svg.height,
       color:getComputedStyle(label).color};
     });
     return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height,
      radius:s.borderTopLeftRadius,gap:s.columnGap,
      bg:s.backgroundColor,buttons};
    }""")
    assert measures["left"]>=-1 and measures["right"]<=width+1,(width,tab,"navigation outside screen",measures)
    assert measures["width"]>=width-20,(width,tab,"container should be almost full-width",measures)
    assert measures["height"]>=73,(width,tab,"short navigation, does not match approved capsule",measures)
    assert measures["bg"]=="rgb(9, 10, 14)",(width,tab,"not one matte outer capsule",measures)
    assert measures["radius"]=="29px",(width,tab,"wrong outer capsule roundness",measures)
    buttons=measures["buttons"]
    assert [b["tab"] for b in buttons]==tabs,(width,"tab order changed",buttons)
    assert [b["text"] for b in buttons]==expected_ar,(width,"labels/icons were modified",buttons)
    assert sum(b["active"] for b in buttons)==1,(width,tab,"more than one selected",buttons)
    for b in buttons:
     assert b["x"]>=measures["left"]-1 and b["right"]<=measures["right"]+1,(width,b["tab"],"tab outside capsule",b)
     assert b["top"]>=measures["top"]-1 and b["bottom"]<=measures["bottom"]+1,(width,b["tab"],"tab outside vertical capsule",b)
     assert b["labelWidth"]<=b["labelClient"]+1,(width,b["tab"],"Arabic label clipped",b)
     assert b["color"]=="rgb(255, 255, 255)",(width,b["tab"],"must have white label",b)
     assert b["iconWidth"]>=22 and b["iconHeight"]>=22,(width,b["tab"],"icon too small",b)
     if b["tab"]==tab:
      assert b["active"] and b["pressed"]=="true",(width,tab,"selected accessibility state",b)
      assert b["background"]=="rgb(17, 74, 183)",(width,tab,"blue must follow active tab",b)
      assert "linear-gradient" in b["image"],(width,tab,"reference blue fill lost",b)
     else:
      assert b["pressed"]=="false",(width,b["tab"],"old active tab retained",b)
      assert b["background"]=="rgba(0, 0, 0, 0)",(width,b["tab"],"inactive tab must be transparent",b)
      assert b["image"]=="none" and b["border"]=="0px",(width,b["tab"],"inactive individual tile still drawn",b)
    if width in (320,390,480) or index in (0,1):
     page.screenshot(path=str(output/f"nav-{width}-{tab}.png"))
   assert not errors,(width,"unexpected JS errors",errors)
   print("PASS",width,"reference capsule, six clear labels, moving blue selection on every tab")
   page.close()
  browser.close()
finally:
 server.shutdown()
