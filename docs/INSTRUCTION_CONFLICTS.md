# Instruction conflict and provenance register — 2026-11-03

| Topic | Evidence of conflicting / stale instructions | Resolution for NEW work |
|---|---|---|
| Release version | `README.md` says 1.0.116, `docs/github-source.json` historically says 1.0.109, while production `apk-release-parts/current.json` says 1.0.123 | Use release manifest as local version source; mark older documentation historical; verify deployed URL separately |
| Reader player position | Preview `tests/preview-four-ui-changes-browser.py` expects fixed player preceding `#qVerses`; `dist/index.html` production has `#mushafPlayerSlot` after `#qSheet`; PR35 describes lower sheet, latest conversation requests centered placement | Keep production unchanged until actual screenshot target and request geometry can be verified; preview test is NOT a production gate |
| Mushaf art | Older blue/Madar visual, later green/pink picture #5, subsequent 604-page official source and illustration in PR36 | Do not substitute one for another; only exact verifiable authorized source; pixel parity not established |
| PR overlap | PR35 and PR36 both modify `dist/index.html`, `dist/salati-ui.css`, and new Quran scripts; PR35 also changes permanent regression workflow | Treat PRs as competing implementations. No blind merge; reconcile feature-by-feature on fresh production base |
| Preview CSS | `tests/preview-four-ui-changes-browser.py` requires `preview-four-ui-changes-20261101.css` linked; production links `salati-ui.css` only | Retain for historical context, exclude from approved-production gates |
| Colors | Historical documents describe old blue `#153D7A` while executing `tests/reference-theme.cjs` expects current action-fill `#2563EB` | Source values and measured computed colors are separate facts; do not claim historical prose has precedence; latest component-specific user reference wins |
| Widget city/date | User requests across sessions vary about city label visibility; date must remain visible | No change outside a user-scoped widget request; log unresolved if asked to adopt an old screenshot |
| CSS priority | Past complaints about `!important` vs currently inspected canonical CSS with zero such tokens | Do NOT add no-op CSS cleanups to claim a fix; maintain existing no-priority safeguard |
| Source vs bundle | `app-v1.0.109.js` runtime name, but `app-source.js` builds into it | Modify source, rebuild bundle and validate; do not conclude bundle name means 1.0.109 installed |

This register is evidence of **why an agent could make the wrong choice**, not a claim that all twenty systemic risks are already fixed. Missing reference bytes/rights are an explicit blocker to exact visual acceptance.

## Newest 2026-11-02 approval sequence
At 19:37 UTC the user requires the **complete printed page** unbroken (not a boxed fragment), which supersedes split-page cards. At 19:54 UTC they approve specific player **shape/order/size** with Salati charcoal/blue/white palette, and remove lock/timer/chevron/notch/separate reciter picker; this supersedes older generic player descriptions in PR35. A later user instruction mentions placing the player **in the middle of the page**, which conflicts with bottom-only acceptance assertions. Preserve all approved constraints and explicitly mark precise final placement/overlap prevention for genuine UI verification, instead of inventing a geometry from a concept image. PR36 implements some controls but remains DRAFT and does not guarantee 604-page printed-art accuracy.

## Superseding scoped approval — Mushaf1441, 2026-11-03
The user selected option3 in the independent 604-page Madinah1441 preview, then expressly requested direct ayah-to-surah-end playback, no action dialog, and the actual surah name in white instead of static/full-surah wording. This supersedes older illustrated frames, middle-placement ambiguity and popup assertions ONLY for the Quran reader. Integrate on production@0576bb3; preserve all other tabs and original app capabilities. See requests/SALATI-20261103-MUSHAF1441.md.

## Opening transparent-margin correction —4Nov2026 Asia/Dubai
The user identified an almost empty Fatiha viewport in a short/wide browser. Verified original PNGs1/2 have494/480 transparent rows above ink. Keep original bytes and complete ink; display-only vertical viewport removes unused transparent rows with24px source safety padding and moves the unchanged SVG hit layer with the image. Only opening pages1/2 use these bounds; the other602 plates are unchanged. This supersedes preserving the opening files' blank canvas as visible layout space, not the original printed artwork. Evidence: requests/SALATI-20261104-OPENING-SPACE.md and reports/mushaf-opening-whitespace/.

## Latest rejection and framed-reference search —4Nov2026 Asia/Dubai
The user rejects candidate125 artwork/desktop gaps and supplies103498.jpg, requiring that original thin-brown-framed edition or a close original edition. This supersedes option3 artwork approval. PR47 remains draft; publication is held. Preserve previous successful audio/selection/top-whitespace fixes. Research exact source and clearly identify any near alternative before adoption; see requests/SALATI-20261104-FRAMED-MUSHAF-RESEARCH.md.

##4Nov2026 — explicit Fatiha entry
Latest user requires Fatiha whenever explicitly opening the Mushaf tab. This supersedes the prior behavior of reopening the start of the saved selected surah. Keep stored explicit bookmark/preferences, deliberate in-reader chapter navigation and background audio. Visibility resume passes the current surah explicitly rather than acting as a new tab entry. Existing tests that need later pages must deliberately select them after entry; do not weaken their geometry/audio assertions. No appearance/artwork modifications authorized.

##4Nov2026 home-reference steering
Latest4Nov home reference explicitly excludes native widget; earlier home strip/capsule assertions are historical for home only. Replace their home geometry assertions with reference3x2 cards, retain all settings/overflow/ordinary Fajr safeguards. Existing mosque authorized as explicit exception to new screenshot photo; no blanket recolors. See requests/SALATI-20261104-HOME-REFERENCE.md.

Home AM steering: latest explicit user says noص and requests exact right alignment. Remove Arabic AM suffix from home only (not native widget). Preserve existing PMم. RTL flex-end was a real physical-left child alignment bug; enforce common actual text-range right edges.

128 CI surfaced another historical collision: css-cascade-equivalence.py froze126 CSS and required every property to remain equal plus file shrinkage; it cannot accept any deliberate home/color change. After actual review and user alignment confirmation, retain126 fixture intact and add immutable128 approved snapshot. All36 cases/44-property/geometry parity assertions and size protection remain intact for future cleanup. Independent48 actual-production scope diff still compares127 to128 and accepts only requested regions. No deployment/signature protection changed.

##4Nov continuation/action-dock/launcher steering
Latest ayah action-dock request supersedes previous blanket no-action-dialog assertions only for a nonmodal reserved toolbar; do not restore an opaque modal. Latest requested default continuation requires one-time legacyfalse migration while preserving future explicit opt-out. Fatiha entry/reset and all non-reader/home/widget designs remain. See requests/SALATI-20261104-QURAN-CONTINUATION-ACTION-ICON.md.
