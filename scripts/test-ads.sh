#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd -- "$(dirname -- "$0")/.." && pwd)"
ads_build="$(mktemp -d)"
trap 'rm -rf -- "$ads_build"' EXIT
"${JAVA_HOME:+$JAVA_HOME/bin/}javac" -d "$ads_build" "$project_root/android/ads/src/main/java/com/salati/ads/AdInitialization.java" "$project_root/android/ads/src/main/java/com/salati/ads/AdVisibility.java" "$project_root/tests/ads/AdInitializationTest.java" "$project_root/tests/ads/AdVisibilityTest.java"
"${JAVA_HOME:+$JAVA_HOME/bin/}java" -cp "$ads_build" com.salati.ads.AdInitializationTest
"${JAVA_HOME:+$JAVA_HOME/bin/}java" -cp "$ads_build" com.salati.ads.AdVisibilityTest
