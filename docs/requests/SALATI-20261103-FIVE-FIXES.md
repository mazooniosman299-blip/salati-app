# SALATI-20261103-FIVE-FIXES — scoped implementation and proof log

**User request (verbatim extract, 2026-11-03):** «أريد منك تنفيذ إصلاح جذري ونهائي للمشاكل الخمس التالية في تطبيق صلاتي. تعامل معها كمبرمج محترف مسؤول عن جودة التطبيق، وليس كمراجع يكتفي بكتابة التقارير.»
**Required issues (verbatim headings):** «المشكلة رقم 3: منع تعديل العناصر غير المطلوبة»؛ «المشكلة رقم 6: المطابقة البصرية الحقيقية»؛ «المشكلة رقم 9: إصلاح تعارضات CSS جذرياً»؛ «المشكلة رقم 11: إصلاح المصحف والمشغّل»؛ «المشكلة رقم 19: اختبار أندرويد النهائي».
**User's primary acceptance:** «لا تعلن اكتمال أي مشكلة إلا مع وجود دليل واضح على تنفيذها ونجاح اختبارها.»

- Repository: `mazooniosman299-blip/salati-app`; base `production@0576bb3a4524000d69076e2f9597b41715866aba`.
- Mode: **non-publishing governance/test hardening**; live user interface, Quran scripture, original images, APK, signer and release parts are untouched.
- Allowed changed paths: `docs/requests/ACTIVE_CHANGE.json`, this request record, `scripts/verify-change-scope.cjs`, `tests/agent-governance-contract.cjs`, `tests/visual-scope-diff.py`, `tests/current-design-visual-proof.py`, `.github/workflows/salati-agent-governance.yml`. Any additional path requires updating the explicit per-request allowlist and documenting its reason.

## Five-issue acceptance — accurate state at proposal creation

| Issue | Concrete source/behavior | Implemented in this branch | Remaining acceptance blockers |
| --- | --- | --- | --- |
| 3 | `scripts/verify-change-scope.cjs`, DOM ownership in `docs/ACTUAL_SOURCE_MAP.md` | Expanded visual-capable source detection to JPEG, AVIF, HTML, fonts; rejecting a visual change that only updates documentation. New negative cases. | Prove all CI checks pass and demonstrate enforcement on a future actual UI edit; current branch intentionally makes no UI change. |
| 6 | `tests/visual-scope-diff.py`, `tests/current-design-visual-proof.py` | Assert no changed pixels outside target, and no unapproved computed CSS, geometry or visibility changes at captured selectors. Capture the scrolled Quran state in real Chromium; 56 images intended. | Run exact CI, inspect its genuine screenshots and compare with authoritative user originals; no 100% claim. |
| 9 | `dist/salati-ui.css`, canonical loaded CSS, `tests/css-component-owner-audit.py` | Added CSS layer/duplicate budget audit and rendered CSS baseline comparison to active CI. **No speculative CSS edits.** | Find reproducible active cascade conflict, repair narrowly, rerun production/Android screenshots and signed-release gate. |
| 11 | `#qSheet`, `#qVerses`, `#mushafPlayerSlot`, `quran-controller.js` | Added real Quran mid-scroll reachability/screenshot evidence. **No player relocation or page substitution.** | PR35/36 overlap in `dist/index.html`, `dist/salati-ui.css`; precise authorized latest printed reference and final placement geometry remain unverified, and re-signed APK needed for runtime change. |
| 19 | Android system WebView, `PrayerWidget.java`, `prayer_widget.xml` | Added CI build of **debug preview only** with independent real Android 15 WebView and native widget emulator jobs, preserving failures/screenshots. | CI must run; debug preview is NOT production certificate verification, original-install upgrade proof or a physical-device test. |

## Already inspected sources and provenance

- `AGENTS.md`, `docs/requests/ORIGINAL_FULL_PROMPT_20261103.md`, `docs/CURRENT_APPROVED_DESIGN.md`, `docs/ACTUAL_SOURCE_MAP.md`, `docs/INSTRUCTION_CONFLICTS.md`.
- `PR #35` and `PR #36` both remain **open draft, unmerged**, with competing Mushaf/player scripts and overlapping live stylesheet/shell files. Do NOT merge or cherry-pick indiscriminately.
- Browser inspection of the real production URL at 390×844 on 2026-11-03 saw all six tabs, the Quran in a card, and player *below* the reading page, not the latest requested middle placement. No horizontal clip or active-nav overlap was observed at that one viewport. Browser tool reported a genuine capture; it has **not** been exported to this repository and cannot serve as a GitHub screenshot artifact.
- Only the existing production release manifest is evidence for original certificate fingerprint. A debug preview does not establish ability to install over original or verify original signing.

## Detailed visual guard contract

The approved target must have a real DOM selector, tab, language, desired before/after and preserved properties. Any candidate running source change must be compared against an actual `production` build at the same widths/languages/states. Every observed unapproved pixel outside the allowed region is a rejection, including tiny changes, and all measured unrelated CSS/geometry/visibility must remain unchanged. No CSS/source change is justified by a passing syntactic audit alone.

## Release decision

**NO MERGE / NO DEPLOY / NO SIGNED RELEASE** until all relevant tests, authentic reference match, and original-key signed asset/fingerprint conditions are independently proved. Current work is test and process infrastructure, not completion of issue 9 or 11 or of the user's five requested final repairs.
