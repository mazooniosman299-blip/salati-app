# Root fix: real Madinah QCF V2 and exact original Salati player heading — review only

User's exact critique: black circles remain in Quran; wants the same Medina Mushaf look; "المصحف الشريف" is truncated and an unwanted text fragment immediately below it spoils the player. Do not merge, deploy or present a false "100% match" claim.

## Demonstrated root cause
The previously bundled "MadinahHafsClassic.ttf" is KFGQPC Uthmanic Script Hafs 0.09, where combining Quran code point U+06DF (ARABIC SMALL HIGH ROUNDED ZERO) is mapped with a **wide 1442-unit advance and large black circular outline**. Quran data includes this Quranic mark 3,988 times. Simply deleting this character would violate scripture integrity and user requirements. The bundled alternative Amiri Quran has a zero-advance mark glyph, but its full calligraphy is not pixel-perfect Medina QCF V2.
The legacy salati-ui.css also has old styling for .recitation-caption strong and #qTrack, making "المصحف الشريف" visually truncated while the metadata line under it appears as garbled dots.

## Actual changes
- `scripts/stage-madinah-qcf-v2.py` stages all **604 genuine matching QCF v2 word-glyph page maps and all 604 matching font files** from sources pinned/documented in `dist/quran/SOURCES.txt`. It refuses a release if any original verse marker mismatch occurs.
- `dist/madinah-qcf-v2.js` injects actual Medina QCF glyphs by page after metadata+font are both loaded; old complete Quran is still present as fallback. Original Tanzil JSON and audio handlers are untouched.
- `dist/mushaf-book.js` delegates only the visible page to the QCF renderer; original page/verse interaction selectors and reader state preserved.
- `dist/mushaf-book.css` restores printed Medina cream/gold page treatment and correctly shapes original Quranic marks; the Unicode fallback uses bundled Amiri. It forces untruncated white "المصحف الشريف" heading, hides garbled qTrack metadata without deleting the values, and leaves original charcoal #18191D and blue #2563EB audio controls.
- `tests/quran-visual-trial-browser.py`: explicitly tests QCF-loaded pages 1, 564, 604 and visible title, hidden duplicate subtitle, no black UI circles, no glyph overflow, original audio/return navigation.
- `.github/workflows/salati-madinah-qcf-preview.yml`: compiles with all 604 offline QCF pages in a preview-only signed APK, never produces a public release or merges to production.

## Blocking conditions
- Require all original 6,236 verse-end markers to match the original canonical source.
- Require verified genuine QCF glyph and matching page font in live browser screenshots (390x844 and 430x932) on pages 1, 564 and 604.
- Require full title as real text "المصحف الشريف" with visible measured bounds; no unreadable subtitle.
- Require 604 assets and matching fonts inside standalone package `com.salati.prayer.preview`; official Salati signature untouched.
- Do not certify 100% printed ornamental artwork or original-device audio behavior until demonstrated; no production release or merge before the user approves.
