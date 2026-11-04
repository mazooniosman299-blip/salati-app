#!/usr/bin/env bash
# Executed as ONE command by reactivecircus/android-emulator-runner,
# which invokes each workflow "script" line through /usr/bin/sh -c.
# All loops and positional arguments belong within this Bash process.
set -euo pipefail
set -x
mkdir -p reports/android-webview-20261102
adb shell wm size 432x960
adb shell wm density 160
adb install -r android/app/build/outputs/apk/debug/app-debug.apk
adb shell pm grant com.salati.prayer.preview android.permission.POST_NOTIFICATIONS || true
adb shell pm grant com.salati.prayer.preview android.permission.ACCESS_FINE_LOCATION || true
adb shell pm grant com.salati.prayer.preview android.permission.ACCESS_COARSE_LOCATION || true
adb shell am start -n com.salati.prayer.preview/com.salati.prayer.MainActivity
# Startup is async. A fixed 12-second sleep captured only Salati's
# splash logo in actual CI evidence; poll for the real blue bottom navigation.
sleep 5
READY=0
for attempt in $(seq 1 42); do
  adb exec-out screencap -p > /tmp/salati-boot-check.png
  if python3 tests/android-emulator-screen-preflight.py ready /tmp/salati-boot-check.png; then
    READY=1
    break
  fi
  if python3 tests/android-emulator-screen-preflight.py dialog /tmp/salati-boot-check.png; then
    adb shell input tap 146 485
    sleep 2
    adb shell am start -n com.salati.prayer.preview/com.salati.prayer.MainActivity
  fi
  echo "Waiting for Salati UI: attempt ${attempt}/42" >&2
  sleep 3
done
if [ "$READY" -ne 1 ]; then
  cp /tmp/salati-boot-check.png reports/android-webview-20261102/times.png
  adb logcat -d -t 2500 > reports/android-webview-20261102/logcat.txt || true
  adb shell dumpsys activity activities > reports/android-webview-20261102/activity.txt || true
  echo "Salati never passed splash; native UI not ready after bounded polling" >&2
  exit 1
fi
adb exec-out screencap -p > reports/android-webview-20261102/times.png
read -r quran_x quran_y < <(python3 tests/android-emulator-screen-preflight.py quran-tap reports/android-webview-20261102/times.png)
test -n "$quran_x" && test -n "$quran_y"
adb shell input tap "$quran_x" "$quran_y"
# Android System WebView may create/select Quran controls before the async
# local 604-page source has finished loading. A fixed 7s sleep captured
# "جار فتح المصحف..." with NO cream reading page and falsely failed QA.
QURAN_READY=0
for attempt in $(seq 1 45); do
  sleep 2
  adb exec-out screencap -p > /tmp/salati-quran-ready.png
  if python3 tests/android-emulator-screen-preflight.py quran-ready /tmp/salati-quran-ready.png; then
    QURAN_READY=1
    break
  fi
  echo "Waiting for real rendered Quran parchment: $attempt/45" >&2
done
if [ "$QURAN_READY" -ne 1 ]; then
  cp /tmp/salati-quran-ready.png reports/android-webview-20261102/mushaf.png
  adb logcat -d -t 2500 > reports/android-webview-20261102/logcat.txt || true
  adb shell uiautomator dump /sdcard/salati-failed-reader.xml || true
  adb shell cat /sdcard/salati-failed-reader.xml || true
  adb shell dumpsys activity activities | tail -35 || true
  python3 tests/android-emulator-screen-preflight.py evidence /tmp/salati-quran-ready.png
  echo 'FAIL: real Quran parchment never appeared before 90-second deadline' >&2
  exit 1
fi
adb exec-out screencap -p > reports/android-webview-20261102/mushaf.png
# Read the visible parchment region from the ACTUAL screenshot. The hard-coded
# swipe at y=520 tapped a reciter picker on 432x960 and produced a false
# reading-panel absence. Never substitute a passed mock or disable real QA.
READER_OK=0
for attempt in 1 2 3; do
  adb exec-out screencap -p > /tmp/salati-reader-before.png
  if ! read -r sx sy ey < <(python3 tests/android-emulator-screen-preflight.py reader-swipe /tmp/salati-reader-before.png); then
    echo "No safe parchment swipe detected, attempt $attempt" >&2
    break
  fi
  adb shell input swipe "$sx" "$sy" "$sx" "$ey" 650
  sleep 2
  adb exec-out screencap -p > reports/android-webview-20261102/mushaf-reader.png
  if python3 tests/android-webview-pixel-qa-20261102.py; then
    READER_OK=1
    break
  fi
  cp reports/android-webview-20261102/mushaf-reader.png "reports/android-webview-20261102/mushaf-reader-attempt-$attempt.png"
  echo "Reader remained obscured after swipe $attempt; dismissing possible overlay and rechecking real Quran parchment" >&2
  adb shell input keyevent 4
  sleep 1
done
adb logcat -d -t 1600 > reports/android-webview-20261102/logcat.txt
python3 tests/android-emulator-screen-preflight.py evidence reports/android-webview-20261102/mushaf.png
if [ "$READER_OK" -ne 1 ]; then
  echo "FAIL: Quran reading parchment not visible after three real Android gestures" >&2
  exit 1
fi
if grep -E 'FATAL EXCEPTION.*com.salati.prayer.preview|Process: com.salati.prayer.preview.*FATAL EXCEPTION' reports/android-webview-20261102/logcat.txt; then
  echo 'Android application crash found in logcat' >&2
  exit 1
fi
echo 'PASS Android 15 system WebView native screenshots and interaction'
