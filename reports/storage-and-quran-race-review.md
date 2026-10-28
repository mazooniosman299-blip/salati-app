# Quran queue and browser storage review

- Reproduced `QuranService.queue()` throwing NullPointerException when session replacement cleared `rows` between its null check and second read on the JavaScript bridge thread. The bridge now reads one snapshot; the array reference is volatile for cross-thread visibility.
- Reproduced PrayerAudio initialization failing when the localStorage getter throws, and scheduled playback being skipped when getItem/setItem throws. Storage acquisition and operations are guarded; a bounded in-memory set prevents repeated playback during the same controller session. Cross-reload deduplication cannot persist while browser storage is unavailable.
- Existing restoreSettings normalization and guarded JSON parsing already handle the malformed settings covered by review-regressions and preferences-storage. Those tests pass; no additional settings behavior change was needed.

Regression commands: npm test; JAVA_HOME=<JDK> npm run test:quran-race; npm run test:quran-background; npm run test:audio-focus. The queue regression compiles the production queue method into a concurrent Java fixture, not an Android device instrumentation test. Web playback tests simulate the browser storage failures. Physical-device background playback was not tested.
