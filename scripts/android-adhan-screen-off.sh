#!/usr/bin/env bash
# Fresh disposable CI emulator only. Never run against a user's phone/data.
set -euo pipefail
out=reports/adhan-screen-off
mkdir -p "$out"
pkg=com.salati.prayer.preview
adb install -r android/app/build/outputs/apk/debug/app-debug.apk
adb install -r android/app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk
uid="$(adb shell cmd package list packages -U "$pkg" | tr -d '\r' | sed -n "s/^package:$pkg uid:\([0-9]*\)$/\1/p")"
test -n "$uid"
for pair in fajr:nufais dhuhr:qatami asr:makkah maghrib:aqsa isha:nufais; do
 prayer="${pair%%:*}"; voice="${pair#*:}"
 adb shell dumpsys deviceidle unforce >/dev/null
 adb shell input keyevent KEYCODE_WAKEUP
 # Isolate native delivery from a prior UI trial's WebView/localStorage and
 # lifecycle callbacks. This is a disposable emulator, never user data.
 adb shell pm clear "$pkg" >/dev/null
 adb shell pm grant "$pkg" android.permission.POST_NOTIFICATIONS
 adb shell appops set "$pkg" SCHEDULE_EXACT_ALARM allow
 adb shell am instrument -w -r -e prayer "$prayer" -e voice "$voice" "$pkg.test/com.salati.prayer.AlarmDeliveryInstrumentation" > "$out/$prayer-prepare.txt"
 cat "$out/$prayer-prepare.txt"
 adb shell dumpsys alarm > "$out/$prayer-alarms-after-prepare.txt"
 grep -F 'INSTRUMENTATION_CODE: -1' "$out/$prayer-prepare.txt"
 adb shell run-as "$pkg" cat shared_prefs/salati_background.xml > "$out/$prayer-prepared-prefs.xml"
 python3 - "$out" "$prayer" <<'PYSETUP'
import sys,re,xml.etree.ElementTree as ET
from pathlib import Path
out=Path(sys.argv[1]);prayer=sys.argv[2]
expected=int(re.search(r'scheduledTime=(\d+)',(out/(prayer+'-prepare.txt')).read_text())[1])
root=ET.parse(out/(prayer+'-prepared-prefs.xml')).getroot()
prefs={e.attrib['name']:e.text if e.tag=='string' else e.attrib.get('value') for e in root}
assert prefs.get('nextAlarmPrayer')==prayer and int(prefs.get('nextAlarmTime',0))==expected,('Native setup lost its pending alarm before cold test',prefs)
PYSETUP
 adb shell input keyevent KEYCODE_HOME
 adb shell am kill "$pkg"
 adb shell dumpsys battery unplug >/dev/null
 adb shell input keyevent KEYCODE_SLEEP
 adb shell dumpsys deviceidle force-idle > "$out/$prayer-idle.txt"
 adb shell dumpsys deviceidle >> "$out/$prayer-idle.txt"
 sleep 17
 delivered=0
 for attempt in $(seq 1 8); do
  adb shell run-as "$pkg" cat shared_prefs/salati_background.xml > "$out/$prayer-prefs.xml"
  adb shell dumpsys audio > "$out/$prayer-audio.txt"
  adb shell dumpsys activity services "$pkg" > "$out/$prayer-services.txt"
  if python3 - "$out" "$prayer" "$uid" <<'PY'
import sys,re,xml.etree.ElementTree as ET
from pathlib import Path
folder=Path(sys.argv[1]);prayer=sys.argv[2];uid=sys.argv[3]
root=ET.parse(folder/(prayer+'-prefs.xml')).getroot()
prefs={e.attrib['name']:e.text if e.tag=='string' else e.attrib.get('value') for e in root}
assert prefs.get('deliveryStatus')=='playing',prefs
assert prefs.get('last','').startswith(prayer),prefs
assert prefs.get('nextAlarmMode')=='exact',prefs
assert int(prefs['nextAlarmTime'])>int(prefs['deliveryAt']),prefs
audio=(folder/(prayer+'-audio.txt')).read_text()
lines=[line for line in audio.splitlines() if re.search(r'\b'+re.escape(uid)+r'\b',line)]
assert any('state:started' in line and 'USAGE_ALARM' in line and 'mutedState:none' in line for line in lines),('No started unmuted real alarm AudioTrack for app UID',lines)
assert 'AdhanService' in (folder/(prayer+'-services.txt')).read_text(),'Actual native adhan service not running'
print('PASS cold-process/screen-off/Doze actual',prayer,'receiver -> foreground service -> started USAGE_ALARM AudioTrack; next alarm scheduled')
PY
  then delivered=1; break; fi
  sleep 2
 done
 if [ "$delivered" -ne 1 ]; then
  adb logcat -d -t 1600 > "$out/$prayer-failure-logcat.txt"
  adb shell dumpsys alarm > "$out/$prayer-alarms-at-failure.txt"
  adb shell cmd appops get "$pkg" TAKE_AUDIO_FOCUS > "$out/$prayer-focus-appops.txt"
  cat "$out/$prayer-focus-appops.txt"
  cat "$out/$prayer-prefs.xml" "$out/$prayer-alarms-after-prepare.txt" "$out/$prayer-alarms-at-failure.txt"
  cat "$out/$prayer-audio.txt" "$out/$prayer-services.txt"
  exit 1
 fi
 adb shell am force-stop "$pkg"
done
adb shell dumpsys deviceidle unforce >/dev/null
adb shell dumpsys battery reset >/dev/null
adb shell input keyevent KEYCODE_WAKEUP
printf '%s\n' 'PASS all5 native scheduled prayers and all4 packaged recordings in a cold process with screen off/Doze. Emulator playback-state evidence, not physical-phone audition.'
