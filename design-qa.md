# Home reference QA —4Nov2026

final result: passed

This is manual visual and measured-layout acceptance against the latest **revised component contract**, not an automated pixel-equality claim. The prior1.0.109 report is preserved at docs/archive/DESIGN-QA-1.0.109-HISTORICAL.md.

Source visual truth: user inline455x457 home screenshot in this conversation,4Nov2026; original source raster is not mounted as a local file. Two explicit revisions: «مامشكله استخدم نفس صورة المسجد» authorizes the unchanged original mosque; latest user requests removeص and correct alignment, then explicitly confirms «هذه المحاذاة هي المقصودة» after the real corrected capture. These revisions supersede those specific initial-image details only. No claim that a different mosque photograph is identical.

Implementation: reports/home-reference/455-ar-dashboard.png (455x457 content crop at deviceScaleFactor1, browser455x900);390-ar-screen.png actual full app at390x844. Actual default calculated Muscat4Nov times differ from the screenshot's illustrative5:00/12:00 etc; no fake prayer time/location inserted. Other real widths320/768/1440, Arabic/English, native widget preservation, switching and reload tested.

Comparison history:
1. First actual capture found a legacy generic button rule adding a city border and dark pin; photo crowded prayer text, tile times were smaller. The isolated home location button is now excluded from that generic button rule, supplied pin is white, original photo positioned left, times16px.
2. User rejected alignment andص. Actual RTL cross-axis flex-end aligned variable-width children physically left; child boxes now stretch with physical right text alignment. Arabic AMص removed from home; existingPMم retained. Actual text-range right-edge assertions pass at all ten width/language combinations. User explicitly confirmed this corrected alignment.
3. Final real capture reopened after these fixes. Hero182px; separator194px; panel206px; first card253px; row gap10px; card90px and radius12px;455x457 component matches measured source composition. Same3x2 RTL order and actual moon/sun/rising/setting/moon-star assets. No known actionable P0/P1/P2 finding against the revised scope.

Five fidelity surfaces:
- Typography: existing app Cairo variable font, white labels, hierarchy and centered card labels; hero label/name/time share physical right edge. English and unavailable messages fit. Source-font exact binary unavailable; no font-identity claim.
- Rhythm: measured455x457 composition,3 equal columns/2 rows,8px horizontal gaps,10px row gap; phone full available content width; desktop same single grid. Existing app header/nav intentionally remain outside the supplied dashboard crop.
- Colors: charcoal default/selected cards; three requested foregrounds computed RGB255,255,255 after actual tab creation/reload. All other tabs retain their computed appearance.
- Images: unchanged original supplied mosque bytes, user-approved exception; no generated replacement, no image stretch. Existing local library icons retained. Widget resource files unchanged.
- Copy: actual city/prayer/time data, short PM only in Arabic; all six prayers and three requested text strings retained. Countdown/dates/calculation remain accessible in calculation details rather than deleted to resemble a crop.

Full-view evidence: inline user reference and actual browser capture visually reviewed in the conversation; source bytes unavailable, so no stitched side-by-side or automatic reference-pixel comparison is claimed. Focused evidence:390-white-juz.png,390-white-qibla.png,390-white-android.png; exact hero text-range/3x2 geometry in result.json. This report records actual manual review and user's explicit alignment confirmation, not a fabricated image diff.

Interactions: six tabs, city/calculation details, actual next prayer/time, language persistence/reload, Fatiha entry/bookmarks and continuous full-surah playback regression. Console page errors zero in home and six-tab suites.48 actual baseline/candidate captures pass the strict component scope guard; this proves absence of unrelated visible changes, not original-image pixel identity.

P3/test limits: no mounted original screenshot binary for automated pixel comparison; source photo substitution was explicitly authorized. Physical phone not available and not claimed; fresh hardware emulator and signed install-over-install must pass before publication.
