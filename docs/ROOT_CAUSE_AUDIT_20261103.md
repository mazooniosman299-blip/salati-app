# Salati — 20-risk implementation evidence and acceptance report

Audit date: **2026-11-03**. Repository baseline: `production@f47ca69e37e5cdbdad38909761a9583a0f70ed49`. Changes proposed in draft PR [#37](https://github.com/mazooniosman299-blip/salati-app/pull/37); production, APK and Quran texts remain unchanged. **No claim of 100% completion.** The source tree has 1,471 Git tree entries including directories, with CI [whole-tree evidence](https://github.com/mazooniosman299-blip/salati-app/actions/runs/41535372480) and actual [browser screenshots](https://github.com/mazooniosman299-blip/salati-app/actions/runs/41535372454).

| # | Root cause supported by evidence | Affected files/components | Actual repair or gate | Test/evidence | Acceptance status |
|---|---|---|---|---|---|
| 1 | No previous root instruction contract | AGENTS.md / all instructions | Created unified mandatory agent contract with precedence | contract CI successful on earlier commit | implemented, behavior over future edits not yet observed |
| 2 | Stale and conflicting requests | docs/specs, README, design-qa, PR35/36 | Current scoped design register + conflict register; historical prose explicitly superseded | commit diff / docs inspection | partially verified |
| 3 | Agents may redesign outside requested scope | CSS, HTML, native widget | Strict prohibition plus exact changed-path and pixel diff allowlists | scope rejection tests; pixel self-test pending latest CI | gate implemented; actual future user edits not proven |
| 4 | Target DOM/source not bound to original request | request records, index DOM, app-source.js | Exact visual target contract: tab, id/class, original and requested behavior, explicitly preserved properties; reject vague requests | changed-scope negative tests in agent-governance-contract.cjs | gate implemented; future human language remains subject to validation |
| 5 | Preview expectations promoted to current design | preview-four-ui-changes-browser.py, design-restoration-contract.cjs | **Removed obsolete mandatory bottom-only Quran player position**, kept six-tab ownership and security invariants; separate historical preview requirements | npm test + permanent test suites / latest head pending | targeted obsolete assertion fixed; other future supersessions need proof |
| 6 | Screenshots were not authoritative reference matches | reports, original reference registry | Capture real Chromium screenshot & computed metrics, require verifiable original image | actual 14+ existing source captures, new 48 screenshot test in CI | reference parity blocked by unverified latest image bytes |
| 7 | Text-level CSS tests may not test computed layout | tests/current-design-visual-proof.py | Runtime color/size/position/overflow/visibility metrics; pixel scope comparator | real browser CI pending | implemented test; final target design unverified |
| 8 | Generated app bundle name misleading vs source | app-source.js, scripts/build-web.cjs, dist/app-v1.0.109.js | Dependency graph plus **source-lifecycle-contract.cjs compares fresh esbuild output byte-for-byte to loaded generated JS**, alongside AR/EN reload Chromium | new lifecycle test added in no-deploy real browser CI | code implemented; latest CI pending |
| 9 | Large CSS cascade may hide semantic overrides | dist/salati-ui.css, CSS audit | Existing canonical single sheet audited, no extra CSS added | CI: 1,778 CSS rules, 6,005 declarations, 0 exact duplicate/conflict selector-property groups; cannot rule out cross-selector cascade interactions | measured, not globally refactored |
| 10 | Historical files alongside running code | dist versioned assets, older tests | Runtime/static upstream inventory and historic classification | `scripts/inventory-current-sources.cjs` CI to verify | proposed, final CI pending |
| 11 | Multiple Quran/player visual proposals | PR35, PR36, latest user screenshot | Mark both proposals unmerged/unapproved for pixel match; exact asset source gate | genuine current mushaf-390 screenshot differs from printed full-page request | unresolved until reference/implementation review |
| 12 | Concurrent PRs may overwrite same code | PR35/PR36 dist/index.html, dist/salati-ui.css | Runtime overlap CI guard; no blind merge | GitHub changed filename lists confirm both shared files | gate proposed; PR35/36 still draft |
| 13 | Original images could be replaced by stand-ins | user mosque image, native widget, design registry | SHA-256 registry and native/web crop exact-digest test | `tests/reference-provenance.cjs` in CI | original mosque locked; Quran/player original reference absent |
| 14 | Stale version information in old documentation | README, docs/source-README, design-qa, docs/github-source.json | Correct current manifest 1.0.123; archive README 1.0.116, explicitly type github-source.json 1.0.109 as historical imported snapshot | same release manifest and Git diff verified | correction implemented; current site delivery separate |
| 15 | Default main is not latest production | production, main, release branches | Branched PR37 directly from production; no main merge | GitHub compare base f47ca69, 0 commits behind at initial comparison | source branch corrected |
| 16 | No automatic rejection of changed out-of-scope files | scripts/verify-change-scope.cjs, active request record | Exact per-request path allowlist and release-critical checks | CI scope negative tests | implemented, new CI revalidation pending |
| 17 | Historical previews might act as blocking production criteria | workflow and test matrix | Explicit classification, unchanged safety requirements; no historical preview CSS imports | active HTML only canonical salati-ui.css | classification implemented; some old assertions require manual supersession audit |
| 18 | PASS treated as visual/user acceptance | tests and request acceptance records | Distinguish source/build/browser/reference/native/sign/publish verdicts | explicit record with unknown/blocked statuses | reporting corrected, not equivalent to all stages passing |
| 19 | Browser does not prove Android/widget equality | Android MainActivity, PrayerWidget, APK | Native-vs-web responsibility map + required emulator/real device scope | CI Android emulator and build jobs; real physical phone unavailable | partial; hardware acceptance outstanding |
| 20 | Lost/unaudited requests and no acceptance ledger | docs/requests/ORIGINAL_FULL_PROMPT_20261103.md, ACCEPTANCE_STATUS.json, ACTIVE_CHANGE.json | **Store complete original 567-line mandate and eleven-stage machine-checked acceptance status; block dishonest complete status** | verify-request-status.cjs negative false-completion test | ledger implemented; final visual/user acceptance blocked |

## Actual runtime findings
- Web HTML loads only `salati-ui.css` and legacy-named `app-v1.0.109.js` generated from `app-source.js`; **the bundle filename is NOT the Android version**.
- Current source release manifest 1.0.123, versionCode 124, applicationId `com.salati.prayer`; cert digest recorded as `559dec66ab13e86be17c661732f1d2b1751a63261ed7d7d353b857f693cf056e`.
- Real Chromium source report: 7 responsive viewports × 6 tabs without JS exceptions; real screenshot at 390px depicts continuous Quran text scrolling, not the requested independently approved exact printed Mushaf page, so do not label it pixel matched.
- CSS auditor inspected nested layers (1,778 rules; 6,005 declarations). Zero exact selector-property conflicts is NOT the same as zero cascading or visual regressions.

## Release and acceptance blockers
- Original approved source image for latest Mushaf/player exact pixels/rights is not established. Cannot certify 100% parity or merge visual PR35/36.
- A signed Android update with the **original** cert and exact site fingerprint is mandatory before any runtime asset reaches production; no keystores/passwords in chat.
- Physical Android device, in-place upgrade and user approval must be independently verified and documented.
- New governance branch only changes docs/tests/CI/scoping scripts; no production deployment, Quran text, audio settings, widget source, or APK release is touched.

Keep status **in progress** until relevant CI ends and user-requested actual design is independently accepted.

## إضافات تحقق سلامة النص القرآني
تم فحص نسخة قرآن صلاتي المضمّنة في APK التجريبي من CI: **604 صفحة، 114 سورة، 6236 آية فريدة، ولا تكرارات**؛ عدد آيات كل سورة يطابق البيان الداخلي. أُضيف `tests/quran-source-integrity.cjs` للتحقق من العدد والبيانات وبصمة SHA-256 الثابتة `cb2be527751f8671b89595a0d81cc059c3db894c213772200bcf9a01dc5096e5`. هذا يثبت عدم تغيير نسخة الملف الموجودة، وليس حكمًا على صحة أي نسخة مصحف جديدة أو زخارف لم يُعتمد مصدرها بعد.

## Unified batch implementation (additional commits)
- Original full, user-provided 567-line task is preserved verbatim in `docs/requests/ORIGINAL_FULL_PROMPT_20261103.md`; `AGENTS.md` points every new agent there before touching code.
- `docs/requests/ACCEPTANCE_STATUS.json` and `scripts/verify-request-status.cjs` separate source/build/functional/browser/visual-reference/Android-emulator/physical-phone/original signing/publication/user acceptance; negative tests reject an invented all-complete claim.
- `tests/design-restoration-contract.cjs`: retired hard-coded bottom-player requirement contradicted by later instructions. The player must stay on the Mushaf tab and must not obscure Quran text, with runtime screenshots as the separate proof.
- `tests/source-lifecycle-contract.cjs`: reproduces the exact bundled app code from `app-source.js` and checks the active binary output plus compatibility bundle; real browser suite checks language persistence and tab rebuild.
- `scripts/verify-change-scope.cjs`: for new visual edits, forces per-element `before`, `after`, and explicit `preserve` fields; background files and unsigned production changes are not silently approved.
- The real Chromium job now checks out full Git ancestry to avoid a previously observed `origin/production...HEAD: no merge base` failure.

**Status is not completed until relevant final CI jobs conclude successfully and unresolved original reference/hardware acceptance is supported.** Production remains unchanged. Do not conflate a green Cloudflare preview with authorized public release.
