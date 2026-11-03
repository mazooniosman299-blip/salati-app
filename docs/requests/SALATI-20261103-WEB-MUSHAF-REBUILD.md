# Rebuild: Salati MushafBook 2026 from genuine open-source reader

## Original instruction
«حل لي المشكله دي من جزورها». The user explicitly rejected generated images, a linked picture of a Quran page, traditional CSS-only patches and falsely described print fidelity. Only the Quran screen and audio drawer may change. The other five tabs and original signing/deployment stay untouched.

## Reference and licensing
User's full-screen gold/cream page reference: screenshot 102822.jpg, numbered page 564; intended layout includes surah/juz top bar, two-column ornamental page border, chapter banner and Bismillah, 15 line slots and visible footer.
**UI source**: Mushaf Companion, https://github.com/abda-dc/mushaf-companion (MIT), source paths `app/page.tsx`, `app/globals.css`, page `frame-outer`/`frame-inner`, four `corner` elements, `mushaf-lines` grid and `page-footer`.
**MIT license**: exact full upstream text copied to `dist/quran/MUSHAF_BOOK_MIT_LICENSE.txt`.
**Quran text**: original immutable `dist/quran/data.json`; original 604 pages/6236 verses, original reciters and preferences.
**Page line metadata**: original prior-stage local CC BY-SA 4.0 layout `dist/quran/line-layout.json` pinned to upstream source commit `507eada...`, all 6236 canonical verses and word positions validated. Five pages differ from exact printed 15-row count and are flagged, not silently rewritten. No QCF glyph assets redistributed.

## Actual code replacement
- `dist/mushaf-book.js`: new standalone HTML/DOM book-page renderer adapted from MIT web source. Creates each Quran leaf with a full-size grid, top surah/juz rail, dual frame, four corners, two ornament side rails and numbered footer; uses real local verified Quran words, marks and clickable verse identities. No downloaded JPEG, screenshot, AI-generated text, hard-coded page 564, or fictional verses.
- `quran-controller.js`: removes old inlined page renderer and delegates only page DOM to MushafBook; retains original audio, reciter, bookmark, page and text state; safe fallback retained.
- `dist/mushaf-book.css`: separate, readable stylesheet scoped to active full-screen Quran tab (MIT-inspired geometry). Original charcoal `#18191D` audio drawer and `#2563EB` play control retained.
- `dist/salati-ui.css`: 25,939 characters of previous stacked trial rules removed. Only one canonical stylesheet link remains in `dist/index.html`; this canonical stylesheet imports MushafBook CSS as its first rule, preserving app build constraints.
- `scripts/prepare-android.py`: preserves the new Quran-only imported CSS during independent debug APK packaging, still removes unreferenced historical styles.

## Acceptance
Run original `npm ci; npm run build; npm test`, 604-page word map audit, page 564 and page 604 screenshot test on actual 390/430 width Chromium, player controls/seek, fullscreen and return-to-home, unrelated tabs unchanged; check independent `com.salati.prayer.preview` APK package/signing including both new source assets and MIT license.
Only pass the visual review when the actual screenshot of `#qSheet` shows a real full-page independent book UI, not the previous small text/card. No merge/deploy on production until user visually approves.

## Truthful limitations
This is a **source-level replacement of the page viewer** and borrowed licensed UI layout, not a copyright-infringing copy of an app screenshot. It is not yet independently certified to reproduce the exact QCF V2 15-line metal typesetting of the user's printed reference (requires matching page fonts/glyph codes and full printed-line audit). The 63-bar waveform is a user-shaped progress visualization, not decoded MP3 amplitude. Physical device performance, real network audio and same-key official APK update have not been certified.
