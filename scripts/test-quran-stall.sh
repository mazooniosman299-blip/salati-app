#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd -- "$(dirname -- "$0")/.." && pwd)"
stall_build="$(mktemp -d)"
trap 'rm -rf -- "$stall_build"' EXIT
"${JAVA_HOME:+$JAVA_HOME/bin/}javac" -d "$stall_build" "$project_root/android/app/src/main/java/com/salati/prayer/PlaybackWatchdog.java" "$project_root/tests/android/PlaybackWatchdogTest.java"
"${JAVA_HOME:+$JAVA_HOME/bin/}java" -cp "$stall_build" com.salati.prayer.PlaybackWatchdogTest
