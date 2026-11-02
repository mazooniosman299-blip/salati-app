#!/usr/bin/env bash
# Real Android emulator install-over-install gate for ORIGINAL certificate.
# Called only after apksigner validated the exact v123 certificate and hash.
set -euo pipefail
set -x
OLD=/tmp/salati-previous-v122.apk
NEW=/tmp/salati-v123-signed/salati-1.0.123.apk
test -s "$OLD"
test -s "$NEW"
mkdir -p reports/salati-v123-release-candidate/native-upgrade
adb shell wm size 432x960
adb shell wm density 160
adb install -r "$OLD"
adb shell pm grant com.salati.prayer android.permission.POST_NOTIFICATIONS || true
adb shell pm grant com.salati.prayer android.permission.ACCESS_COARSE_LOCATION || true
adb shell am start -n com.salati.prayer/com.salati.prayer.MainActivity
sleep 5
# Android must ACCEPT replacement of the installed v122 original-key package.
# Same-package/different-key would cause INSTALL_FAILED_UPDATE_INCOMPATIBLE.
adb install -r "$NEW"
adb shell am force-stop com.salati.prayer || true
adb shell am start -n com.salati.prayer/com.salati.prayer.MainActivity
READY=0
for n in $(seq 1 40); do
  adb exec-out screencap -p > reports/salati-v123-release-candidate/native-upgrade/after-update.png
  if python3 tests/android-emulator-screen-preflight.py ready reports/salati-v123-release-candidate/native-upgrade/after-update.png; then
    READY=1; break
  fi
  if python3 tests/android-emulator-screen-preflight.py dialog reports/salati-v123-release-candidate/native-upgrade/after-update.png; then
    adb shell input tap 146 485
    adb shell am start -n com.salati.prayer/com.salati.prayer.MainActivity
  fi
  sleep 3
done
adb shell dumpsys package com.salati.prayer > reports/salati-v123-release-candidate/native-upgrade/package-after-update.txt
adb logcat -d -t 1800 > reports/salati-v123-release-candidate/native-upgrade/logcat.txt
test "$READY" -eq 1 || { echo "Updated signed Salati never displayed native UI" >&2; exit 1; }
grep -E 'versionCode=124\b' reports/salati-v123-release-candidate/native-upgrade/package-after-update.txt
if grep -E 'FATAL EXCEPTION.*com.salati.prayer|Process: com.salati.prayer.*FATAL EXCEPTION' reports/salati-v123-release-candidate/native-upgrade/logcat.txt; then
  echo 'Signed Salati crashed after in-place update' >&2; exit 1
fi
echo 'PASS original-key v122 -> v123 Android upgrade, package identity, interactive UI'
