"""Audit computed UI colors, including portals/pseudo-elements and open menus."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from threading import Thread
import json
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')));Thread(target=s.serve_forever,daemon=True).start()
scan=r'''()=>{
 const findings=[];let inspected=0;
 function unexpected(color){const parts=color.match(/[\d.]+/g);if(!parts||parts.length<3)return false;let[r,g,b,a=1]=parts.map(Number);if(color.startsWith('color(srgb ')){r*=255;g*=255;b*=255;}if(a<=.01)return false;const key=[r,g,b].map(Math.round).join(',');return !['11,14,19','4,5,9','21,24,29','50,56,63','255,255,255','174,188,203','0,0,0'].includes(key);}

 for(const e of document.querySelectorAll('body *')){
  const rect=e.getBoundingClientRect(),base=getComputedStyle(e);
  if(!rect.width||!rect.height||base.visibility==='hidden'||base.display==='none')continue;
  for(const pseudo of [null,'::before','::after','::placeholder']){
   if(pseudo==='::placeholder'&&(!(e instanceof HTMLInputElement)||!e.placeholder||e.value))continue;
   const c=pseudo?getComputedStyle(e,pseudo):base;
   if(pseudo&&pseudo!=='::placeholder'&&['none','normal'].includes(c.content))continue;
   inspected++;
   const colors={color:c.color,background:c.backgroundColor,fill:c.fill,stroke:c.stroke};
   for(const edge of ['Top','Right','Bottom','Left'])if(parseFloat(c['border'+edge+'Width'])>0&&c['border'+edge+'Style']!=='none')colors['border'+edge]=c['border'+edge+'Color'];
   if(c.outlineStyle!=='none'&&parseFloat(c.outlineWidth)>0)colors.outline=c.outlineColor;
   for(const [property,color]of Object.entries(colors))if(unexpected(color))findings.push({element:e.tagName,id:e.id,class:e.getAttribute('class'),pseudo,property,color});
  }
 }
 return{inspected,findings};
}'''
results=[]
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  page=b.new_page(viewport={'width':390,'height':844},service_workers='block')
  page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:24.7136,lon:46.6753,zone:'Asia/Riyadh',name:'الرياض',locationSet:true,locationMode:'manual'}));")
  page.goto(f'http://127.0.0.1:{s.server_port}/',wait_until='domcontentloaded');page.wait_for_selector('.nav-selection')
  def audit(state):
   page.wait_for_timeout(350);result=page.evaluate(scan);results.append({'state':state,**result})
  for width in [390,1440]:
   page.set_viewport_size({'width':width,'height':1000})
   for dark in [True]:
    page.evaluate('(dark)=>document.body.classList.toggle("dark",dark)',dark)
    for tab in ['times','mushaf','qibla','dhikr','tasbih','settings']:
     page.click('[data-tab='+tab+']');audit(f'{width}/{dark}/{tab}')
     triggers=page.locator('button[aria-haspopup]')
     for i in range(triggers.count()):
      trigger=triggers.nth(i)
      if not trigger.is_visible() or trigger.is_disabled():continue
      label=trigger.get_attribute('id') or trigger.inner_text()
      trigger.click();audit(f'{width}/{dark}/{tab}/menu:{label}');page.keyboard.press('Escape')
  b.close()
 failures=[{'state':r['state'],**f}for r in results for f in r['findings']]
 output={'result':'FAIL' if failures else 'PASS','states':len(results),'computed_styles':sum(r['inspected']for r in results),'failures':failures,'checks':'Exact final palette for computed text, fill, stroke, backgrounds, active borders and outlines; black is allowed for monochrome masks/icons. Transparent colors excluded; actual photographs and OS/third-party UI are not palette tokens.'}
 (root/'reports'/('rendered-colors-'+__import__('re').search(r'app-v([\d.]+)\.js',(root/'dist/index.html').read_text())[1]+'.json')).write_text(json.dumps(output,indent=2)+'\n')
 print(json.dumps(output,indent=2));assert not failures,'Rendered colors outside the final palette remain'
finally:s.shutdown()
