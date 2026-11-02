"""Verify Salati's original mushaf encloses the audio controls without obscuring any ayah."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "mushaf-inframe-player-20261102"
REPORT.mkdir(parents=True, exist_ok=True)

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Quiet, directory=str(ROOT / "dist")))
Thread(target=server.serve_forever, daemon=True).start()

try:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path="/usr/bin/chromium", headless=True, args=["--no-sandbox"]
        )
        for width in (320, 390, 760, 768, 1440):
            page = browser.new_page(viewport={"width": width, "height": 900}, service_workers="block")
            page.add_init_script(
                "localStorage.setItem('salati',JSON.stringify({lang:'ar',lat:23.588,"
                "lon:58.3829,zone:'Asia/Muscat',name:'مسقط',locationSet:true,"
                "locationMode:'manual'}))"
            )
            failures = []
            page.on("pageerror", lambda error: failures.append(str(error)))
            response = page.goto(f"http://127.0.0.1:{server.server_port}/", wait_until="domcontentloaded")
            assert response and response.ok, (width, "reader failed to load")
            page.click("[data-tab=mushaf]")
            page.wait_for_function(
                "() => !!document.querySelector('#qVerses .quran-reading-page .quran-text [data-ayah]')",
                timeout=30000
            )
            page.locator("#mushafPlayerSlot").scroll_into_view_if_needed()
            page.evaluate("""() => {
                const p = document.getElementById('mushafPlayerSlot').getBoundingClientRect();
                const nav = document.querySelector('header>.site-nav').getBoundingClientRect();
                const main = document.querySelector('main');
                if (innerWidth <= 760 && p.bottom > nav.top - 8 && main)
                    main.scrollTop += p.bottom - nav.top + 18;
            }""")
            geometry = page.evaluate("""() => {
                const byId = id => document.getElementById(id);
                const rect = el => {
                    const b = el.getBoundingClientRect();
                    return { top:b.top, bottom:b.bottom, left:b.left, right:b.right, width:b.width, height:b.height };
                };
                const q = byId('qVerses'), p = byId('mushafPlayerSlot'), s = byId('qSheet');
                return {
                    inside:s.contains(p),
                    versesContainPlayer:q.contains(p),
                    follows:!!(q.compareDocumentPosition(p) & Node.DOCUMENT_POSITION_FOLLOWING),
                    position:getComputedStyle(p).position,
                    reader:rect(q), player:rect(p), sheet:rect(s),
                    track:rect(byId('qSeek')), button:rect(byId('qTransport')),
                    verseCount:q.querySelectorAll('[data-ayah]').length,
                    navTop:document.querySelector('header>.site-nav').getBoundingClientRect().top
                };
            }""")
            assert geometry["inside"] and not geometry["versesContainPlayer"], (width, "player must be IN the sheet but OUT of the Quran text", geometry)
            assert geometry["follows"], (width, "player precedes Quran verse text", geometry)
            assert geometry["position"] not in ("absolute", "fixed", "sticky"), (width, "player overlays text", geometry)
            assert geometry["verseCount"] > 0, (width, "verse text missing", geometry)
            assert geometry["reader"]["bottom"] <= geometry["player"]["top"] + 1, (width, "player overlaps verse viewport", geometry)
            assert geometry["player"]["bottom"] <= geometry["sheet"]["bottom"] + 1, (width, "player escapes the mushaf", geometry)
            assert geometry["player"]["left"] >= geometry["sheet"]["left"] - 1, (width, "player clipped at left", geometry)
            assert geometry["player"]["right"] <= geometry["sheet"]["right"] + 1, (width, "player clipped at right", geometry)
            for key in ("track", "button"):
                assert geometry[key]["width"] > 0 and geometry[key]["height"] > 0, (width, key, geometry)
                assert geometry[key]["left"] >= geometry["player"]["left"] - 2, (width, key, "left clipped", geometry)
                assert geometry[key]["right"] <= geometry["player"]["right"] + 2, (width, key, "right clipped", geometry)
            page.locator("#qSheet").screenshot(path=str(REPORT / f"mushaf-player-{width}.png"))
            assert not failures, (width, "browser errors", failures)
            page.close()
        browser.close()
    print("PASS: player inside original mushaf, below Quran verses, not floating; 320/390/760/768/1440px")
finally:
    server.shutdown()
