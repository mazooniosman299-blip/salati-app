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
sleep 12
# Avoid a false negative when Android shows a Pixel Launcher ANR dialog in
# front of the otherwise healthy app. Determine it from native screenshot.
for attempt in 1 2 3 4; do
  adb exec-out screencap -p > /tmp/salati-boot-check.png
  if python3 tests/android-emulator-screen-preflight.py dialog /tmp/salati-boot-check.png; then
    adb shell input tap 146 485
    sleep 3
    adb shell am start -n com.salati.prayer.preview/com.salati.prayer.MainActivity
    sleep 2
  else
    break
  fi
done
adb exec-out screencap -p > reports/android-webview-20261102/times.png
read -r quran_x quran_y < <(python3 tests/android-emulator-screen-preflight.py quran-tap reports/android-webview-20261102/times.png)
test -n "$quran_x" && test -n "$quran_y"
adb shell input tap "$quran_x" "$quran_y"
sleep 7
adb exec-out screencap -p > reports/android-webview-20261102/mushaf.png
adb logcat -d -t 1600 > reports/android-webview-20261102/logcat.txt
python3 tests/android-webview-pixel-qa-20261102.py
if grep -E 'FATAL EXCEPTION.*com.salati.prayer.preview|Process: com.salati.prayer.preview.*FATAL EXCEPTION' reports/android-webview-20261102/logcat.txt; then
  echo 'Android application crash found in logcat' >&2
  exit 1
fi
echo 'PASS Android 15 system WebView native screenshots and interaction'
