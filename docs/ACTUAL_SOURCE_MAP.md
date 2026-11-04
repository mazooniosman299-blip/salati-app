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
