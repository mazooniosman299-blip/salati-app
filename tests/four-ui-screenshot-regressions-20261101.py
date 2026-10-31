"""Four screenshot issues: black Mushaf glyph, Qibla contrast, every location pin, no voice checks.
Real Chromium only. This test never deploys or signs anything.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import json
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
evidence = root / "reports" / "four-screenshot-regressions"
evidence.mkdir(parents=True, exist_ok=True)

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Quiet, directory=str(root / "dist")))
Thread(target=server.serve_forever, daemon=True).start()
checks = []
try:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True, executable_path="/usr/bin/chromium", args=["--no-sandbox"]
        )
        for width in (360, 390, 768, 1440):
            page = browser.new_page(viewport={"width": width, "height": 900}, service_workers="block")
            page.add_init_script(
                "localStorage.setItem('salati',JSON.stringify({"
                "lang:'ar',lat:23.588,lon:58.3829,zone:'Asia/Muscat',"
                "name:'مسقط',locationSet:true,locationMode:'manual'}))"
            )
            errors = []
            page.on("pageerror", lambda err: errors.append(str(err)))
            response = page.goto(f"http://127.0.0.1:{server.server_port}/", wait_until="domcontentloaded")
            assert response is not None and response.ok

            # Black circled Quran ornament glyphs are font-dependent text signs,
            # not verse numbers. Keep verified rosette and Quran source bytes.
            page.click("[data-tab=mushaf]")
            page.locator("#qVerses .quran-text .ayah-number").first.wait_for(state="visible", timeout=25000)
            page.wait_for_function("document.querySelector('#qVerses .ayah-number[data-mushaf-ornament]')")
            assert page.locator("#qVerses").evaluate("e=>!/[\\u06dd\\u06de]/u.test(e.textContent)")
            page.evaluate("""()=>{
                const verse=document.querySelector('#qVerses .quran-text [data-ayah]');
                verse.appendChild(document.createTextNode('\\u06dd\\u06de'));
            }""")
            page.wait_for_function("!/[\\u06dd\\u06de]/u.test(document.querySelector('#qVerses').textContent)")
            number=page.locator("#qVerses .ayah-number").first.inner_text().strip()
            assert number and all(c in "٠١٢٣٤٥٦٧٨٩" for c in number), (width, "readable number", number)
            assert "quran-ayah-rosette.svg" in page.locator("#qVerses .ayah-number").first.evaluate(
                "e=>getComputedStyle(e).backgroundImage"
            ),(width,"keep ornate ayah numbers")
            page.locator("#qVerses").screenshot(path=str(evidence/f"mushaf-{width}.png"))

            # The entire bearing block and the true-north badge are explicit,
            # opaque matte layers with strong borders; no dull opacity overlay.
            page.click("[data-tab=qibla]")
            bearing=page.locator("#qibla .qibla-reading")
            style=bearing.evaluate("""e=>({
                bg:getComputedStyle(e).backgroundColor,
                border:getComputedStyle(e).borderTopColor,
                width:getComputedStyle(e).borderTopWidth,
                opacity:getComputedStyle(e).opacity,
                filter:getComputedStyle(e).filter
            })""")
            assert style["bg"]=="rgb(36, 43, 51)" and style["border"]=="rgb(102, 115, 129)",(width,style)
            assert style["width"]=="1px" and style["opacity"]=="1" and style["filter"]=="none",(width,style)
            heading=page.locator("#headingValue").evaluate(
                "e=>({bg:getComputedStyle(e).backgroundColor,border:getComputedStyle(e).borderTopColor,color:getComputedStyle(e).color})"
            )
            assert heading=={"bg":"rgb(17, 22, 29)","border":"rgb(104, 117, 131)","color":"rgb(255, 255, 255)"},(width,heading)
            bearing.screenshot(path=str(evidence/f"qibla-{width}.png"))

            # Every country and automatic option uses the SAME SVG, centered
            # against the first Arabic title line, not the subtitle or row.
            page.click("[data-tab=settings]")
            page.click("#locationPickerOpen")
            page.locator("#locationOptions .choice-option").first.wait_for(state="visible")
            locations=page.locator("#locationOptions .choice-option").evaluate_all("""es=>es.map(e=>{
                const icon=e.querySelector('.location-icon');
                const title=e.querySelector('.choice-option-text');
                if(!icon||!title)return {label:e.innerText,error:'missing icon or title'};
                const r=icon.getBoundingClientRect(),b=title.getBoundingClientRect();
                return {label:e.innerText.slice(0,32),
                  offset:r.top+r.height/2-b.top-parseFloat(getComputedStyle(title).lineHeight)/2,
                  size:[r.width,r.height],relative:getComputedStyle(icon).position}
            })""")
            assert len(locations)==251,(width,"all location rows",len(locations))
            assert all("error" not in x and abs(x["offset"])<=4 and x["size"]==[18,18] and x["relative"]=="static" for x in locations),(width,"bad pins",[x for x in locations if "error" in x or abs(x.get("offset",99))>4][:10])
            page.locator("#locationOptions").screenshot(path=str(evidence/f"locations-{width}.png"))
            page.keyboard.press("Escape")

            # Four original voice positions. The selected state is retained
            # but neither a CSS-generated tick nor a check SVG is present.
            page.click("#voicePickerOpen")
            for voice in ("qatami","nufais","makkah","aqsa"):
                page.evaluate("""value=>{
                   const select=document.querySelector('#audioVoice');
                   select.value=value;select.dispatchEvent(new Event('change',{bubbles:true}));
                }""",voice)
                rows=page.locator("#voicePickerList .voice-option").evaluate_all("""es=>es.map(e=>({
                    value:e.dataset.voiceOption,
                    chosen:e.getAttribute('aria-pressed')==='true',
                    checkNodes:e.querySelectorAll('.voice-check').length,
                    tick:getComputedStyle(e.querySelector('.voice-symbol'),'::after').content,
                    wave:getComputedStyle(e.querySelector('.voice-symbol svg')).display
                }))""")
                assert [x["value"] for x in rows]==["qatami","nufais","makkah","aqsa"],(width,rows)
                assert sum(x["chosen"] for x in rows)==1 and next(x for x in rows if x["chosen"])["value"]==voice,(width,voice,rows)
                assert all(x["checkNodes"]==0 and x["tick"] in ("none","normal") and x["wave"]!="none" for x in rows),(width,voice,"stray check",rows)
            page.locator("#voicePickerList").screenshot(path=str(evidence/f"voices-{width}.png"))
            page.click("#voicePickerClose")
            assert not errors,(width,"JS errors",errors)
            checks.append({"width":width,"quran":True,"qibla":True,"locations":len(locations),"voices":4,"errors":0})
            page.close()
        browser.close()
    (evidence/"results.json").write_text(json.dumps({"passed":True,"checks":checks},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("PASS: four screenshot root-causes validated in Chromium at 360/390/768/1440",json.dumps(checks))
finally:
    server.shutdown()
