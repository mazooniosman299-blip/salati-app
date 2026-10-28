# Application review — 1.0.90

The user requested a broad application review alongside spacing/navigation corrections. Reviewed the application modules by subsystem: startup/storage and location intent, GPS/country/place selection, calculation/provider/cache and calendar refresh, adhan settings/voices/audio/native synchronization, Quran controller/continuous cues/follow/offline/native mirror, adhkar/tasbih, picker/popover controls, and theme/layout. Reviewed Android activity/bridge/permissions/insets, receivers/schedule/widget, Quran and adhan services, PCM output/focus/volume, offline files/downloads/ranges, and optional ads initialization/visibility.

## Confirmed defects fixed

- The general action-button sizing rule also resized the nested adhan switch; retain the direct-child fix from unreleased 1.0.89.
- Card margin shorthand displaced capped centered cards to one side. Restore inline auto margins using selectors present in the actual HTML.
- Fixed mobile navigation inherited stretch/auto sizing. Give the container and track explicit consistent dimensions; account for safe area once. Preserve browser insets and the native root's system padding.
- Section switching reused the previous section's document scroll. Save independent positions and restore before Quran follows the playing verse. Ignore repeated active-section clicks and blur fields in the departing panel.
- Persisted calendar JSON could be null, or contain invalid entries. Reproduced a TypeError on opening prayer screens, and a null-entry refresh failure. Validate stored record structure; keep valid offline data and permit network recovery.

## Validation

- Complete npm test suite, responsive CSS cascade regression tests at phone/tablet/desktop widths, SEO/static-link checks, JS/CSS syntax and DOM ID/asset checks.
- Java executable tests for Quran queue progression, audio-focus interruption/restoration, alarm volume/delivery, local audio range requests, and ad visibility/initialization.
- Web and Android release builds, Android lintRelease, fixed-certificate APK verification, package/version comparison, and byte-exact comparison of every packaged web asset.
- Lint: 0 fatal/errors; 33 warnings reviewed. These concern synchronous persistence used for durable alarm/file state, API-guarded or ignored-on-old-device fields, deliberate local WebView JavaScript, lifecycle-managed playback wake locks, backup policy guidance, and widget resource/layout/localization suggestions. They are not represented as zero warnings.

## Limits

No supported browser renderer or physical Android device was available. Automated cascade checks do not demonstrate pixel layout. The previously authorized publication without browser QA remains applicable. An independent reviewer returned preliminary navigation findings, then stopped at its usage limit; the remaining review was performed directly. This review does not guarantee absence of all defects.
