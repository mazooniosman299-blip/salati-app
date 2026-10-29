# Fresh Android review — 2026-10-29

Scope: read-only review of `/workspace/sites/salati-source` at HEAD `2a1fb07`, including the coordinator's concurrent palette work. No app source was edited by this reviewer. Private signing files and credentials were not opened. Review artifacts only are written under `/workspace/salati-fix/201/`.

## Confirmed issues

### P2 — An older Android Activity permanently rejects a newer native Quran session

Evidence: `native-quran-player.js:18` sets `expected=true` for every `playQueue()`. No method clears it. `apply()` at line 9 then ignores every different session, even after the original session was acknowledged, and even through `sync()`/resume/visible polling (lines 5, 8). `QuranService.java:16` discards commands for a session other than its current one.

The Android manifest line 6 gives MainActivity standard launch behavior. Quran notification (`QuranService.java:53`), adhan notification (`AdhanService.java:10`), widget (`PrayerWidget.java:15`), and alarm show intents (`PrayerSchedule.java:10`) target it without activity reuse flags. Opening the notification from an already running app can therefore create a second WebView.

Reproduction: Activity A starts Quran session A; open Quran notification to create Activity B; B starts another surah/session B; press Back to A. A's resume and polling continue displaying A; Pause/Seek/Stop target obsolete A and are ignored while B continues. This is a concrete adapter failure, not a claim that notification task behavior was physically tested.

Executable host reproduction using the actual bundled module: `node /workspace/salati-fix/201/repro-native-session.cjs`. It instantiates the two native-player owners, acknowledges A, starts B, dispatches the native-resume event, and verifies that the old owner remains A and sends its Pause command to A. Current source prints `reproduced: true`.

Minimal robust direction: make `expected` represent only an unacknowledged start, clearing it after a matching native snapshot and on stop/rejection. Distinguish authoritative `quranState()` synchronization from pushed events: after acknowledgement, authoritative polling can adopt the actual service session; mismatched delayed event payloads should continue to be rejected. Unconditionally accepting a different session on resume is unsafe because `quranPlay()` returns before the service consumes the staged request, so a resume sync may still observe the old service snapshot. Add cases for pending start vs old state, acknowledged A -> B takeover, and delayed old pushed events.

Existing `tests/native-quran.cjs` restores a newly created player (whose expected flag is false), so it does not exercise returning to a player that previously initiated a session.

### P2 — Returning to an older Activity loses the native event destination

Evidence: `MainActivity.java:17` assigns `current` only in `onCreate()`. `onDestroy()` at line 103 (pre-palette line layout) clears it when that Activity is current. `onResume()` at line 101 does not reclaim it. All notify methods at lines 9–14 send events through `current.get()`.

Reproduction: create Activity A; open a native notification to create B; Back destroys B and resumes A. B's onDestroy clears current; A's onResume never sets it. Subsequent native adhan, announcement, playback and Quran events have no live destination. Quran has polling recovery only if the preceding issue is also corrected; adhan/announcement events and native ad suppression have no equivalent reclaim mechanism. A is visibly active but not reachable by the native callback bridge.

Minimal correction: set `current` to this in onResume before emitting native-resume/status events; keep the existing identity check onDestroy so an old Activity cannot clear a newer owner's reference. Alternatively guarantee one Activity via a deliberate launch/task policy and test notification/widget/task entry points, but restoring current onResume is independently appropriate. Add a production-method lifecycle harness for A create/resume -> B create/resume -> B destroy -> A resume -> notification recipient A.

## Device checks / gaps, not confirmed regressions

- QuranService has no `ACTION_AUDIO_BECOMING_NOISY` listener. Headphone/Bluetooth disconnection may route the existing stream to speaker. Verify on a device and decide whether to pause on route loss; do not count host policy tests as proof of audio-route behavior.
- Repeated Activity entry from notification/widget deserves a real Android task-stack check in addition to the deterministic adapter reproduction above.
- Exact alarm delivery under doze, process death, reboot, permission revocation, DND/ringer/volume changes, full downloads after Android's DownloadManager cleanup, real launcher sizing, and sensor accuracy cannot be established by these host tests.
- The compass JS explicitly rejects landscape and corrects reverse portrait (`compass.js:10–13`); missing Java screen-axis remapping is therefore not reported as a bug.
- Legacy Sudais files are deliberately excluded from playback and download controls because the selected studio edition differs. The broad native download server helper is not alone evidence of an exposed user-facing Sudais download bug.
- The shader/text/icon white alpha values are intentional glass/monochrome content, not neutral-gray surface bugs.

## Native palette inventory (snapshot before coordinator changes)

| Location | Existing surface / text | Recommendation |
|---|---|---|
| MainActivity.java:17 | Four `Color.BLACK` uses: system bars, root and WebView | Reference navy base so startup/insets do not flash black |
| MainActivity.java:82 | Dark surface `#171717`, white light surface; dark ink `#F5F5F5`, light ink `#18212B` | Navy glass confirmation surface and compatible ink |
| MainActivity.java:86 | Dark `#CCCCCC` / light `#4B5563` secondary text | Cool blue-gray secondary ink |
| MainActivity.java:87 | Gold button `#D4B87F`, charcoal label `#171717` | Reference cool blue action and high-contrast text |
| AdsController.java:51 | Container `Color.rgb(20,20,20)` | Navy surface matching native shell |
| drawable/widget_background.xml | `#252A33` | Navy base |
| drawable/widget_glass_header.xml | `#C012141B` -> `#A612141B` | Translucent navy glass |
| drawable/widget_glass_strip.xml | `#C012141B` -> `#D912141B` | Translucent navy glass |
| drawable/ic_salati_background.xml and drawable/ic_salati.xml | `#252A33` launcher-icon backing | Optional matching navy backing if icon is in requested scope |
| widget_overlay_day/night.xml | Transparent to `#24000000`, white-alpha outline | Keep transparent shadow or tint it navy; not opaque gray |
| widget_prayer_active.xml, widget layout | White alpha glass fill/outline; white text and black-alpha text shadow | Functional contrast layers; retain unless visual evidence calls for a tint |

