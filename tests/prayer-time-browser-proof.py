#!/usr/bin/env python3
"""Real Playwright screenshots of the exact built Salati web runtime, not mockups."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from pathlib import Path
from functools import partial
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright
import json, os

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"reports/prayer-calendar-real"
OUT.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args): pass
server=ThreadingHTTPServer(("127.0.0.1",0),partial(Quiet,directory=str(ROOT/"dist")))
Thread(target=server.serve_forever,daemon=True).start()
CASES=[
 ("muscat-ar","ar",23.588,58.3829,"Asia/Muscat","Oman","Shafi",["4:59","6:16","11:56","3:07 م","5:30 م","6:42 م"]),
 ("muscat-en","en",23.588,58.3829,"Asia/Muscat","Oman","Shafi",["4:59 AM","6:16 AM","11:56 AM","3:07 PM","5:30 PM","6:42 PM"]),
 ("singapore-ar","ar",1.3521,103.8198,"Asia/Singapore","Singapore","Shafi",["5:27","6:47","12:50 م","4:11 م","6:51 م","8:03 م"]),
 ("singapore-en","en",1.3521,103.8198,"Asia/Singapore","Singapore","Shafi",["5:27 AM","6:47 AM","12:50 PM","4:11 PM","6:51 PM","8:03 PM"]),
 ("kuala-lumpur-ar","ar",3.139,101.6869,"Asia/Kuala_Lumpur","Jakim","Shafi",["5:48","6:56","1:00 م","4:21 م","6:58 م","8:10 م"]),
 ("kuala-lumpur-en","en",3.139,101.6869,"Asia/Kuala_Lumpur","Jakim","Shafi",["5:48 AM","6:56 AM","1:00 PM","4:21 PM","6:58 PM","8:10 PM"]),
 ("cairo-ar","ar",30.0444,31.2357,"Africa/Cairo","Egyptian","Shafi",["4:45","6:13","11:39","2:41 م","5:03 م","6:23 م"]),
 ("cairo-en","en",30.0444,31.2357,"Africa/Cairo","Egyptian","Shafi",["4:45 AM","6:13 AM","11:39 AM","2:41 PM","5:03 PM","6:23 PM"])
]
RESULT=[]
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
  for name,lang,lat,lon,zone,method,madhab,expected in CASES:
   page=browser.new_page(viewport={"width":390,"height":844},device_scale_factor=1,service_workers="block",reduced_motion="reduce")
   page.clock.set_fixed_time(datetime(2026,11,7,8,0,tzinfo=timezone.utc))
   state={"lang":lang,"lat":lat,"lon":lon,"zone":zone,"zoneMode":"auto","name":("Muscat" if method=="Oman" else ("Kuala Lumpur" if method=="Jakim" else ("Cairo" if method=="Egyptian" else "Singapore"))),"method":method,"methodPreferenceVersion":1,"madhab":madhab,"locationMode":"manual","locationSet":True,"adjustments":{"fajr":0,"sunrise":0,"dhuhr":0,"asr":0,"maghrib":0,"isha":0}}
   page.add_init_script("localStorage.setItem('salati', "+json.dumps(json.dumps(state))+");")
   page_errors=[]
   page.on("pageerror",lambda exc: page_errors.append(str(exc)))
   resp=page.goto(f"http://127.0.0.1:{server.server_port}/",wait_until="domcontentloaded",timeout=35000)
   assert resp and resp.ok,(name,"homepage unavailable")
   page.wait_for_function("document.querySelectorAll('#prayers .prayer').length===6",timeout=30000)
   actual=[x.strip() for x in page.locator("#prayers .prayer strong").all_text_contents()]
   assert actual==expected, f"{name}: actual UI {actual}, expected {expected}"
   note=page.locator("#prayerSourceDisclaimer").inner_text()
   if lang=="ar":
    assert "التقويم الرسمي" in note and "فلكيًا" in note,(name,"incorrect source note",note)
   else:
    assert "official" in note and "astronomically" in note,(name,"incorrect source note",note)
   assert not page_errors,(name,page_errors)
   file=OUT/(name+".png")
   page.screenshot(path=str(file),animations="disabled",full_page=False)
   assert file.stat().st_size>10000,(name,"screenshot seems empty")
   RESULT.append({"case":name,"url":page.url,"tested_utc":"2026-11-07T08:00:00Z","local_zone":zone,"display":actual,"screenshot":file.name,"real_browser":"Playwright Chromium","no_prod_deploy":True})
   page.close()
  browser.close()
finally:
 server.shutdown()
 server.server_close()
(OUT/"verified-browser-results.json").write_text(json.dumps(RESULT,ensure_ascii=False,indent=2)+"\n")
print("PASS: actual Salati DOM and screenshots; Muscat/Singapore/Kuala Lumpur/Cairo official local times in Arabic and English with 12-hour display.")
