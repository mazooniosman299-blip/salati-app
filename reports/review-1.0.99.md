# Salati1.0.99: recorded voices and neutral glass

## Final requested behavior

The user rejected synthetic voice recordings, generated mosque imagery, and blue controls. The application now uses two existing recorded excerpts and real photographer-published day/night mosque images. No voice or image generation/AI enhancement was used to create these replacements.

The user explicitly chose the genuine recorded «حي على الصلاة» call for approach reminders. All five prayer events play that shared call; the individual prayer name remains in the notification. Fajr uses one complete «الصلاة خير من النوم» excerpt. No new speaker-name UI was added. Attribution is retained in source/provenance documents.

- Approach clip:10.8seconds, contiguous excerpt of the existing owner-supplied recording.
- Fajr clip:19.75seconds, existing2014 SoundCloud recording credited by its publisher, who enables downloads and invites sharing.
- Source documents: dist/audio/reminders/SOURCES.md and verification.json.
- Removed all six rejected synthetic clips and their generation scripts. Distinct immutable human-file URLs avoid serving old cached synthetic clips after an update.
- Extended playback deadlines to allow complete human phrases:30seconds controller,33seconds reminder-service bound,35seconds wake lease/prelude safety. Actual adhan continues after prelude completion/error and remains cancellable.

## Visual direction

Neutral charcoal/frosted glass surfaces replace blue and gold controls. The selected prayer uses a glass pill. Navigation uses locally bundled Phosphor icons and Motion for its sliding selection. Controls remain44px touch targets with smaller visual styling; Tasbih action52px. Light text is black; dark text is white. The countdown retains black/white. Reduced motion and reduced transparency have explicit fallbacks; Quran glyphs stay sharp.

Mosque photographs are by Mauricio Krupka Buendia(day) and Reyyan(night), published on Pexels. The pair shows matching real architecture and dry ground. Conventional cropping brings the mosque closer and removes foreground distractions. Both source titles are preserved in attribution links, but the app makes no building-name claim. Credits/license/crop coordinates: dist/images/MOSQUE-SOURCE.txt.

## Review findings fixed before release

- Motion selection did not move after RTL/LTR language reversal with the same active tab. Watching document dir/lang and snapping geometry fixes it; Chromium regression failed first, then passed both directions.
- Fajr prelude ignored live volume and audio-focus ducking. Forwarding updates to its local PCM player fixes both without changing focus-pause or adhan continuation. Wrapper and service tests reproduced the old behavior before the fix.
- Previous short synthetic-clip deadlines would cut complete real phrases. Tests now hold playback beyond14seconds and verify bounded completion at30seconds.

## Validation limits

Full JavaScript tests, native reminder/lifecycle/focus tests, real Chromium previews including offline playback, six viewport widths/both themes/keyboard/RTL, Android resource compilation and release build, signing verification and exact packaged-asset comparisons are recorded in release-1.0.99.json. Dependency audit found zero reported vulnerabilities at verification time.

No physical Android device or subjective human listening test was performed by this environment. Source attribution and unprompted transcription support recording identity/content; signal measurements verify levels, not subjective sound quality. User-accessible audio samples were supplied before publication.

The obsolete1.0.68 APK was removed from the hosting tree to stay within hosting size limits. A private workspace copy and previous Git history retain it; recent APKs remain available.
