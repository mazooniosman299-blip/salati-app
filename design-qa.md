# Selected-reference design QA

final result: passed

## Scope

Responsive application UI shared by web/Android WebView, approved mosque asset identity, Android widget source/resources and build verification. Physical Android launcher rendering is not included in the visual pass and remains untested.

## Selected source

`design-references/user-mosque-original.png` is copied unchanged from the user's `Salati_Original_Mosque_References.zip / 01_original_widget_reference.png`. The exact source was inspected alongside captures at `reports/selected-reference-1.0.102/screenshots/`. Source hash and crop coordinates are recorded in `design-references/mosque-crop.json` and `dist/images/SELECTED-MOSQUE-SOURCE.json`.

The central mosque region is extracted using lossless cropping only. No generation, inpainting, resampling or color modification is used for the image asset. Full screenshot text is not baked into the app: location, Gregorian/Hijri dates, next prayer, countdown and six prayer times remain live. Visible architecture is limited to what the supplied screenshot itself contains; missing imagery is not invented. The two alternate reference images and the rejected generated replacement are not used as the mosque background.

## Comparison and interaction checks

- Deep navy glass palette, rounded transparent surfaces, fine borders and white icons are shared across Times, Quran, Qibla, Adhkar, Tasbih, Settings and popup menus; the light theme retains black text and readable white surfaces.
- The live prayer card groups location/date at left, original mosque at center, next prayer/countdown at right, and all six times on one aligned lower strip. The highlighted time follows the actual upcoming prayer rather than copying the stale highlighted prayer in the screenshot.
- Mobile reflows the same uncropped asset to a full-width middle row so its visible mosque content is not lost to a cover crop. Metadata and controls remain readable without horizontal overflow.
- Existing white location action remains available, honoring the user's earlier functional preference; live date text correctly reflects the current selected-zone calendar instead of copying the incorrect weekday/Hijri text baked into the mockup.
- Book-open, heart and compass navigation glyphs follow the supplied icon reference. All six navigation destinations use equally sized rectangular glass targets, including RTL/LTR and reduced-motion states.
- Compact Quran transport has one visible primary play/pause button, thin timeline, complete current-stream elapsed/duration information and a Stop control when active. No player ownership or background-audio logic is replaced by this visual change.
- The native widget uses the same exact cropped PNG. Its day/night policy changes only the text-legibility overlay, not the approved mosque image. Its existing scheduling/countdown behavior and selected time zone remain intact.

## Verification

PASS: exact source-crop pixel comparison; web/native image files are identical. Compiled APK native image pixels also match the approved crop. All prepared Android web assets match their source payload byte-for-byte.

PASS: 39 JavaScript regression commands; 7 CSS cascade responsive checks; 12 selected-widget width/theme cases; actual Chromium navigation/menu/keyboard/focus/contrast/reduced-motion tests; 56 rendered-color states with no non-black/white neutral-gray failures. Background photography is correctly excluded from UI token classification.

PASS: controlled offline Arabic/English deep-link fallback loads the actual approved mosque and Quran data. Public information pages follow saved themes and recover from malformed settings.

PASS: Android reminder/widget/date scheduling, permission and Activity/session harnesses; `assembleDebug --offline` for 1.0.102, versionCode 103. Native resource IDs resolve uniquely. No physical-device, launcher font-scale, doze or audio-route claims are made.

## Remaining notes

No P0/P1/P2 issue remains in the checked UI and asset integration. The native launcher appearance still needs a real-device check. This is a local implementation/preview, not a published or newly signed release. Subjective replacement of reminder voice recordings is a separate outstanding task and was not changed by this design work.

## Mushaf-only media reference refinement

Following clarification, primary navigation retains its existing position (bottom on phones). No extra shortcut row or audio panel is added to Times/Home. The selected glass media styling applies to the existing single player inside Mushaf only; its audio owner is never replaced when switching pages. Playback may continue with the controls hidden outside Mushaf.

Browser regression verification confirms no Home player, one Mushaf player, preserved playhead and audio identity across navigation, start/pause/resume/stop, actual verse/reciter metadata across theme/language refresh, failed Quran load and retry, and both themes at 320/390/760/1440. Audio output is mocked. Physical launcher rendering remains untested; changes are unpublished.
