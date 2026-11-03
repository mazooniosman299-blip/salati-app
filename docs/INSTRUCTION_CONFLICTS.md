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
