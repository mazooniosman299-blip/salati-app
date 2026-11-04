#!/usr/bin/env bash
# Actual original-certificate install-over-install evidence; no physical-phone claim.
set -euo pipefail
out=reports/mushaf1441-signed-upgrade
mkdir -p "$out"
adb shell wm size 432x960
adb shell wm density 160
adb install -r /tmp/salati-previous-123.apk
adb shell pm grant com.salati.prayer android.permission.POST_NOTIFICATIONS
adb shell pm grant com.salati.prayer android.permission.ACCESS_COARSE_LOCATION
adb shell pm grant com.salati.prayer android.permission.ACCESS_FINE_LOCATION
adb shell am start -n com.salati.prayer/com.salati.prayer.MainActivity
sleep 5
adb install -r /tmp/salati-candidate-126.apk
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
grep -E 'versionCode=127\b' "$out/package.txt"
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
printf '%s\n' 'PASS original-key127 update over124, package identity, permission persistence, real System WebView reader; physical phone NOT RUN'
