# Independent review of pending 1.0.106 changes

Reviewed uncommitted modifications against e6248cd980201548ad76e5e860cafeca5cfc1bee, focusing on selection lifecycle/search/focus, shared dialog presentation, action controls, and native date layout. No source edits or builds were performed.

## Finding — resolved

- **P2 — Filtered verse-reader keyboard navigation traverses hidden results.** `quran-controller.js:66` collects all `menu.children`, while `popover-menu.js:51` now hides nonmatching reader buttons. Searching `ش` leaves `shatri` and `afasy` visible with hidden `yasser`/`qatami` between them. ArrowDown from `shatri` attempts to focus hidden `yasser`, leaving focus stuck on `shatri`; users cannot reach the next visible match with the arrow key. Filter to visible enabled buttons and guard an empty result set. Coordinator corrected the handler to filter hidden/disabled rows and return on empty results. Source reinspection confirms the fix at `quran-controller.js:66`; `tests/selection-menus.py:37` now covers search `ش`, ArrowDown from `shatri` to `afasy`, then Escape. Finding closed on source review; coordinator is running the final browser suite. No broad rerun was performed by this reviewer.

## Review limits

No other concrete regression identified within the pending source changes. The new observer has conditional text updates, so its own child mutations settle; native back uses the existing open-dialog handler; dialog closure restores the anchor.

Native date fitting accounts for wrapped text and the existing column ratio, and dates use physical left gravity. Physical phone and native rendered font-scale tests were not available. At large system font scales, the unconditional minimum12sp return can still exceed the space at minResizeHeight140dp; that remains an unverified layout limit rather than a claim of successful native rendering. Existing browser/source checks do not establish physical widget fit or actual audio playback.
