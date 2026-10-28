#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd -- "$(dirname -- "$0")/.." && pwd)"
quran_build="$(mktemp -d)"
trap 'rm -rf -- "$quran_build"' EXIT
"${JAVA_HOME:+$JAVA_HOME/bin/}javac" -d "$quran_build" "$project_root/android/app/src/main/java/com/salati/prayer/QuranPlaylist.java" "$project_root/tests/android/QuranPlaylistTest.java"
"${JAVA_HOME:+$JAVA_HOME/bin/}java" -cp "$quran_build" com.salati.prayer.QuranPlaylistTest
