# Root cause workboard — evidence, not blanket completion
Scope: `production@f47ca69`, repository inventory (1471 entries incl. dirs), current manifests, selected source, CSS, active CI, and PR35/36. This is an **initial audit**: not every source line and runtime device has been independently executed. Statuses are deliberately conservative.

| # | Risk | Evidence / affected area | Fix in governance PR | Validation state |
|---|---|---|---|---|
| 1 | No unified instructions | No root AGENTS.md identified in tree | Add root AGENTS.md | Source committed; CI pending |
| 2 | Old/current conflicts | README 1.0.116 vs manifest 1.0.123; PR35/36 | Current design + conflict register | Documentary |
| 3 | Agent invents design | Original assets vs proposed mockups | Explicit no-guessing rule | Behavioral proof requires future requests |
| 4 | Wrong target component | dynamic app-source.js/DOM | Request acceptance template/IDs | Process only |
| 5 | Old UI tests | preview expects unlinked stylesheet | Test classification/documentation | Active runtime test reconciliation pending |
| 6 | No definitive visual match | latest image bytes inaccessible in repo | Reference proof protocol | Blocked original asset |
| 7 | Weak pixel assertions | existing browser tests/computed-style assertions present | Require scoped geometry+comparison | Additional checks pending |
| 8 | Editing generated outputs | build-web.cjs bundles app-source.js to version-named dist | Active source map and build rule | Verified from code |
| 9 | CSS cascade complexity | single canonical CSS ~195KB, 2 layers, no !important tokens | Owner-map instruction | Full selector audit not rerun |
| 10 | Historical files mixed | many version-named dist files | Source classification | Verified inventory |
| 11 | Multiple Mushaf implementations | PR35 vs PR36 plus new image instructions | Mark unresolved; do not merge | Requires reference approval |
| 12 | Competing PRs | shared dist/index.html and CSS | Overlap register / block blind merge | Verified changed-file lists |
| 13 | Poor ref management | user mosque asset present; other image uncertain | Provenance requirement | Partial |
| 14 | Outdated docs | README misleading published version | README current-state banner | Updated; live publication unverified |
| 15 | Wrong base branch | default main, production has newer release manifest | Branch created from production | Verify diff via GitHub |
| 16 | Unrequested changes | no per-request allowlist in repo baseline | Active change manifest + diff-scoping script | CI pending |
| 17 | Preview mixed with production | old CSS preview expectations | Test classification | CI migration pending |
| 18 | PASS confused with success | CI contract tests only source & sign safeguards | Multistage result terminology | Not a visual QA claim |
| 19 | Browser ≠ WebView/widget | native PrayerWidget and assets separate | Surface-specific acceptance requirement | Device work pending |
| 20 | No unified acceptance records | no known per-user standardized record | Record template and active manifest | First record established |

## Critical technical facts
- Active HTML CSS: `salati-ui.css`; JS bundle: `app-v1.0.109.js` (filename is not release truth).
- Current local release manifest: `1.0.123`, versionCode `124`, original cert SHA `559dec66ab13e86be17c661732f1d2b1751a63261ed7d7d353b857f693cf056e`.
- `PR35` and `PR36` remain DRAFT; their full design requirements must be reconciled against actual last user reference.
- No UI, signed APK, Cloudflare deployment, or Quran assets are changed by this governance PR.

## Remaining implementation before user can call 20 items resolved
Reconcile outdated production-browser visual assertions with latest real design; add screenshot-to-approved-reference comparisons and per-request computed-style assertions; audit all source/CI paths; test all six tabs Arabic+English and Android/Widget; verify signed release if runtime files change. None is claimed complete now.
