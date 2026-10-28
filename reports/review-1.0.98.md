# Salati 1.0.98

## User-requested changes

- Replaced installed-device Arabic TTS with six bundled fixed Arabic recordings; removed Arabic voice settings.
- Preview buttons display loading/playing/finished/error/blocked/muted state. Both previews run with automatic adhan disabled. Existing audio wins over reminders; stop and Quran actions cancel reminders.
- Foreground browser reminders and Android background alarms retain 5/10/15-minute scheduling, default five minutes. Fajr phrase precedes the existing selected adhan; a missing/failed phrase cannot prevent adhan playback.
- Rebuilt Qibla and Tasbih presentation, uniform 24px navigation, blue/white launcher and web identity, custom interval list, navy switches and theme contrast.
- Widget now has distinct matching day/night mosque backgrounds, sunrise/maghrib switching and independent recovery refresh.

## Bugs found and repaired during verification

- Missing installed Arabic voices previously ended speech previews without a sound.
- Bound browser timer calls raised Illegal invocation in real Chromium. Default timer wrappers now preserve the global receiver; real preview regression test failed before the fix and passed after it.
- Service worker bypassed every audio request, including newly precached reminder clips. Reminders now use a dedicated cache-first path; legacy adhan audio keeps its existing cache behavior.
- Two checkbox pseudo-elements could paint two overlapping thumbs. Final cascade and browser checks enforce one thumb.
- Reminder cancellation from an old service can no longer overwrite a newer Fajr-prelude status; local playback owns its status lifecycle.
- A CSS filter flattened the new opaque app icon; header now displays the actual blue/white icon.

## Validation and limits

Automated JavaScript behavior tests, Android reminder and audio lifecycle tests, actual Android release build, resource linking, signing identity checks, responsive cascade checks, Chromium layout/keyboard tests and real HTMLAudio preview/offline tests were run. Detailed release evidence accompanies this file.

The six new recordings use the same generic Arabic Hamed preset. Unprompted ASR matches all intended phrases; numeric decode/peak checks found no clipped samples. This verifies content and signal properties, not subjective pleasantness. No human listening or physical Android device test was performed here. Physical phone playback, OEM battery restrictions, speaker volume and installed-update experience still need device validation.

Widget background images are original generated architectural concepts, not photographs identifying a real mosque. Appearance uses the configured location's sunrise/maghrib; system alarm/Doze scheduling can delay updates.

The obsolete public 1.0.67 ZIP was removed from the hosting tree to stay within the static hosting size limit; its prior Git history and a workspace archive retain it. All existing APKs remain available.
