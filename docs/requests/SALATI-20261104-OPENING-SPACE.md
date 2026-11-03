# SALATI-20261104-OPENING-SPACE
Status: قيد التنفيذ

Original user wording,4 November2026 Asia/Dubai:
> الفراغ دا ليه هل لانها معاينه ومفتوحه في متصفح ولا في مشكله في الكود

Observed: user screenshot is a short/wide opening Fatiha viewport, almost all empty paper. Verified source PNG1 is1014×1628 with alpha ink bounds(156,494)-(859,1134); PNG2 ink bounds(156,480)-(858,1139). Current image scales the full canvas by width, making494 transparent top pixels consume the visible reading area. This is a display geometry problem, not an inherent browser preview restriction.

Scope: original opening plates1/2 only, .printed-page-artwork/.printed-page-image/.printed-ayah-regions; quran-printed-pages.js and derived regions1/2 metadata. Trim only unused transparent top/bottom display space with24 native pixels safety padding; preserve original PNG bytes, width/font scale, all ink/diacritics/verse markers, page order, polygons and their coordinate transform. Image and hit layer translate together. Other602 pages and all other tabs/player/audio/settings unchanged.

Acceptance: five viewports935×325,844×390,1440×700,390×844,320×740; first ink visible within32CSS pixels of reading-area top; entire alpha bbox retained inside viewport; image and SVG retain identical geometry and real point selections; no player overlap. Keep all604 original image hashes and6236 verse mappings. Rebuild/re-sign matching candidate before publication; preserve prior signed candidate1.0.124 and official1.0.123 artifacts. Current official publication remains onhold.

Evidence: failing actual-app regression tests/mushaf-opening-whitespace.py before fix. Reference is user's attached screenshot, not a generated image. New candidate1.0.125/code126 preserves immutable1.0.124 candidate chunks rather than overwriting them.

Local regression reproduced original failure:935×325 first inkY486 while reader starts48 and ends234. Display frame now cuts only transparent rows470..1158 (p1) and456..1163 (p2), with all original ink retained. All10 opening-page viewport cases passed before new signing; sourcePNG hashes unchanged. Actual screenshots personally inspected: first text visible at top on935×325 and390×844; continuous vertical reading preserved.
Previous signed-upgrade CI repeated a broad white-modal/ANR pixel detection and timed out; it had not granted geolocation unlike the existing debug/older-upgrade tests. Set explicit coarse/fine fixture permissions in the emulator and retain UI hierarchy/logcat on failure; do not bypass a failed readiness result or label it as a phone test.

New signed candidate metadata:
```json
{
  "version": "1.0.125",
  "versionCode": 126,
  "applicationId": "com.salati.prayer",
  "filename": "salati-1.0.125.apk",
  "size": 26038738,
  "sha256": "362d9addaa1c6b752c62abc9602175ad21389f30744ec56d5918afd18f1cba5d",
  "certificateSha256": "559dec66ab13e86be17c661732f1d2b1751a63261ed7d7d353b857f693cf056e",
  "partCount": 15,
  "chunkBytes": 1800000,
  "webFingerprint": "0aa60838515afe15adc75c3ce8b0467c5af21de367afdb79e427598359701e7a"
}
```
Original124 candidate chunks are retained. Original PNG hashes and canonical Quran data remain unchanged. Local full native/site comparison must pass before upload.

Final local125 checks passed: ten opening cases including real hit testing and exact full alpha bounds; full604 original hash/6236 map check; direct continuous-ayah playback regression; source rebuild/lifecycle; current CSS parity36 states; npm test; Android release build32s; original-key signing;989-file native/site equality; current release guard. Remote125 signed install-over-install and official publication remain pending.
