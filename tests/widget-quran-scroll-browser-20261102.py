#!/usr/bin/env python3
"""Verify real Quran vertical scrolling across pages without arrow controls."""
from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'reports/widget-quran-scroll-20261102'
OUTPUT.mkdir(parents=True,exist_ok=True)
class Silent(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
@contextmanager
def server():
    srv=ThreadingHTTPServer(('127.0.0.1',0),partial(Silent,directory=str(ROOT/'dist')))
    t=Thread(target=srv.serve_forever,daemon=True)
    t.start()
    try:yield f'http://127.0.0.1:{srv.server_port}/'
    finally:srv.shutdown();srv.server_close()

with server() as origin, sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
    for width,height in [(390,844),(1280,850)]:
        page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
        errors=[]
        page.on('pageerror',lambda err:errors.append(str(err)))
        page.goto(origin,wait_until='domcontentloaded',timeout=30000)
        page.locator('button[data-tab="mushaf"]').click()
        page.locator('#qVerses .quran-reading-page').first.wait_for(timeout=30000)
        page.locator('#qVerses').scroll_into_view_if_needed()
        state=page.evaluate("""() => {
          const q=document.getElementById('qVerses'),s=getComputedStyle(q),
            nav=document.querySelector('.mushaf-pagination');
          return {visible:!document.getElementById('mushaf').hidden,
            continuous:q.querySelectorAll('.quran-reading-page').length,
            overflow:s.overflowY,touch:s.touchAction,
            viewport:q.clientHeight,content:q.scrollHeight,
            noArrows:!nav.querySelector('button,a'),
            label:q.getAttribute('aria-label'),player:!!document.getElementById('mushafPlayerSlot')};
        }""")
        assert state['visible'] and state['noArrows'] and state['player'],state
        assert state['overflow'] in ('auto','scroll'),state
        assert state['touch']=='pan-y',state
        assert state['viewport']>150 and state['content']>=state['viewport'],state
        assert state['label'] and 'مرّر عمودياً' in state['label'],state
        before=state['continuous']
        # Wheel/touch gestures control one scrollable Quran reader; next pages
        # are added by IntersectionObserver rather than page buttons.
        for _ in range(12):
            page.locator('#qVerses').hover()
            page.mouse.wheel(0,1150)
            page.wait_for_timeout(250)
        page.wait_for_function("() => document.querySelectorAll('#qVerses .quran-reading-page').length >= 2",timeout=15000)
        after=page.locator('#qVerses .quran-reading-page').count()
        assert after>=before and after>=2,(width,before,after)
        assert not errors,errors[:8]
        page.screenshot(path=str(OUTPUT/f'quran-{width}px.png'),full_page=False)
        print('PASS',width,'Quran page count',before,'->',after,'arrowless vertical scroll, original player retained')
        page.close()
    browser.close()
