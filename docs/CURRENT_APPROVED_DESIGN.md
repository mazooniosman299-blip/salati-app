# Current confirmed design facts — Salati
Checked 2026-11-03 against production commit `f47ca69e37e5cdbdad38909761a9583a0f70ed49`. This is a *living scoped decision register*, not permission to redesign. An older file's title or passing test cannot override a later user request.

## Verified on current production source (baseline; not a claim of newest requested mockup)
- Six real tabs with DOM IDs: `times`, `mushaf`, `qibla`, `dhikr`, `tasbih`, `settings`; see [dist/index.html](../dist/index.html).
- Homepage loads one canonical stylesheet `dist/salati-ui.css`; its declared palette contains dark `#0B0E13` background and `#040509` cards. Active stylesheet has zero literal `!important` tokens in source inspection. This does not certify rendered pixels on all devices.
- Quran reading uses `#qSheet`, `#qVerses`; real controls `#qTransport`, `#qStop`, `#qSeek` appear in `#mushafPlayerSlot` after the reading element in the currently committed HTML.
- Original mosque image path appears in hero: `dist/images/mosque-reference-original.png`, and original reference assets exist in `design-references/`. Do not substitute generated art.
- Current release manifest: 1.0.123, Android versionCode 124, original certificate SHA-256 recorded in `apk-release-parts/v1.0.123/manifest.json`. That is manifest evidence, not on-device verification.

## Explicit user constraints (retain on subsequent work)
- Dark-only UI; keep current approved elements unchanged unless specifically requested.
- Original mosque image and unchanged Quran verse text, vowel marks, reciters, audio playback and preferences.
- The player belongs to the Quran experience, not the home dashboard; never obscure verses. Keep fixed bottom navigation clear of content.
- The user requires a real capture from the *actual Salati interface*, not an invented image or synthetic layout.
- When a request refers to a particular picture or player position, use the exact most recent user instruction for that component; don't infer approval from PR test assertions.

## Unresolved and supersession-sensitive — DO NOT silently decide
1. `PR #35`: text describes a bottom-of-sheet player, green printed-full-page preview and alternative earlier blue/Madar reference. Original exact approved print image/rights are not established; it is still DRAFT and unmerged.
2. `PR #36`: a later player sheet design with real controls and a fullscreen layout, also DRAFT and unmerged. Its text says the illustrated mockup is *not* the final 604-page artwork, and original signing key is unavailable. These PRs modify overlapping `dist/index.html` and `dist/salati-ui.css`.
3. More recent conversation asks for the Quran player in the **middle of the page**, conflicting with older "bottom" assertions. Do not promote a bottom position as approved without comparing the actual last reference and requested placement. Precise viewport-relative geometry is not verified.
4. Older documents disagree on whether the location/city label should display. Preserve the production widget until a request explicitly targets that field; do not auto-remove it.
5. Pixel-exact Mushaf Al-Madinah artwork cannot be certified until original authoritative asset, rights and screenshot matching are available.

## Supersession rule
Latest explicit user request for a *specific element* takes precedence only for that element. Never extrapolate its colors/layout to other pages. On ambiguity: freeze disputed scope; safely implement independent repairs and record evidence. See [INSTRUCTION_CONFLICTS.md](INSTRUCTION_CONFLICTS.md).

## Acceptance reference index
- `docs/design/approved-salati.png`: historical repository reference; current-vs-approved match **not reverified** in this governance pass.
- `design-references/user-mosque-original.png`: user-provided image asset. Original image should remain unmodified.
- `PR #35` and `PR #36` discussions: implementation proposals, **not** merged production rules.

## Later verified user decisions (2026-11-02; scoped, not pixel-certification)

- **Full printed page**: At 19:37 UTC the user reiterated that the Mushaf should appear as an entire uninterrupted printed leaf like their screenshot, not within a clipped card or pieced-together nested boxes. Do not crop or break a printed page to emulate a responsive card. The illustrative file `Salati App Full Quran Page.png` shows the intended whole-page composition but is not licensed Quran artwork.
- **Latest clearly approved player styling**: At 19:54 UTC the user accepted the **concept, order and size** of the dark player from a reference (later illustrated by `Salati Quran Reading Screen with Dark Player.png`); retain Salati **charcoal body, blue transport button and white Arabic labels**. The user requested removal of the timer/lock, chevron/notch and separate reciter field; integrate reciter selection within player settings while preserving real reciter state. Retain functional previous, next, repeat, speed, play, progress, close and settings according to original app capabilities. These are scoped user instructions, not permission to replace Quran text/artwork or redesign other tabs.
- **Placement conflict is genuinely later**: Another subsequent request states the player should appear **in the middle of the page**, which supersedes a blanket bottom-dock assumption for that specific placement. Without verified latest viewport-relative geometry, do not silently deliver the previously rejected bottom position and call it fully accepted. Keep actual Quran content unobscured at all times.
- **Unverified screenshots vs authorization**: Existing library files titled `Salati App Full Quran Page.png`, `Salati Quran Reading Screen with Dark Player.png`, and `Salati App with Ornate Green-Pink Mushaf.png` are *illustrative user-discussed examples* (not authoritative licensed plate assets or ready-to-ship files). The precise original printed plate library + use rights remain unverified. Visual matching to these screenshots is a distinct test from Quranic page accuracy.

## Superseding scoped approval — Mushaf1441, 2026-11-03
The user selected option3 in the independent 604-page Madinah1441 preview, then expressly requested direct ayah-to-surah-end playback, no action dialog, and the actual surah name in white instead of static/full-surah wording. This supersedes older illustrated frames, middle-placement ambiguity and popup assertions ONLY for the Quran reader. Integrate on production@0576bb3; preserve all other tabs and original app capabilities. See requests/SALATI-20261103-MUSHAF1441.md.
