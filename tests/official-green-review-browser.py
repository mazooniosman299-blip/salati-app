#!/usr/bin/env python3
"""Chromium screenshot from the REAL original Salati app with publisher PDF leaf."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright
import json

root = Path(__file__).resolve().parents[1]
output = root / "reports" / "official-green-review"
output.mkdir(parents=True, exist_ok=True)

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *a): pass

server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Quiet, directory=str(root / "dist")))
Thread(target=server.serve_forever, daemon=True).start()

try:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, executable_path="/usr/bin/chromium",
                                             args=["--no-sandbox"])
        for width, height in [(390, 844), (768, 960), (1440, 900)]:
            page = browser.new_page(viewport={"width": width, "height": height}, service_workers="block")
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.add_init_script(
                "localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,"
                "lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,"
                "locationMode:'manual'}))"
            )
            response = page.goto(f"http://127.0.0.1:{server.server_port}/?mushaf-preview=official-green",
                                 wait_until="domcontentloaded")
            assert response and response.ok
            page.click('[data-tab="mushaf"]')
            page.wait_for_function(
                "() => document.querySelector('#qGreenOriginalReview img')?.naturalWidth > 250",
                timeout=30000
            )
            geometry = page.evaluate("""() => {
                const rect = x => x.getBoundingClientRect();
                const a = document.getElementById('qGreenOriginalReview');
                const s = document.getElementById('qSheet');
                const p = document.getElementById('mushafPlayerSlot');
                const v = document.getElementById('qVerses');
                const image = a.querySelector('img');
                return {
                    inside: s.contains(a) && s.contains(p),
                    natural: [image.naturalWidth, image.naturalHeight],
                    readerHidden: v.hidden,
                    imageBottom: rect(image).bottom,
                    playerTop: rect(p).top,
                    frameBottom: rect(s).bottom,
                    playerBottom: rect(p).bottom,
                    width: rect(a).width,
                    externalScripts: Array.from(document.scripts).filter(x => x.src && !x.src.startsWith(location.origin)).length
                };
            }""")
            assert geometry['inside'] and geometry['readerHidden'], (width, geometry)
            assert geometry['playerTop'] >= geometry['imageBottom'] - 1, (width, 'verses covered', geometry)
            assert geometry['playerBottom'] <= geometry['frameBottom'] + 1, (width, 'dock outside mushaf', geometry)
            assert geometry['externalScripts'] == 0
            assert not errors, (width, errors)
            # Capture unmodified source first, then ensure the ENTIRE audio dock
            # is visible above the fixed bottom navigation on narrow phones.
            page.locator('#qSheet').screenshot(path=str(output / f"official-green-original-sheet-{width}.png"))
            page.locator('#mushafPlayerSlot').scroll_into_view_if_needed()
            if width <= 760:
                page.evaluate("""() => {
                    const p=document.getElementById('mushafPlayerSlot').getBoundingClientRect();
                    const nav=document.querySelector('header>.site-nav').getBoundingClientRect();
                    if(p.bottom>nav.top-7){
                        const main=document.querySelector('main');
                        if(main)main.scrollTop+=p.bottom-nav.top+20;
                        else window.scrollBy(0,p.bottom-nav.top+20);
                    }
                }""")
                page.wait_for_timeout(220)
                visible = page.evaluate("""() => ({
                    playerBottom:document.getElementById('mushafPlayerSlot').getBoundingClientRect().bottom,
                    navTop:document.querySelector('header>.site-nav').getBoundingClientRect().top
                })""")
                assert visible['playerBottom'] <= visible['navTop'] - 4, (width, 'player covered by bottom tabs', visible)
            page.screenshot(path=str(output / f"original-salati-green-review-{width}.png"), full_page=True)
            page.close()
        # No query flag: unchanged production reader with NO preview UI ever.
        clean = browser.new_page(service_workers="block")
        clean.goto(f"http://127.0.0.1:{server.server_port}/", wait_until="domcontentloaded")
        clean.click('[data-tab="mushaf"]')
        clean.wait_for_function("() => document.querySelector('#qVerses [data-ayah]') !== null")
        assert clean.locator('#qGreenOriginalReview').count() == 0
        assert clean.locator('#mushafPlayerSlot').count() == 1
        clean.close()
        browser.close()
    print('PASS: untouched Salati baseline; authentic scanned green edition in-frame with original player, no verse overlap, 390/768/1440px')
finally:
    server.shutdown()
