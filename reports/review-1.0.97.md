# Salati 1.0.97 — approved fixes and requested changes

The owner authorized repairing the infrastructure audit findings and publication, then requested UI, permissions, reminders and widget changes. The owner selected a five-minute spoken approach reminder. No redesign approval is pending.

## Completed behavior

- GPS refresh preserves explicit calculation method and Asr school. An explicitly chosen, validated timezone remains editable and is respected by the calendar engine, provider, saved native schedule and widget; automatic timezone remains available.
- Bad cached web adhan responses are evicted and replaced; fresh responses are cached only after decoding succeeds. Storage quota/privacy failure does not discard decoded playback.
- Adhan completion, timeout and focus callbacks are tied to their service request/generation and release resources promptly. Quran uses a position-progress watchdog and renewable bounded wake leases, allowing normal buffering and pauses without terminating long recordings.
- Android approach reminders use a separate alarm from the actual adhan, default five minutes, configurable5/10/15, with stale delivery/settings rejection, deduplication and a local voice. They yield to existing audio and can leave a short text reminder when speech cannot play. Browser reminders are foreground-only and explicitly described that way.
- Fajr can say «الصلاة خير من النوم» before the selected existing recording. Speech is bounded and cancellable; unavailable speech continues to the adhan. Neither existing recordings nor their playback levels were changed.
- Speech uses the highest-quality installed local Arabic Android voice (no network/not-installed voices); browsers use an installed local Arabic voice. Added preview controls and an Android speech-settings shortcut. A local Arabic voice is required for spoken messages; absent voice data is reported rather than silently claiming speech works.
- Existing first-install notification-before-location order was verified for notification grant and denial, page readiness and older Android versions.
- White Locate button, black/light and white/dark countdown, original smaller24px outline nav symbols, white internal brand symbol over a blue backing, blue dark-mode prayer selection and Qibla, compact silent-mode section and aligned48px adhkar controls.
- Widget mosque fills the background; sunrise/maghrib control day/night overlays independently of OS theme. Missing solar timings use a timezone-aware clock fallback for visual appearance only, never fabricated prayer times. Existing low-frequency transition alarms, live chronometer, six times and app tap remain.

## Verification

All35 JavaScript test commands passed. Native queue/lifecycle/focus tests, reminder scheduling/voice/permissions fixtures, Quran stall tests, offline range tests and widget day/night/DST tests passed. Seven responsive CSS cascade tests passed. Web/SEO build and Android release compilation/lint/assembly passed. APK signing identity, version increase and all packaged assets are verified in release-1.0.97.json. Original audio files were decoded/measured without errors and are byte-identical to the prior release.

Host fixtures substitute Android/browser boundaries; they are not phone instrumentation or visual browser tests. No physical phone, update installation, sleep/wake, Doze/call/Bluetooth behavior or live ad-account fill was tested. Ordinary source playback level cannot guarantee waking a sleeper. Local TTS voice quality and availability depend on the device. Existing polar prayer-calculation limits remain explicitly reported; no unapproved religious estimation method was introduced.
