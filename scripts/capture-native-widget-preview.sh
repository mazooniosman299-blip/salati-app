#!/usr/bin/env bash
set -euo pipefail
python3 -m pip install --quiet Pillow
mkdir -p reports/native-widget
adb shell wm size 1080x2400
adb shell wm density 420
adb install -r android/app/build/outputs/apk/debug/app-debug.apk
adb shell am start -n com.salati.prayer/.WidgetPreviewActivity --es prayer maghrib
sleep 6
adb exec-out screencap -p > reports/native-widget/maghrib.png
adb shell uiautomator dump /sdcard/widget.xml
adb pull /sdcard/widget.xml reports/native-widget/maghrib.xml
adb shell am force-stop com.salati.prayer
adb shell am start -n com.salati.prayer/.WidgetPreviewActivity --es prayer asr
# The Android splash screen must finish BEFORE screenshot comparison.
for attempt in $(seq 1 15); do
  sleep 2
  adb shell uiautomator dump /sdcard/widget-asr.xml >/dev/null 2>&1 || true
  adb pull /sdcard/widget-asr.xml reports/native-widget/asr.xml >/dev/null 2>&1 || true
  if python3 -c "from xml.etree import ElementTree as ET;root=ET.parse('reports/native-widget/asr.xml');texts={n.attrib.get('text') for n in root.iter('node')};assert {'الفجر','العصر','المغرب','3:08','5:33'}.issubset(texts)" 2>/dev/null; then
    break
  fi
done
adb exec-out screencap -p > reports/native-widget/asr.png
python3 tests/native-widget-screenshot-contract.py
