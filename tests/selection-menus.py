"""Every selection list shares the supplied centered glass reference, preserving behavior."""
from pathlib import Path
from functools import partial
from threading import Thread
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
import json
root=Path(__file__).resolve().parents[1];out=root/'reports/visual-corrections-1.0.109/menus';out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'dist')));Thread(target=s.serve_forever,daemon=True).start();checks=[]
try:
 with sync_playwright()as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(service_workers='block');errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.add_init_script("localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,locationMode:'manual'}))")
  page.goto(f'http://127.0.0.1:{s.server_port}/',wait_until='domcontentloaded');page.wait_for_timeout(500);assert not errors,errors;page.click('[data-tab=mushaf]');page.wait_for_function('document.getElementById("qSurah").options.length>=114')
  cases=[('mushaf','qSurahPickerOpen','choicePicker'),('mushaf','qJuzPickerOpen','choicePicker'),('mushaf','qReciterPickerOpen','choicePicker'),('mushaf','__verse__','verseReciterMenuDialog'),('settings','locationPickerOpen','locationMenu'),('settings','voicePickerOpen','voicePicker'),('settings','methodPickerOpen','choicePicker'),('settings','madhabPickerOpen','choicePicker'),('dhikr','adhkarCategoryPickerOpen','adhkarCategoryMenuDialog')]
  for width in [390,1440]:
   page.set_viewport_size({'width':width,'height':1000})
   for tab,trigger,dialogid in cases:
    page.click(f'[data-tab={tab}]')
    if trigger=='madhabPickerOpen':page.locator('#method').select_option(index=1,force=True)
    if trigger=='__verse__':page.locator('#qVerses [data-ayah]').first.press('Enter')
    else:page.click('#'+trigger)
    d=page.locator('#'+dialogid);d.wait_for(state='visible');page.wait_for_timeout(350)
    box=d.bounding_box();assert box['x']>=0 and box['y']>=0 and box['x']+box['width']<=width+1 and box['y']+box['height']<=1001,(width,trigger,box)
    assert abs(box['x']+box['width']/2-width/2)<2 and abs(box['y']+box['height']/2-500)<2,(width,trigger,'dialog must be centered',box)
    assert d.locator('input[type=search]:visible').count()==1,(trigger,'one visible search')
    search=d.locator('input[type=search]:visible');search.focus();focus=search.evaluate('(e)=>({outline:getComputedStyle(e).outlineWidth,shadow:getComputedStyle(e).boxShadow,border:getComputedStyle(e).borderTopWidth})');assert focus=={'outline':'0px','shadow':'none','border':'1px'},(trigger,focus)
    rows=d.locator('button.choice-option,button.voice-option');assert rows.count()>0,trigger
    styles=rows.evaluate_all('(es)=>es.filter(e=>!e.hidden).slice(0,5).map(e=>{let c=getComputedStyle(e);return{selected:e.matches("[aria-selected=true],[aria-checked=true],[aria-pressed=true]"),bg:c.backgroundColor,image:c.backgroundImage,radius:c.borderRadius,color:c.color}})')
    assert all(x['bg']==('rgb(43, 57, 71)'if x['selected']else'rgb(32, 41, 51)')and x['color']=='rgb(255, 255, 255)'and x['radius']=='16px'and x['image']=='none'for x in styles),(trigger,styles)
    close=d.locator('.choice-close,#voicePickerClose');cb=close.bounding_box();assert cb['width']==cb['height']==44,(trigger,cb)
    closecolor=close.evaluate('(e)=>getComputedStyle(e).backgroundColor');assert closecolor not in ['rgb(37, 99, 235)','rgb(29, 78, 216)'],closecolor
    d.screenshot(path=str(out/f'{trigger}-{width}.png'));page.keyboard.press('Escape');assert not d.is_visible(),trigger
    assert (page.locator('#qVerses [data-ayah]').first if trigger=='__verse__' else page.locator('#'+trigger)).evaluate('(e)=>e===document.activeElement'),(trigger,'close returns focus')
   # Search + arrow navigation skips hidden verse readers.
   page.click('[data-tab=mushaf]');page.locator('#qVerses [data-ayah]').first.press('Enter');page.locator('#verseReciterMenuDialog input').fill('ش');page.locator('#verseReciterMenu [data-reciter=shatri]').focus();page.keyboard.press('ArrowDown');assert page.locator('#verseReciterMenu [data-reciter=afasy]').evaluate('(e)=>e===document.activeElement');page.keyboard.press('Escape')
   # Search and select retain the underlying select/change path.
   page.click('[data-tab=mushaf]');page.click('#qSurahPickerOpen');page.locator('#choiceSearch').fill('البقرة');assert page.locator('#choiceList button').count()==1;page.locator('#choiceList button').click();assert page.locator('#qSurah').input_value()=='2'
   page.click('[data-tab=dhikr]');page.click('#adhkarCategoryPickerOpen');page.locator('#adhkarCategoryMenu input').fill('الصباح');rows=page.locator('#adhkarCategoryOptions button');assert rows.count()>=1;rows.first.click();assert not page.locator('#adhkarCategoryMenuDialog').is_visible();assert 'الصباح'in page.locator('#adhkarCategoryPickerOpen').inner_text()
   page.click('[data-tab=settings]');page.click('#voicePickerOpen');page.locator('#voicePickerSearch').fill('النفيس');assert page.locator('#voicePickerList button:visible').count()==1;page.locator('#voicePickerList button:visible').click();assert page.locator('#audioVoice').input_value()=='nufais'
   # Native back hook closes the modal before leaving the current tab.
   page.click('#locationPickerOpen');assert page.evaluate('window.salatiHandleBack()')is True;assert not page.locator('#locationMenu').is_visible()
   checks.append({'width':width,'menus':len(cases),'search_selection_focus_back':'PASS'})
  assert not errors,errors;b.close()
 (out/'checks.json').write_text(json.dumps({'result':'PASS','checks':checks,'page_errors':errors},indent=2)+'\n');print('PASS: shared centered reference for nine menus at phone/desktop widths; dark glass rows, search, round close, selection, focus, Escape and Android back.')
finally:s.shutdown()