The manifest still sets a framework light theme for native AlertDialog/permission settings explanation. App-drawn confirmation is custom, but other AlertDialog surfaces inherit the framework palette; a full all-native-palette claim should account for those surfaces. Android OS permission dialogs and notification/consent SDK windows are system/SDK controlled.

## Files reviewed

All 23 main first-party Java files: AdhanService, AlarmDeliveryPolicy, AlarmVolumePolicy, AlarmVolumeSession, ApproachPolicy, ApproachReceiver, ApproachService, ArabicSpeech, AudioFocusPolicy, MainActivity, PcmAudioPlayer, PlaybackWatchdog, PrayerReceiver, PrayerSchedule, PrayerWidget, QuranAudioFiles, QuranAudioRange, QuranDownloadReceiver, QuranDownloads, QuranPlaylist, QuranService, RestoreReceiver, WidgetAppearancePolicy.

All three ads-module Java files: AdsController, AdInitialization, AdVisibility; noAds AdsController. Main/ads manifests; root/app/ads build.gradle, settings.gradle, gradle.properties, ads-config.gradle and wrapper distribution properties. Public publisher identity/signing credentials were unnecessary for this review and were not opened.

Resources: prayer_widget.xml, prayer_widget_info.xml, strings.xml, all drawable XML, v26/v33 adaptive icon XML. Widget raster day/night resources inventoried as image assets; no claim that their rendered launcher appearance was device-tested.

Native contracts and related paths: native-adapter.js, native-prayer-audio.js, native-quran-player.js; quran-page-audio.js, quran-offline.js, relevant quran-controller.js playback/restore source, compass.js, scripts/prepare-android.py. Tests reviewed include native-quran.cjs, native-audio.cjs, native-sync.cjs, native-schedule.cjs, prayer-announcements.cjs and all Android Java policy test classes; production-method first-install permission, ArabicSpeech lifecycle and approach-scheduling harnesses were exercised.

## Verification run

PASS: `node tests/native-quran.cjs`, `node tests/native-schedule.cjs`, `node tests/native-sync.cjs`, `node tests/native-audio.cjs`, `node tests/prayer-announcements.cjs`.

PASS with `JAVA_HOME=/workspace/toolchains/jdk-21.0.12.1`: scripts/test-audio-focus.sh, scripts/test-ads.sh, scripts/test-reminders.sh, scripts/test-quran-offline.sh, scripts/test-quran-background.sh. These include extracted production-method lifecycle/scheduler/permission checks. The initial shell test invocation lacked JAVA_HOME and reported javac not found; rerunning with the installed toolchain passed.

No signed/release build was triggered by this reviewer because release prebuild performs signing-identity validation and the coordinator owns the build. No emulator/physical device was connected for this review. Findings are independent of palette CSS edits. Line references refer to the reviewed source before coordinator edits and may shift during fixes.

## Fix re-review

Reviewed coordinator changes to native-quran-player.js, MainActivity.java, manifest, ads container, values/styles.xml, values-night/styles.xml and values/colors.xml / values-night/colors.xml. The acknowledged-session takeover correction is sound: authoritative polling can adopt a newer service session only after pending-start acknowledgement; foreign pushed callbacks cannot roll it back. Stop/rejected-start clears expected. onResume reclaims current, and identity-guarded onDestroy preserves newer owners. New resource/theme references are coherent; system-theme night variants cover framework AlertDialog colors. No new blocker found in these edits.

Re-run PASS: tests/fresh-review-regressions.cjs (compass cancellation / native session takeover / offline nested navigation), tests/activity-owner.py using the installed JDK, existing tests/native-quran.cjs and tests/native-audio.cjs. New tests exercise actual adapter and extracted production Activity methods. They verify returning A -> acknowledged B, pending-start protection against old native state, late old pushed payload, and stopping without revival.

Two narrow remaining robustness gaps were sent to the coordinator: a start superseded by another owner before its first acknowledgement can leave that old owner's expected flag set (new test currently acknowledges A before starting B); and an old Activity's AdsController can retain stale nativeAudio state unless onResume reapplies static nativeAdhanPlaying/nativeApproachPlaying before ads.resume(). These are pre-existing concurrent-Activity cases, not new palette regressions. Headphone routing/physical task-stack behavior remain device validation items.

### Final closure after additional coordinator fixes

The coordinator addressed both narrow gaps. QuranService now keeps volatile requestedSession metadata across stage/take and returns it alongside the last playback snapshot; the adapter allows a pending owner to adopt a superseding authoritative snapshot only when requestedSession matches that snapshot's session, proving that the newer request has reached playback state. A pending request cannot accidentally revert to an older snapshot. Native pushed payloads remain unable to switch sessions. MainActivity reapplies current native playback flags before ads.resume(), closing the old-Activity cached-ad-state gap.

Final read-only verification PASS: `node tests/fresh-review-regressions.cjs`, `JAVA_HOME=/workspace/toolchains/jdk-21.0.12.1 python3 tests/quran-request-state.py`, the same JDK invocation for `tests/activity-owner.py`, `node tests/native-quran.cjs`, `node tests/native-audio.cjs`. Superseded-before-acknowledgement C->D recovery is now explicitly covered. No remaining important source regression or blocker found in the reviewed native/session fixes. Real-device limitations above still apply.
