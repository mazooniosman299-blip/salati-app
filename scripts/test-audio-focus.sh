#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd -- "$(dirname -- "$0")/.." && pwd)"
focus_build="$(mktemp -d)"
trap 'rm -rf -- "$focus_build"' EXIT
javac_bin="${JAVA_HOME:+$JAVA_HOME/bin/}javac"
java_bin="${JAVA_HOME:+$JAVA_HOME/bin/}java"
"$javac_bin" -d "$focus_build" "$project_root/android/app/src/main/java/com/salati/prayer/AudioFocusPolicy.java" "$project_root/tests/android/AudioFocusPolicyTest.java" "$project_root/android/app/src/main/java/com/salati/prayer/AlarmVolumePolicy.java" "$project_root/tests/android/AlarmVolumePolicyTest.java"
"$java_bin" -cp "$focus_build" com.salati.prayer.AudioFocusPolicyTest
"$java_bin" -cp "$focus_build" com.salati.prayer.AlarmVolumePolicyTest

"$javac_bin" -d "$focus_build" "$project_root/android/app/src/main/java/com/salati/prayer/AlarmDeliveryPolicy.java" "$project_root/tests/android/AlarmDeliveryPolicyTest.java"
"$java_bin" -cp "$focus_build" com.salati.prayer.AlarmDeliveryPolicyTest
