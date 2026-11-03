# Salati Mushaf V2 — user visual review only

## Original request
«الفكره كامله صحيحه ... عاوز اغير شكل المصحف كلو كامل واتاكد انو مايكون في دائره سوداء والمشغل قلل حجم الاطار حبه» ثم «رد بشكل تفاعلي بعد التعديل».

## Actual intended changes
The full screen and genuine Quran reader architecture remain. Only the active Quran tab's entire visual presentation is restyled through `dist/mushaf-book.css`, replacing the gold/cream dense ornamental design with a clean ivory and ink-blue page, slim double manuscript rules, blue diamond corner ornaments, a pale blue chapter heading, and light geometric verse-number medallions. No black filled circular UI decorations. Quran text, Uthmani marks, original 604-page line map and audio are unmodified.

The player is slightly smaller: outer charcoal sheet #18191D, blue #2563EB play button reduced from 60px to 54px, waveform height reduced to 32px. Slider/reciter/stop/prev/next/repeat keep their original real event handlers.

## Acceptance and delivery
Capture genuine application screenshots in Chromium at 390×844 and 430×932 of page 1 (with player, without player) and page 564. Test the same Quran source integrity, navigation, player visibility, 63 variable bars and exactly 0 black filled circular UI elements. Player height must be at most 160px. Check the suite and build a separately installable preview APK, but **do not create a GitHub Release, merge PRs or deploy production before the user's visual approval**.

The five known non-exact printed-line pages (208, 586, 587, 590, 591) and pixel-exact QCF typesetting limitations still exist and must not be falsely described as fixed.
