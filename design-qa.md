## Final 1.0.103 decision — supersedes prior publication holds

User removed all approach announcements and explicitly directed use of the attached Fajr file after disclosure that redistribution permission is unverified. Exact bytes retained; not described as licensed. Current evidence: `reports/release-1.0.103.json`. JS/native/browser/build/lint/signature/APK checks passed. No physical device testing or subjective audio listening claimed. Final six-color palette includes PWA manifest. Original mosque/icons and Quran behavior preserved.

## Historical checks (superseded decisions below)

# Salati permanent dark matte correction

final result: passed

Scope: targeted WEB design acceptance only. Publication remains held on new reminder-audio rights and listening approval. Physical-device tests were not performed and, per the latest user instruction, are not a condition for completing the web changes. This is not a published release or an assurance of zero possible defects.

## Target and preserved structure

User specification: `docs/specs/2026-10-29-dark-matte-user-request.md`; previous original mosque screenshot: `design-references/user-mosque-original.png`. Correct the existing implementation only. Approved visual tokens: #0B0E13/#040509/#15181D/#32383F/#FFFFFF/#AEBCCB. The active theme stylesheet keeps its historical filename for build compatibility but contains only the permanent dark palette. No light/system switching remains.

City/dates stay in the left grid area; per the latest clarification, city size is unchanged and dates are smaller white text with normal word wrapping (15px desktop/12px mobile). Right area shows live next-prayer title, name, white countdown; no extra caption/icon. Image box/layout stays in place; exact original crop is preserved with four-edge CSS feathering and no image filtering/recoloring. Six live times remain below. Bottom six-tab phone navigation/safe-area padding and Mushaf-only media controls remain in place.

## Verified

- Actual Chromium measurements/screenshots at360/390/412/768/1024/1366/1920; six tabs, popovers, no horizontal overflow, matched date styles, white enabled-button text and charcoal controls. Independent English/navigation-safe-inset review also passed.
- Dark first paint with CSS and JS disabled, saved dark=false, malformed/blocked storage and public information pages.
-39 JavaScript commands, media owner/playhead/metadata/error retry, native reminder/permission harnesses, responsive CSS checks, actual computed-color audit, exact image identity and offline navigation.
- Android release and lint succeed (no errors/fatal; warnings documented), original certificate matches, all prepared APK assets and original image pixels match source. Original Quran text and all existing audio bytes are unchanged.
- Native city stays17sp; smaller dates start at12sp and fit using actual text/fallback-font metrics, with guarded API28 behavior. This is not physical launcher verification;8sp fallback does not certify arbitrary custom scales.

## Not completed / publication gate

No newly approved spoken approach recording with complete redistribution/editing/commercial scope has been verified. The prior five approach clips are available for comparison on a local review page only; they have not been reapproved. Two short continuous audition excerpts were prepared from a creator-owned CC BY4.0 Fajr source; full-phrase-only content and listening suitability still need approval. No full adhan is offered as a preview or bundled as a new alert. Existing reminder audio remains unchanged. No real Android device/emulator was connected, so lock-screen/background playback, installation upgrade and native launcher visuals are not physically verified.

Do not deploy or present1.0.103 as complete until the mandatory audio acceptance is resolved. Existing public1.0.102 remains unchanged. Rollback tag: `salati-1.0.102-stable`.

Evidence: `reports/dark-matte-1.0.103/verification.json`, `acceptance.json`, `screenshots/`, `web-review.md`, `native-review.md` and `audio-research.md`.

## Latest bounded refinement

User clarification: `docs/specs/2026-10-29-1.0.103-refinement.md`. Original24px white Phosphor book-open/heart/compass paths are unchanged and compared to their library originals. The player keeps its charcoal palette/card, stop control and one audio owner: stop moved onto the header row, play has44px hit target/36px visual disc, with16px glyph and4px track. No Home player added. Surrounding cards, calculations and other functions were not changed.

Only affected checks were rerun: date/player geometry at14 viewport/language cases, existing playback/metadata regression, private audition-page decoding/exclusivity, native build/lint/signature and prepared-asset verification. Other previously passing systems were not retested unnecessarily. Samples remain unadopted; published1.0.102 unchanged.

Current evidence and previews: `reports/1.0.103-refinement/README.md`, `focused-checks.json`, `audio-checks.json`, `audio-review.html` and `screenshots/`.

### Final visual feedback

Player-only neutral graphite overrides: frame/disc edge#363636, progress track#606060 (computedRGB channels equal; no blue tint). All other approved material tokens remain unchanged. The card fills its content width; phones gain16px within the existing toolbar padding without overflow. New screenshots use Arabic title/details: `player-ar-1600-v2.png`, `player-ar-390-v2.png`. Five focused widths pass; playback regression remains green. No broad unrelated tests repeated.

User explicitly chose to WAIT for audio rights and listening approval before publication. Fajr must contain only «الصلاة خير من النوم», once. No candidate has been adopted; prior approach distribution/editing/commercial scope is unresolved. Current public1.0.102 is retained.
