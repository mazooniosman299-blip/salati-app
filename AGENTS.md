# Salati — mandatory implementation contract for AI agents

> Applies to every new AI coding session and every proposed change. Start here, then read `docs/CURRENT_APPROVED_DESIGN.md`, `docs/ACTUAL_SOURCE_MAP.md`, `docs/INSTRUCTION_CONFLICTS.md`, and the current request record. Do not treat this document as a substitute for direct code inspection.

## 1. Source of truth and precedence
1. Explicit, most recent USER instruction for the specific element and scope, where its wording and evidence are available.
2. The original user reference asset actually available and approved for that element; never replace it with an AI-generated image or a merely similar web image.
3. `docs/CURRENT_APPROVED_DESIGN.md` for currently verified, nonconflicting decisions.
4. Executing source from the current `production` HEAD (`dist/index.html`, linked CSS, actual entry bundle, JS source, native Android code).
5. Historical plans, readmes, tests, previews and earlier PR text are evidence of past work, NOT overriding instructions.

If two recent instructions conflict, record both, affected elements, timestamps and evidence; implement independent work, mark disputed visual behavior unresolved, and ask one narrow question only when implementation cannot safely proceed. Do not silently choose an older visual design.

## 2. Identify what was requested, BEFORE coding
Create/update a request record in `docs/requests/` using `docs/requests/TEMPLATE.md`. Quote the original user instruction exactly; translate it into:
- affected tab/screen and real DOM id or Android view;
- current observed behavior and requested behavior;
- approved reference (exact asset and provenance, if any);
- files actually executing and upstream source files;
- expected edits, prohibited side effects, data/settings preserved;
- explicit measurable acceptance tests and screenshot viewport(s).
Never claim an unavailable image, an AI-generated mockup, or a screenshot of a different build is a genuine implementation proof.

## 3. Implementation scope is strict
Changing a color does not authorize changing dimensions, shape, location, padding or another component. Moving the Quran player does not authorize changing Quran text, page artwork, navigation or sound engine. A dependent change is allowed only if technically necessary and recorded with a reason.
Check `git diff --name-status` and relevant affected CSS/JS selectors after every modification. Every changed file must be in the request's declared allowlist or justified as a dependency and approved through the same scope record. Prefer narrow changes in source, NOT layers appended to CSS just to override an earlier rule. Preserve unknown behavior.

## 4. Actual build system (verify on every task)
- `dist/index.html` is the live UI shell. The HTML loads `dist/salati-ui.css` and an *historically named* `app-v1.0.109.js` script on the examined production commit; do not infer installed version from this filename.
- `scripts/build-web.cjs` uses esbuild to bundle `app-source.js` and its imports (including `quran-controller.js`) into the actual referenced `dist/app-v*.js` and `dist/app.js`.
- Changing only a generated bundle is not a permanent fix. Detect dynamic DOM recreation, language/tab/navigation and persisted state.
- Native app code is under `android/app/src/main`; native widget lives in `PrayerWidget.java` and `res/layout/prayer_widget.xml`. Website CSS alone cannot certify native widget or WebView.
- Keep backups, old CSS, release chunks, Quran datasets and original mosque files intact unless independently approved for removal.

## 5. Quran, media and visual references
Never edit Quranic verse content or diacritics to fit design. Keep all original reader/reciter/audio/offline/settings features; no clipped verses or overlapping player. Exact printed Mushaf artwork or portrait comparisons require verified original bytes, usage rights and true visual comparison. `PR #35` and `PR #36` are separate UNMERGED experiments; audit overlapping changes instead of merging blindly.
Dark-only production is baseline. Do not restore a light mode or introduce unsolicited colors. Use `design-references/` and `docs/design/` only after validating whether a file is original, approved, a historical illustration or an actual test screenshot.

## 6. Tests and evidence
Run code/build tests, actual runtime DOM/computed-style/geometry tests, visual screenshots at relevant mobile/desktop widths, Arabic/English, reload, navigation, settings persistence and Android surfaces affected. Compare actual capture and authoritative reference; record differences and pass/fail explicitly. Passing CSS grep, compiler, emulator, or CI is NOT pixel fidelity or physical device proof.
Classify tests into core/security, approved-production visual, historical, preview-only and Android/release. Do not rewrite safety tests to make a visual preview pass. If an outdated test contradicts current approval, document and isolate/replace its visual assertion before disabling anything.

## 7. Release protection
Start from the newest verified `production` commit in a NEW branch; do not start from stale `main`. Never push directly to production, silently deploy previews or bypass published web fingerprint checks. A site asset change normally requires a matching original-key signed APK release before merging/publishing. No new signing identity; no secrets in chat/repo. Preserve applicationId `com.salati.prayer` and the original certificate SHA-256 `559dec66ab13e86be17c661732f1d2b1751a63261ed7d7d353b857f693cf056e`.
Unverified signing or hardware testing means BLOCK production, not fabricate success. Preview deployments must remain separate from official production URLs.

## 8. Completion language
Report separately: source changed / build passed / functional tests passed / browser capture passed / visual reference confirmed / Android emulator checked / physical device checked / ready to release / published and verified. Provide a link to commit, test run, reference and real screenshot where possible. State `not tested`, `blocked`, or `unresolved` honestly. The word «مكتمل» is reserved for full acceptance of the user's particular request with evidence.

## 9. Every new request
Update the request record, `docs/requests/ACTIVE_CHANGE.json` path allowlist, visual spec and conflict register as needed; run `node tests/agent-governance-contract.cjs` and `node scripts/verify-change-scope.cjs origin/production` in PR CI. Deliver changes as a reviewable PR; don't merge or deploy without all required signed-release gates.
