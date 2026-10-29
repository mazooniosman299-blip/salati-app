# Fresh web source review

Reviewed HEAD `2a1fb07`, with current uncommitted theme work present. Review only: no application file edits, publication, secrets access, or generated-JavaScript bundle review. The HTML, service worker and CSS in `dist` are maintained source inputs to this build, so these were inspected. Severity: P2 = functional issue worth fixing; no confirmed critical/security issue found in this review.

## Confirmed findings

### P2 — Pending orientation permission can reactivate a disabled compass

Evidence: `compass.js:9` awaits `Orientation.requestPermission(true)` and subsequently sets `enabled=true` and installs both orientation listeners without checking whether `disable()` intervened. `compass.js:14` disables synchronously; `app-source.js:88` (setupCompass) invokes disable on document visibility becoming hidden. A permission dialog, navigating away, or another disable while permission is outstanding can therefore be followed by stale listener installation and a live compass after disable. An older denied request can likewise overwrite the current request's status.

Reproduced without hardware: call enable with a deferred permission promise, call disable, resolve granted, await enable. Actual: enabled=true and both orientation listeners present. Expected: remains disabled. Saved executable regression: `/workspace/salati-fix/202/web-review-repros.cjs` (currently fails).

Minimal repair: increment an enable-generation token in disable; capture it immediately after enable's initial disable(false); after every awaited permission result, return if the generation differs. Guard both success and denied/error reporting with the captured token so a stale request does not overwrite a newer request. Test delayed grant and delayed denial after disable, plus overlapping enables.

### P2 — Offline fallback at a nested URL cannot load the app shell

Evidence: `dist/sw.js:1` returns `caches.match('./index.html')` for every uncached offline navigation while preserving the requested URL. `dist/index.html:1`/`:29` use root-shell relative styles/scripts/assets (including `app-v1.0.100.js`) and have no base URL. Visiting `/en/prayer-times/unvisited.html` offline returns the root shell but its app script resolves to `/en/prayer-times/app-v1.0.100.js`; that resource is neither the cached root script nor a real asset. The shell does not boot. This is visible after first visiting the app online, then opening an uncached nested city or guide page offline.

Reproduced with the actual SW in a VM and a cached root response: the returned shell's script resolves to `/en/prayer-times/app-v1.0.100.js`, expected `/app-v1.0.100.js`. Same saved regression file currently fails.

Minimal repair options: (a) make shell resource references and fetch/data paths root-relative, or (b) add `<base href="/">` to a cloned fallback response only, preserving its content type, or (c) redirect failed nested navigations to the cached root URL. The scoped fallback base avoids changing normal document behavior or runtime source paths. A redirect must be tested in an actual controlled offline browser: it must trigger a fresh root navigation that the worker can serve. Do not merely substitute the body without correcting its base. Verify script, CSS, Quran/data, icon, and world-city fetch paths, and avoid accidentally serving this HTML fallback to non-navigation requests.

## Checks and scope

Passed commands: `node tests/infrastructure-regressions.cjs`, `node tests/review-round-two.cjs`, `node tests/quran-audio.cjs`, `node tests/prayer-engine.cjs`, `node tests/city-pages.cjs`. These cover GPS/calculation choices, native sensor routing, persisted volume and malformed cache restoration, Quran recording/cue coverage and switching, 2760 finite/ordered city-date schedules, city runtime midnight/foreground refresh and DST behavior. They do not cover the two reproduced failures above.

Reviewed all root first-party JavaScript modules: `adhkar-controller.js`, `ads-adapter.js`, `app-source.js`, `audio-controller.js`, `back-navigation.js`, `choice-picker.js`, `compass.js`, `glass-navigation.js`, `location-picker.js`, `location-startup.js`, `location.js`, `native-adapter.js`, `native-prayer-audio.js`, `native-quran-player.js`, `official-muscat.js`, `popover-menu.js`, `prayer-announcements.js`, `prayer-engine.js`, `prayer-preferences.js`, `prayer-provider.js`, `prayer-refresh.js`, `quran-audio-source.js`, `quran-controller.js`, `quran-download-controls.js`, `quran-follow.js`, `quran-offline.js`, `quran-page-audio.js`, `reminder-interval-picker.js`, `seo-metadata.js`, `settings-restore.js`, `voice-picker.js`, `world-directory.js`. `cities.js` was examined as structured coordinate data/imported engine input rather than manually validating every coordinate.

