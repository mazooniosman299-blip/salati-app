# Selected-reference web skin review

Read-only review of the current `/workspace/sites/salati-source` working tree, release 1.0.102 / shell cache 136. No application edits or publication. No confirmed functional blocker found in the inspected web skin.

## Reviewed changes

- `dist/reference-layout.css`: shared prayer-overview surface, mobile six-prayer strip, rectangular navigation targets and selection, compact Quran player, captions, next-prayer icon, reduced-transparency fallback.
- `dist/index.html`: retained unique runtime IDs; location/hero/prayers inside one overview; moved qTrack and qStop; hidden compatibility qPlay; visible qTransport retained; pending original photo explicitly hidden without a substituted image.
- `app-source.js:40–41`: dark browser theme-color and real next-prayer icon updates, including hiding the icon when location/times are unavailable. Schedule/date/countdown calculations remain intact.
- `glass-navigation.js:15`: target-relative selection rectangle using inset 4px and target dimensions minus 8px; existing resize, direction/language and reduced-motion handling retained.
- `scripts/build-navigation.cjs`, `scripts/build-web.cjs`, `scripts/prepare-android.py`, `dist/sw.js`: selected Phosphor symbols, four versioned stylesheets, fourth CSS family retained by APK packager, new stylesheet/location icon included in shell precache.
- Shared theme and component CSS layers, new targeted tests, and existing Quran transport event handlers in `quran-controller.js`.

## Verification

Passed independently in this review:

- `python3 tests/reference-widget.py`: one live overview, six aligned prayer cells, single visible primary transport, rectangular marker geometry, no horizontal page overflow across 320/390/600/760/1024/1440px and both themes.
- `python3 tests/modern-instruments.py`: all six tabs, both themes, same-tab RTL/LTR geometry, menu keyboard/focus behavior, Quran switches, enabled/disabled control contrast, tasbih controls, reduced motion/transparency and crisp Quran text. No page errors.
- `python3 tests/offline-navigation.py`: controlled offline Chromium Arabic/English deep links return to a bootable cached root and Quran content loads with the new CSS release.
- `node tests/fresh-review-regressions.cjs`, `node tests/quran.cjs`, `node tests/tab-controls.cjs`, `node tests/reference-theme.cjs`, `node tests/light-theme.cjs`.
- Additional external browser probe `/workspace/salati-fix/203/playback-probe.py`: English Times layout at 320px, then visible Quran transport starts, pauses, resumes and stops recitation. Stop becomes visible during playback, clears the source and disappears after stopping. Media output was mocked; this verifies event/control wiring, not recording delivery or audio quality.

Inspected the rendered dark mobile Times screenshot produced by the browser checks. Location, live dates, current next-prayer label/icon, countdown, six-cell strip and bottom navigation remain legible and inside the viewport. The unavailable original photograph is not rendered or claimed complete. Desktop reserves the intended centre scene region; final photograph fit cannot be reviewed until the user supplies the original image.

## Remaining limitations

No runtime or cascade blocker was reproduced. Tests verify measured layout and behavior, not exact visual equivalence to every pixel of the selected reference. The photo remains a known unfinished asset dependency, as explicitly requested. Audio hardware/background Android behavior and final APK visual rendering are outside this web-skin review; packager source references were checked without rebuilding or modifying the APK.
