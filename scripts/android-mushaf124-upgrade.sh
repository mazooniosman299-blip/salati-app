#!/usr/bin/env bash
# Actual original-certificate install-over-install evidence; no physical-phone claim.
set -euo pipefail
out=reports/mushaf1441-signed-upgrade
mkdir -p "$out"
adb shell wm size 432x960
adb shell wm density 160
adb install -r /tmp/salati-previous-130.apk
adb shell pm grant com.salati.prayer android.permission.POST_NOTIFICATIONS
adb shell pm grant com.salati.prayer android.permission.ACCESS_COARSE_LOCATION
adb shell pm grant com.salati.prayer android.permission.ACCESS_FINE_LOCATION
adb shell am start -n com.salati.prayer/com.salati.prayer.MainActivity
sleep 5
adb install -r /tmp/salati-candidate-131.apk
adb shell am force-stop com.salati.prayer
adb shell am start -n com.salati.prayer/com.salati.prayer.MainActivity
ready=0
for attempt in $(seq 1 40); do
  adb exec-out screencap -p > "$out/after-upgrade.png"
  if python3 tests/android-emulator-screen-preflight.py ready "$out/after-upgrade.png"; then ready=1; break; fi
  if python3 tests/android-emulator-screen-preflight.py dialog "$out/after-upgrade.png"; then
    adb shell input tap 146 485
    adb shell am start -n com.salati.prayer/com.salati.prayer.MainActivity
  fi
  sleep 3
done
if [ "$ready" -ne 1 ]; then
  adb shell uiautomator dump /sdcard/salati-upgrade-failure.xml || true
  adb shell cat /sdcard/salati-upgrade-failure.xml || true
  adb logcat -d -t 1600 > "$out/logcat.txt"
  adb shell dumpsys activity activities > "$out/activity.txt"
  echo 'FAIL signed update: real UI never became ready; hierarchy and screenshot retained' >&2
  exit 1
fi
adb shell dumpsys package com.salati.prayer > "$out/package.txt"
grep -E 'versionCode=132\b' "$out/package.txt"
grep -F 'android.permission.POST_NOTIFICATIONS: granted=true' "$out/package.txt"
read -r x y < <(python3 tests/android-emulator-screen-preflight.py quran-tap "$out/after-upgrade.png")
adb shell input tap "$x" "$y"
ready=0
for attempt in $(seq 1 30); do
  adb exec-out screencap -p > "$out/mushaf.png"
  if python3 tests/android-emulator-screen-preflight.py quran-ready "$out/mushaf.png"; then ready=1; break; fi
  sleep 2
done
test "$ready" -eq 1
adb logcat -d -t 2000 > "$out/logcat.txt"
if grep -E 'FATAL EXCEPTION.*com.salati.prayer|Process: com.salati.prayer.*FATAL EXCEPTION' "$out/logcat.txt"; then exit 1; fi
printf '%s\n' 'PASS original-key1.0.131/code132 update over1.0.130/code131, package identity, permission persistence, real System WebView reader; physical phone NOT RUN'

# Actual launcher drawer; a home screenshot without Salati is not icon evidence.
adb shell input keyevent KEYCODE_HOME
sleep 1
for attempt in $(seq 1 5); do
  if [ "$attempt" -eq 1 ]; then adb shell input keyevent KEYCODE_ALL_APPS; else adb shell input swipe 216 800 216 250 450; fi
  sleep 2
  adb shell uiautomator dump /sdcard/salati-launcher.xml >/dev/null 2>&1 || true
  adb shell cat /sdcard/salati-launcher.xml > "$out/launcher.xml" || true
  adb exec-out screencap -p > "$out/launcher-drawer.png"
  if python3 - "$out/launcher.xml" <<'PYINNER'
import sys,xml.etree.ElementTree as ET
root=ET.parse(sys.argv[1]).getroot()
assert any('صلاتي' in (e.get('text','')+' '+e.get('content-desc','')) for e in root.iter('node')),'Salati must actually be visible in launcher'
PYINNER
  then break; fi
done
python3 tests/android-emulator-screen-preflight.py evidence "$out/launcher-drawer.png"
python3 - "$out" <<'PYINNER'
import sys,xml.etree.ElementTree as ET,re,base64
from pathlib import Path
from PIL import Image
out=Path(sys.argv[1]);root=ET.parse(out/'launcher.xml').getroot()
nodes=[e for e in root.iter('node') if 'صلاتي' in (e.get('text','')+' '+e.get('content-desc',''))]
assert nodes,'No real visible Salati launcher icon captured'
with Image.open(out/'launcher-drawer.png') as im:
 boxes=[]
 for e in nodes:
  nums=list(map(int,re.findall(r'\d+',e.get('bounds',''))))
  if len(nums)==4 and nums[2]>nums[0] and nums[3]>nums[1]:boxes.append(nums)
 assert boxes,'Visible launcher node needs real bounds'
 x0,y0,x1,y1=max(boxes,key=lambda b:(b[2]-b[0])*(b[3]-b[1]))
 im.crop((max(0,x0-8),max(0,y0-8),min(im.width,x1+8),min(im.height,y1+8))).save(out/'launcher-salati-actual.png')
print('SALATI_SCREENSHOT_PNG_BASE64='+base64.b64encode((out/'launcher-salati-actual.png').read_bytes()).decode())
PYINNER
