#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd -- "$(dirname -- "$0")/.." && pwd)"
reminder_build="$(mktemp -d)"
trap 'rm -rf -- "$reminder_build"' EXIT
"${JAVA_HOME:+$JAVA_HOME/bin/}javac" -d "$reminder_build" "$project_root/android/app/src/main/java/com/salati/prayer/ApproachPolicy.java" "$project_root/tests/android/ApproachPolicyTest.java" "$project_root/android/app/src/main/java/com/salati/prayer/WidgetAppearancePolicy.java" "$project_root/tests/android/WidgetAppearancePolicyTest.java"
"${JAVA_HOME:+$JAVA_HOME/bin/}java" -cp "$reminder_build" com.salati.prayer.ApproachPolicyTest
"${JAVA_HOME:+$JAVA_HOME/bin/}java" -cp "$reminder_build" com.salati.prayer.WidgetAppearancePolicyTest
cd "$project_root"
python3 tests/arabic-speech-lifecycle.py
python3 tests/approach-scheduling.py
python3 tests/first-install-permissions.py
