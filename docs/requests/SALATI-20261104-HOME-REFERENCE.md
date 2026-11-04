# SALATI-20261104-HOME-REFERENCE
Status: قيد التنفيذ

Original user wording (verbatim):
> النص دا اعملو  ابيض **الجزء الأول**
> وعاوز اغير الشاشه الرئيسيه  بالشكل دا فقط في الشاشه الرئيسيه وليس الويجدت لازم يكون زيو ميه الميه ماتنشر الا تتاكد انو مطابق للصوره دي  والكلمه دي اعمله برضو ابيض **إلى البيت الحرام والكمله دي برضو ابيض ثبّت التطبيق على هاتفك لاستخدام أذان الخلفية وويدجت المواقيت. أندرويد ٨ أو أحدث.**
> اتاكد انو كلامي نفذ 100 في الميه

Later explicit asset approval (verbatim): «مامشكله استخدم نفس صورة المسجد» in reply to the original-photo question. Use unchanged existing mosque-reference-original.png; the reference's different mosque photograph is now an explicitly authorized exception. No generated or third-party substitute.

Base: verified production5eee10c / official1.0.127, fresh branchfix/home-reference-20261104. Target is the inline455x457 home screenshot, not historical widget screenshots. Inline source is visible in this conversation but its original bytes are not mounted; do not claim automated pixel equality. Match measured layout and manually inspect actual captures. Publication requires visual review first.

Affected owners: dist/index.html #times overview/hero/prayers; app-source.js render/tick; dist/salati-ui.css narrow home component. #qTrack Juz text; #qibla .eyebrow; #androidDownload>p foreground only. Keep one canonical stylesheet, no forced priorities.

Measured target at455px content width: hero182px high, city top-left, small top-right prayer pill, next prayer/name/time right aligned; divider at194; cards panel begins206, heading18px and white, 3 equal columns x2 rows; 8px horizontal panel padding, 8px column gap,10px row gap, tiles90px high/radius12px. Fajr/sunrise/dhuhr then asr/maghrib/isha in RTL. White icons/labels/time with AM/PM. Selected tile lighter charcoal. Preserve runtime times, never hardcode screenshot's sample times or city. Desktop retains same single grid, adapts hero height. Dates/countdown/location/calculation remain reachable below dashboard in existing calculation details; nav and other tabs unaffected.

Preserved: all native widget source/resources and mosque bytes, native background adhan/receivers, prayer engine/timezone/manual adjustments, city settings/data, bookmarks/preferences, all Quran plates/verse content/audio/direct selection/Fatiha entry. No unrelated recolors. #qTrack, Qibla eyebrow and Android paragraph color only.

Allowlist: ACTIVE_CHANGE.json is authoritative exact path list. Release paths will be added only after reviewed visual implementation, original-key matching APK remains required before publication.

Tests: real Chromium at320/390/455/768/1440, Arabic/English and language/reload/tab restoration; calculated time vs actual next-prayer card, one highlight,3x2 ordering/gaps/radii/icons, white requested text; location unavailable state; settings/date/countdown access; six-tab functionality; widget source bytes vs base. Visual capture at455 dashboard content width and responsive sizes; retain evidence. Record user-authorized existing-photo exception explicitly. Full CI/signed upgrade before normal merge. Physical device not available, no claim.

Stages: source/build/function/browser/visual/Android/signing/publication not yet verified. User acceptance after implementation not yet requested or claimed.

Latest steering (verbatim): «اولا كلمة ص دي مافي في الصوره الرسلتها ليك انا قلت ليك قارن وتاني شي محاذاة النصوص مانفس الصوره الرسلتها ليك انت دقق شديد وحتفهمني». Explicitly remove Arabic AM markerص from home only; retain requested referencePM markerم and English formatting. Correct real RTL flex cross-axis error: flex-end aligned variable-width hero children physically left inside the right-positioned cluster. Use stretched child boxes with right text alignment. Add real text-range right-edge assertion to prevent recurrence. This scoped instruction supersedes the initial screenshot AM marker, even though the inline picture shows it. No widget formatting change.

Necessary test dependency: computed-style capture now records the three narrow recolor selectors and #times for actual scope comparison. The Android description lies below viewport: its clipped allowance originally had inverted y bounds and crashed PIL. pixel_scope clips rectangles to viewport and ignores empty intersections; added negative assertion that off-screen allowances grant zero pixels. No outside-change threshold or visual assertion weakened.

Review candidate1.0.128/code129 is prepared only after actual captures,10 home responsive cases/3 empty states, seven-size full-tab regression,9 Fatiha/audio scenarios and48 scoped comparisons passed. Request alignment clarification remains pending after user rejection; do not merge/publish on assumed silence. Signed release metadata/build is necessary to make exact payload reviewable, not permission or proof of visual acceptance. Matching website/APK and original identity retained;127 remains live until every gate and visual decision pass.

Alignment clarification answered verbatim «هذه المحاذاة هي المقصودة». The revised physical-right text alignment is approved; no further permission required for that choice. Final3x2 geometry and manually reviewed real capture match the revised component spec, with existing photo and AM removal explicitly authorized. Automated reference pixel equality is not claimed (inline original bytes unavailable). Prior QA archived before writing new scoped QA; user full post-publication acceptance remains separate.

First PR CI root-cause job126645747007 failed before parity iteration: «Optimized CSS unexpectedly grew», because its126 fixture forbids intentional new home layout or requested foregrounds. Source/runtime already passed local actual48 scoped comparisons. Preserve126 fixture; add source-controlled128 approved CSS snapshot after manual/user alignment review. All36-case44-property geometry equality/size assertions unchanged. This is a test-reference update only, no runtime/signature changes. Rerun exact-head CI before merge.

Initial integration job126645745190 also waited for retired .hero-picture img. Update only the locator to actual .home-hero .home-mosque; retain original1120px natural width, exact original source path, actual offline service-worker/deep-link/location/Quran assertions unchanged. Historical home-widget screenshot suites remain historical; native widget tests unchanged.
