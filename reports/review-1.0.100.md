# Salati 1.0.100 — source review and regression record

## Scope

Read-only independent reviews covered all 33 root application JavaScript modules, the four city-page modules, build/preparation/signing/recovery scripts and shell runners; all 23 main Android Java classes, noAds and ads Java sources, manifests, Gradle configuration and widget resources. This is a review of application-owned source. It is not a claim that third-party libraries, large Quran/adhkar/world data, generated binaries or every possible runtime path have been manually audited.

The coordinator reviewed the actual HTML/CSS cascade and current screenshots. User-provided screenshots showed washed-out nested panels, weak control hierarchy and navigation unlike the requested reference. Audio provenance and routing were checked separately from interface appearance.

## Confirmed issues and changes

1. Two distinct announcement controllers could retain PCM/HTMLAudio outputs simultaneously. New web and Java tests reproduced the issue before fixing owner replacement. Starting a replacement now stops the previous output; stale completion callbacks cannot finish the replacement.
2. The approach clip said `حي على الصلاة`. The user has now approved the real human per-prayer recordings saying `اقتربت صلاة…`. All five phrases map independently on web and Android, preserving selectable 5/10/15-minute lead times without speaking a fixed number of minutes.
3. The prior engineered Fajr SoundCloud recording was reported as doubled. It has been removed from the current application and replaced with a contiguous phrase from the existing mosque Fajr recording. No new synthetic speech, word assembly or voice cloning is used. Sources and exact hashes are in `dist/audio/reminders/`.
4. QuranService lost pending resume intent on consecutive transient audio-focus losses. A test using the production handler reproduced the issue. Resume intent now persists, while explicit user pause and permanent focus loss suppress resumption.
5. The Quran lifecycle test fixture had not been updated when the adhan prelude acquired volume handling. Its missing boundary field is corrected and the test compiles again.
6. Nested glass backgrounds and desaturation flattened the dark theme. One glass surface now owns each panel; inner fieldsets, volume and transport groups are transparent separators. The obsolete Tasbih inner frame and the Adhkar library card wrapper were removed at their original definitions, with real-browser regressions for both. Glass retains saturation, a highlight edge and a controlled shadow. Primary controls have explicit foreground/background contrast in both themes.
7. The inherited SVG stroke was removed from the filled Phosphor sprite; navigation uses circular glass icon mounts and one animated selected circle, with consistent 24px icons and full label hit targets. Reduced motion and transparency are respected.
8. App stylesheets use the same version as the JavaScript entrypoint, avoiding a cached stylesheet from an older release being mixed into a new release.
9. The widget no longer darkens the entire photograph with a gray veil. Contrast comes from bounded text strips. Image framing is independent from text readability; day/night scheduling behavior is preserved.

## Verification

The complete JavaScript suite passed. Native queue, service-race, lifecycle, consecutive-focus, stall recovery, alarm/audio-focus/volume, reminder scheduling, first-install permission and ads boundary suites passed. Seven responsive cascade checks passed. Chromium checks exercise all six tabs across six widths in light/dark, keyboard menus, language direction, reduced motion/transparency, switch geometry, readable controls, no horizontal overflow and no page errors.

Real browser audio tests check both preview buttons, rapid replacements with at most one active HTMLAudio output, all six clips cached offline and completion of the offline Fajr preview. These tests establish playback behavior, not subjective recording quality.

Release build, signature, packaged-byte and final screenshot results are recorded in the release manifest when packaging finishes.

## Limits

No physical Android device, launcher, audible listening session, overnight alarm, real GPS trip or in-place APK installation was tested here. App-widget appearance varies with launcher size. Static review and automated tests cannot guarantee a program has no remaining defects. User acceptance of voice tone and visual taste remains distinct from objective playback/layout verification.
