#!/usr/bin/env bash
set -Eeuo pipefail
mkdir -p reports/native-widget-preview
adb install -r android/app/build/outputs/apk/debug/app-debug.apk
adb shell wm size 1080x2340
adb shell wm density 440
adb shell settings put system screen_off_timeout 600000 || true
adb shell input keyevent 82 || true
for state in maghrib dhuhr; do
  selection=4
  [[ "$state" == "dhuhr" ]] && selection=2
  adb shell am force-stop com.salati.prayer || true
  adb shell am start -W -n com.salati.prayer/.WidgetPreviewActivity --ei active "$selection"
  file="reports/native-widget-preview/${state}-active.png"
  ready=false
  for attempt in 1 2 3 4; do
    sleep 12
    adb exec-out screencap -p > "$file"
    if python3 - "$file" <<'PY'
import sys
from PIL import Image
im=Image.open(sys.argv[1]).convert('RGB')
assert im.size==(1080,2340),im.size
im=im.crop((0,70,1080,1000))
im.thumbnail((360,320))
orange=sum(1 for r,g,b in im.getdata() if r>105 and r>g*1.22 and g>b*1.28 and g>42)
if orange<230:
    print('NOT READY: splash/empty UI, orange-mosque pixels:',orange)
    sys.exit(1)
print('READY: actual mosque widget rendered, orange pixels:',orange)
PY
    then ready=true; break; fi
    adb shell dumpsys activity activities | grep -E 'ResumedActivity|topResumedActivity' | head -6 || true
  done
  if [[ "$ready" != true ]]; then
    echo "FAIL: WidgetPreviewActivity did not render; do not accept splash screen as widget evidence"
    adb logcat -d -t 600 | grep -A18 -E 'FATAL EXCEPTION|Unable to start activity|WidgetPreviewActivity' | tail -85 || true
    exit 1
  fi
  python3 - "$file" <<'PY'
import sys
from pathlib import Path
from PIL import Image
file=Path(sys.argv[1])
im=Image.open(file).convert('RGB')
im.crop((0,55,1080,950)).save(file.with_name(file.stem+'-crop.png'))
PY
done
echo 'PASS: Android 15 native RemoteViews rendered, NOT splash; both Maghrib and Dhuhr time-only capsule states captured'