Reviewed city modules: `city-pages/directory-search.js`, `city-pages/directory.js`, `city-pages/runtime.js`, `city-pages/timetable.js`; source build scripts: `scripts/build-web.cjs`, `scripts/build-city-pages.cjs`, `scripts/build-navigation.cjs`, `scripts/build-world-cities.cjs`; maintained shell inputs: `dist/sw.js`, `dist/index.html`, `dist/style.css`, `dist/light-theme.css`, `dist/salati-design.css`, `dist/city-pages.css`.

Important test source inspected: `tests/infrastructure-regressions.cjs`, `tests/quran-download-controls.cjs`, `tests/location-picker.cjs`, `tests/reference-theme.cjs`; selected other checks executed above. Generated bundles/node_modules were excluded from code review (installed build tooling/library calls were used to bundle probes). Android source, deployment scripts and external infrastructure are outside this assigned web review.

## Neutral hardcoded colors outside theme declarations

These are a maintainability/theme inventory, separate from the confirmed functional findings. Some white/black sheen, shadow, text and light-only choices may be intentional. Match current working source when applying changes because the main agent owns theme edits.

Highest-confidence remaining live gray escapes:

- `dist/salati-design.css:66`: unchecked Quran option track `#8b8b8b` with `#898989` border; checked track uses tokens but unchecked gray remains.
- `dist/salati-design.css:123`: aligned Qibla state has `#9c9c9c` border and `#9c9c9c1c` halo. Later generic compass border/shadow at :202 actually overrides these because its selector specificity is higher; treat :123 as dormant until cascade changes, not a currently visible aligned gray defect.
- `dist/salati-design.css:185`: Locate control hardcodes `#fff` background, `#000` text, and `#767676` border for both modes. This is a live shared-theme escape, though its intentional white style may be a product choice.
- `app-source.js:40`: `meta[name="theme-color"]` uses `#000000`/`#ffffff` independent of CSS variables; browser chrome does not inherit the dark blue theme.

Additional literal sites in final design CSS: :32 white switch thumb and `#0003` shadow; :68 `#0002` thumb shadow; :72 `#33333306` card shadow; :88 `#51515124` counter shadow; :101 white inset and `#30303008`; :102 `#131313` inset; :110 `#39393926` icon shadow; :128 `#000` text/`#39393924` shadow; :129 `#1d1d1d` menu fill/`#0005` shadow; :142 `#ffffff0a` sheen; :165 `#ffffff38` sheen; :169–170 white checked marks/thumbs; :178–179 black/white countdown; :183 `#ffffff24`/`#00000010` active-prayer effects; :193 `#ffffff14`, `#ffffff02`, `#ffffff20` mounts; :198 `#ffffff70`/`#00000020` selection effects; :202 `#00000012` compass shadow. Several of :72/:88/:101/:102/:128/:129 are superseded by later glass/token selectors. Do not count them as active visual defects without cascade verification.

Legacy opaque gray at `dist/salati-design.css:31` (`#939393`) and :33 (`#606060`) is superseded by :171 and :62. Its Quran gray at :66 remains active. Light-only fixed white/black values remain throughout `dist/light-theme.css:7–23`; :2 and :24 are the actual shared theme declarations and intentionally excluded from escape findings. `dist/city-pages.css` contains no gray color literals (`white-space` is unrelated).

`dist/style.css` retains a large legacy gray layer: hero/primary/counter (:2), compass (:8), audio enable/warning (:12/:20/:22), Mushaf sheet/text/rules (:27), compass cards/status (:43–46), prayer checkboxes (:49), adjustment controls and other later component layers. Final design/light-theme selectors supersede many but not necessarily every pseudo-element or state. A literal inventory follows; it is explicitly not an assertion that all entries win the cascade.

