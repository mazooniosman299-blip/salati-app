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
sleep 7
adb exec-out screencap -p > reports/android-webview-20261102/mushaf.png
# Reader sits below the header/selection controls on compact displays.
# Swipe the real Android WebView and capture a separate parchment screenshot.
adb shell input swipe 216 755 216 315 580
sleep 3
adb exec-out screencap -p > reports/android-webview-20261102/mushaf-reader.png
adb logcat -d -t 1600 > reports/android-webview-20261102/logcat.txt
python3 tests/android-webview-pixel-qa-20261102.py
if grep -E 'FATAL EXCEPTION.*com.salati.prayer.preview|Process: com.salati.prayer.preview.*FATAL EXCEPTION' reports/android-webview-20261102/logcat.txt; then
  echo 'Android application crash found in logcat' >&2
  exit 1
fi
echo 'PASS Android 15 system WebView native screenshots and interaction'
