#!/usr/bin/env bash
set -euo pipefail
task_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
task_classes="$(mktemp -d)"
trap 'rm -rf "$task_classes"' EXIT
task_javac="${JAVA_HOME:+$JAVA_HOME/bin/}javac"
task_java="${JAVA_HOME:+$JAVA_HOME/bin/}java"
"$task_javac" -d "$task_classes" "$task_root/android/app/src/main/java/com/salati/prayer/QuranAudioRange.java" "$task_root/android/app/src/main/java/com/salati/prayer/QuranAudioFiles.java" "$task_root/tests/android/QuranAudioRangeTest.java"
"$task_java" -cp "$task_classes" com.salati.prayer.QuranAudioRangeTest
