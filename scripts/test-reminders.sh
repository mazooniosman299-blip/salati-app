#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd -- "$(dirname -- "$0")/.." && pwd)"
reminder_build="$(mktemp -d)"
trap 'rm -rf -- "$reminder_build"' EXIT
sdk_root="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-}}"
sdk_jar="$sdk_root/platforms/android-36/android.jar"
if [ ! -f "$sdk_jar" ]; then echo "Set ANDROID_HOME to test against the actual Android36 SDK constants." >&2; exit 1; fi
"${JAVA_HOME:+$JAVA_HOME/bin/}javac" -cp "$sdk_jar" -d "$reminder_build" "$project_root/android/app/src/main/java/com/salati/prayer/FajrAnnouncementPolicy.java" "$project_root/tests/android/FajrAnnouncementPolicyTest.java" "$project_root/android/app/src/main/java/com/salati/prayer/WidgetAppearancePolicy.java" "$project_root/tests/android/WidgetAppearancePolicyTest.java"
"${JAVA_HOME:+$JAVA_HOME/bin/}java" -cp "$reminder_build" com.salati.prayer.FajrAnnouncementPolicyTest
"${JAVA_HOME:+$JAVA_HOME/bin/}java" -cp "$reminder_build" com.salati.prayer.WidgetAppearancePolicyTest
cd "$project_root"
python3 tests/arabic-speech-lifecycle.py
python3 tests/legacy-reminder-migration.py
python3 tests/first-install-permissions.py
