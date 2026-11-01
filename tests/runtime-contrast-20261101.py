"""Measure actual computed foreground/background contrast on Salati UI at mobile and desktop sizes."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from threading import Thread
import json
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
out=root/'reports/runtime-contrast-20261101'
out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')))
Thread(target=server.serve_forever,daemon=True).start()
contrast_js=r"""selector=>{
 const el=document.querySelector(selector);
 if(!el)return {selector,error:'selector missing'};
 const val=getComputedStyle(el);
 const px=v=>{let c=v.match(/[0-9.]+/g);if(!c)return null;let z=c.map(Number);return z.length>=3?[z[0],z[1],z[2],z.length>3?z[3]:1]:null};
 const blend=(top,bottom)=>top.slice(0,3).map((x,i)=>x*top[3]+bottom[i]*(1-top[3]));
 let bg=[11,14,19],layers=[],node=el;
 while(node&&node.nodeType===1){
   const style=getComputedStyle(node),c=px(style.backgroundColor);
   if(c&&c[3]>0)layers.push(c);
   node=node.parentElement;
 }
 for(const layer of layers.reverse())bg=blend(layer,bg);
 const fg=px(val.color);
 if(!fg)return {selector,error:'foreground not resolved'};
 const lumi=c=>{
   let normalized=c.slice(0,3).map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4);
   return normalized[0]*.2126+normalized[1]*.7152+normalized[2]*.0722;
 };
 const text=blend(fg,bg);let l1=lumi(text),l2=lumi(bg);
 return {selector,ratio:+((Math.max(l1,l2)+.05)/(Math.min(l1,l2)+.05)).toFixed(2),
         fg:val.color,bg:bg.map(Math.round),fontSize:val.fontSize,visible:el.getBoundingClientRect().height>0};
}"""
targets={
 'times':['#times .prayer span','#times .prayer strong','#times .hero-prayer>span'],
 'mushaf':['#mushaf .quran-play-options label','#mushaf #qTrack'],
 'qibla':['#qibla .qibla-reading p','#qibla .qibla-reading h2','#qibla #headingValue'],
 'settings':['#settings .minute-adjustments .prayer-adjust-row span','#settings .audio-card>.eyebrow']
}
checks=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  for width in (360,390,768,1440):
   page=browser.new_page(viewport={'width':width,'height':844},service_workers='block')
   page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='domcontentloaded')
   for tab,selectors in targets.items():
    page.click(f'[data-tab={tab}]')
    page.wait_for_timeout(70)
    for selector in selectors:
     record=page.evaluate(contrast_js,selector)
     if record.get('error')=='selector missing':continue
     assert not record.get('error'),(width,tab,record)
     if not record['visible']:continue
     checks.append(dict(width=width,tab=tab,**record))
   page.click('[data-tab=settings]')
   page.click('#locationPickerOpen')
   page.wait_for_timeout(60)
   for selector in ['#locationOptions .location-automatic .choice-option-text',
                    '#locationOptions .choice-option-detail']:
    record=page.evaluate(contrast_js,selector)
    if not record.get('error') and record['visible']:checks.append(dict(width=width,tab='locations',**record))
   page.close()
  browser.close()
 (out/'results.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\\n',encoding='utf8')
 failed=[x for x in checks if x['ratio']<4.5]
 assert len(checks)>25,('Too few actual visible UI labels',checks)
 assert not failed,('Labels below 4.5:1 WCAG AA contrast in transparent backgrounds',failed)
 print('PASS: runtime contrast above 4.5:1 in',len(checks),'representative labels')
finally:
 server.shutdown()
