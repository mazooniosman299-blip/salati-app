# Active source and generated-file map
Inspected from `production@f47ca69` on 2026-11-03. Do not infer actual usage solely from filenames.

| Surface / behavior | Runtime entry | Edit upstream source (when appropriate) | Verify |
|---|---|---|---|
| Six-tab web shell and controls | `dist/index.html` | `dist/index.html` + component sources | Real DOM ids, screenshots |
| Main web CSS | linked `dist/salati-ui.css` only | `dist/salati-ui.css` after selector/cascade audit | computedStyle and geometry across screens |
| Application logic | `dist/app-v1.0.109.js` currently linked despite v1.0.123 release | `app-source.js` and its imports | `node scripts/build-web.cjs`, reload, tab/lang/state |
| Quran reader/text | `#qSheet`, `#qVerses`, `#mushafPlayerSlot` | `quran-controller.js`, `quran-page-audio.js`, `app-source.js`, `dist/index.html` | Quran content integrity, scroll, player nonoverlap |
| Quran data | `dist/quran/data.json` and timings | Verify authoritative origin/rights before changes | Verse order and hashes; don't alter religious text |
| Prayer times / settings | DOM `#times`; JS bundle | `prayer-engine.js`, `prayer-preferences.js`, `settings-restore.js`, `location-startup.js` | AR/EN, timezone, persistence, offline |
| Adhkar / Tasbih / Qibla | `#dhikr`, `#tasbih`, `#qibla` | `adhkar-controller.js`, related tasbih sources, `compass.js` | Each tab functionality |
| Android WebView | `MainActivity.java` and packaged web assets | `android/app/src/main/`, `scripts/prepare-android.py` | emulator AND physical device where accessible |
| Native widget | Android `PrayerWidget.java`, `prayer_widget.xml` | Android native sources and `widget_reference_mosque.png` | real widget screenshot & resize |
| Web build | browser bundle + pages | `scripts/build-web.cjs` (esbuild) | loaded filename/hash after build |
| Cloudflare publication | Pages deployment | `scripts/build-cloudflare-pages.cjs`, `scripts/release-guard.cjs`, workflows | exact original-key signed APK/web fingerprint, CI SHA |
| Visual original assets | mosque/reference files | `design-references/`, `docs/design/`, `dist/images/` | provenance, license, original SHA |
| Historical assets | named `-v1.0.x` styles/scripts, older tests/previews | do NOT edit as first instinct | verify link/CI use before classifying |

## Known deceptive names
- `README.md` historically asserted version 1.0.116 although `apk-release-parts/current.json` says 1.0.123.
- `docs/github-source.json` says version 1.0.109 as historical provenance; not a current release pointer.
- The linked JS bundle name `app-v1.0.109.js` is historical and is rebuilt by esbuild; it does not equal the signed APK release version.
- `tests/preview-four-ui-changes-browser.py` asserts `preview-four-ui-changes-20261101.css` is linked, while current HTML links only `salati-ui.css`; this is PREVIEW-HISTORICAL and must not be promoted to current production acceptance.
- Existing `tests/design-restoration-contract.cjs` and `tests/permanent-regression-contract.cjs` validate aspects of the production shell/signature, but cannot prove reference image fidelity.

## Priority of test suites
CORE: `npm test`, `tests/permanent-regression-contract.cjs`, `scripts/release-guard.cjs` (do not weaken).
PRODUCTION browser: `tests/active-production-browser-20261102.py`, `tests/mobile-layout-contract-20261101.py` (recheck current user approval if asserting visual layout).
CSS audit: `tests/css-component-owner-audit.py`, `tests/canonical-css-maintainability.py`.
PREVIEW-HISTORICAL: old preview-only scripts testing separate CSS files or alternate player placement. Run only under their specified preview branch/asset condition.
ANDROID: `tests/android-webview-pixel-qa-20261102.py`, `scripts/android-webview-smoke.sh`, native tests. No physical-device claim from emulator.

Mushaf1441 integration source: `quran-printed-pages.js` enhances QuranReader pages with original local images and calibrated SVG hit regions under `dist/quran/printed-1441/`. `quran-controller.js` owns direct ayah selection and dynamic `#qTrackTitle`; `quran-page-audio.js` owns full-file initial cue playback. Canonical text remains the fallback. No standalone preview app replaces production.

Candidate126 decoration owner: quran-printed-pages.js inserts .printed-opening-title for pages1/2 and the .printed-page-index. dist/salati-ui.css scopes original borders/header/cartouche to #mushaf.printed-reader. Exact sources/licenses/hashes live in dist/quran/printed-1441/ornaments/SOURCES.json and licenses/ORNAMENTS-NOTICE.md. Original image bytes and calibrated regions unchanged. SW183 precaches five decorative assets; canonical native packaging retains them locally.