- `dist/style.css:2`: `white`, `#fff`, `#ffffff06`, `#0008`.
- `dist/style.css:4`: `white`.
- `dist/style.css:8`: `#00000007`, `#0003`, `#88888822`.
- `dist/style.css:12`: `#fff`.
- `dist/style.css:20`: `white`, `#0002`.
- `dist/style.css:22`: `#fff`.
- `dist/style.css:27`: `white`.
- `dist/style.css:38`: `white`, `#00000012`.
- `dist/style.css:43`: `#91919118`.
- `dist/style.css:44`: `#fff`, `#1e1e1e0a`, `#000`, `#0002`, `#99999977`.
- `dist/style.css:45`: `#91919118`.
- `dist/style.css:46`: `#0004`, `#1a1a1a`, `#c0c0c018`.
- `dist/style.css:49`: `white`.
- `dist/style.css:57`: `#a6a6a620`.
- `dist/style.css:61`: `#0004`, `#0009`.
- `dist/style.css:67`: `#00000004`, `white`.
- `dist/style.css:68`: `#0005`, `#0009`.
- `dist/style.css:78`: `#0003`.
- `dist/style.css:85`: `#00000012`.
- `dist/style.css:90`: `#fff`.
- `dist/style.css:92`: `#fff`, `#0003`.
- `dist/style.css:94`: `white`.
- `dist/style.css:105`: `white`.
- `dist/style.css:107`: `#fff`, `#0003`.
- `dist/style.css:109`: `white`.
- `dist/style.css:112`: `#fdfdfd`, `#43434308`, `#111`.
- `dist/style.css:127`: `#000`.
- `dist/style.css:135`: `#0008`.
- `dist/style.css:138`: `#0002`.
- `dist/style.css:140`: `white`.
- `dist/style.css:141`: `white`.
- `dist/style.css:143`: `#a6a6a670`.
- `dist/style.css:144`: `#fff`.
- `dist/style.css:147`: `white`.
- `dist/style.css:161`: `#0003`.

No security exploit, secret exposure or arbitrary HTML injection was confirmed. The report does not certify the whole deployment or third-party dependencies; it records this first-party web-source review and the reproducible checks above.

## Follow-up review of implemented fixes

Reviewed current compass generation guard, SW root redirect, NativeQuranPlayer authoritative adoption, public-page theme bridge/CSS, generated city-page wiring, privacy wiring, and their targeted tests. The two original runtime findings are fixed in the inspected source. `tests/fresh-review-regressions.cjs`, `tests/native-quran.cjs`, `tests/infrastructure-regressions.cjs`, and `tests/public-theme.py` passed independently during follow-up.

One test-only blocker: `tests/offline-navigation.py:27–28` waits for an existing `.mushaf-verses` container and immediately asserts its text. Because the container exists before asynchronous Quran loading completes, the test failed in this review even though the runtime worked. An external probe copy at `/workspace/salati-fix/202/offline-navigation-wait-probe.py` waits for nonempty verse text and passed both Arabic/English controlled offline navigations and Quran loading. The source test should wait for actual content before asserting. No app edits made by this reviewer.

The static public theme bridge passed saved dark, saved light, and malformed-storage cases. The theme bridge is loaded with defer, so the initial render may briefly use default light styling before saved dark preference is applied; no functional blocker was identified.

Canonical diagnosis: build-city-pages, app HTML, privacy and sitemap still explicitly use `salati-world-prayer.sprytitan65.chatgpt.site`. `seo-metadata.js` changes title/description only; current runtime host does not rewrite these canonical URLs. Therefore serving this build at `salati-world-prayer.mazenosman968.chatgpt.site` still advertises the previous host as canonical. If the old host is the intended canonical alias this is deliberate; if the new host is a migration destination these links need a coordinated domain migration. Source tests deliberately preserving the old origin are not evidence of deployment routing. No migration recommendation can be made conclusively without routing/ownership facts, and no speculative change was made.