Fatiha-entry owner: QuranReader.enterAtSurahStart in quran-controller.js, called without a surah by app-source.js on explicit Mushaf tab entry. Visibility resume passes the current surah. QuranReader.go increments reading-navigation intent so an older pending entry cannot overwrite a newer explicit surah/bookmark choice. No CSS or original Quran data/art changes.

##4Nov2026 home-reference steering
Home-reference owner: #times .home-dashboard in index.html and salati-ui.css; app-source.js render/tick own real next-prayer clock, AM/PM and six calculated cards. Native PrayerWidget.java/XML/resources untouched. Requested white text owners: printed-reader #qTrack, #qibla .eyebrow and #androidDownload>p. See requests/SALATI-20261104-HOME-REFERENCE.md.

##4Nov continuation/action-dock/launcher steering
New continuation/dock owners: QuranReader constructor/save and completion callback, setupVerseActions; scoped printed-reader dock CSS. Native playlist already supports autoNext. Android launcher uses ic_salati adaptive resources; shared uses must be checked before replacing launcher-only art. See requests/SALATI-20261104-QURAN-CONTINUATION-ACTION-ICON.md.

##4Nov latest correction: remove unpublished action dock
User explicitly rejects extra Pause/Surah start/Bookmark/Close actions; this supersedes the earlier contextual-dock clarification. Restore exact production128 reader/player UI, retain only continuation behavior. First displayed crescent/minaret launcher chosen with black background removed; revised transparent artwork must be verified. No extra UI features authorized.

##5Nov pointer-focus correction
Latest user points out the black rounded box enclosing a selected ayah. Actual129 reproduction confirms browser UAauto5px outline on:focus without:focus-visible. Fix only.printed-ayah common outline reset; retain the existing brown keyboard path stroke/selection/full-file audio. No extra actions or redesign. Source ownerdist/salati-ui.css printed-reader component; requestSALATI-20261105-AYAH-POINTER-FOCUS.

##5Nov Fajr delivery and coloured launcher
Fajr pending-resync owner native-adapter.js must keep still-deliverable event data; PrayerSchedule.sync must apply the same due-pending protection as Activity resume after persisting selected settings. OS AlarmDeliveryPolicy remains authoritative. Native-only launcher uses selected384pxWebP/full coloured backing/14% inset and separate themed silhouette. Test-only Android instrumentation remains outside release APK. See requests/SALATI-20261105-FAJR-ADHAN-ICON.md.

AdhanService.requestPlaybackFocus now owns bounded automatic startup focus retries; generation/terminal state guards cancellation and original beginFocusedPlayback owns unchanged local output setup. A real Android15 cold-service focus denial is the acceptance trigger.

Corrected after actual persistent-focus denial: AdhanService.requestPlaybackFocus distinguishes API35+ automatic USAGE_ALARM output from optional focus control; monitorAlarmMode gives calls priority and is canceled through existing release/generation ownership. Ineffective startup retry is removed. No media-engine/SDK/permission changes.

Verified current alarm architecture: actual5/5 cold/Doze outputs pass on sourcec312c7a/run41953110805; see current request evidence. This supersedes failed startup-retry hypotheses. API35+ alarm-stream output and call-mode/generation guards are active owners; media previews and earlier SDK focus requirements remain.

Alarm persistence owner: successful PrayerSchedule.scheduleNext writes nextAlarmTime/prayer/mode with synchronous commit before returning; host cold-process restore regression protects against losing pending identity/mode. Final native acceptance setup uses src/debug AlarmPreparationActivity normalfinish; exiting Instrumentation force-stops target packages and cannot reliably leave alarms scheduled. Neither utility is packaged into release.

##5Nov2026 scoped polish and approved real photo2
New shared timezone-lookup.js refines existing approximate tz-lookup using exact licensed offline polygons under world-data/exact-timezone-regions.json; prayer-engine.js calendarAlignedSolarTimes recomputes the correct civil-day solar date. Both app-source and city-times builds import that engine. Brand source pipeline scripts/build-salati-brand-assets.py derives header icon192, PWA512WebP/SVG and native launcher from one canonical original-mark/photo tile. Authentic frame pipeline scripts/build-authentic-mushaf-frame.py embeds pinned original PNG and excludes fixed source captions, without new decorative paths. Current per-request docs/allowlist/acceptance ledger govern scope.
