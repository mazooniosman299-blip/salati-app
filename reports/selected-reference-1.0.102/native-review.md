# Selected-reference Android widget review

Read-only review of `/workspace/sites/salati-source`, 2026-10-29. No application files, signing material or publication changed by this reviewer.

## Findings

No confirmed runtime crash, RemoteViews incompatibility or scheduling regression found in the selected-reference native widget changes. The existing scenery view being invisible is intentional while the user's original picture bytes are unavailable; it is not reported as an accidental regression. Exact photo fidelity remains blocked on that asset, with no generated replacement introduced.

## Verified source behavior

- `prayer_widget.xml` uses only FrameLayout, LinearLayout, ImageView, TextView and Chronometer, all framework RemoteViews-supported classes. No custom view or unsupported container was added.
- All 30 `R.id` references in `PrayerWidget.java` resolve exactly once in the layout, including location, Gregorian date, Hijri date, the six existing prayer cells and countdown views. Existing visibility/color/background/chronometer actions still target compatible view types.
- The root RTL order puts upcoming prayer/countdown on the right and the location/date block on the left. The six prayer times remain on one weighted horizontal strip. The location icon is a framework vector drawable, supported below this app's API26 minimum.
- New ICU formatting uses `android.icu.text.DateFormat` / `ULocale`, available since API24. There is no API26 compatibility gap. Gregorian and Hijri formatters both receive the saved schedule zone rather than implicitly formatting in the phone zone; schedule day selection already uses that same zone.
- `PrayerWidget.update()` still looks up today's six timings from saved config, selects the upcoming non-sunrise prayer, rolls to next-day Fajr after Isha, anchors its countdown with elapsedRealtime, highlights the matching cell and opens MainActivity on click. No new network lookup is needed for date/name rendering.
- Compact mode hides Hijri and secondary countdown/upcoming labels below 170dp. Provider minimum/resize range now accounts for the taller layout (170dp initial, 140dp minimum resize, 320dp maximum). Existing sunrise/maghrib appearance and alarm recovery scheduling are unchanged.
- `widget_background.xml`, glass strip and active-prayer drawable use deep navy tones. The remaining overlay black/transparent and white alpha strokes are contrast layers. The old day/night image resources remain selected in Java, but the deliberately invisible scenery view prevents either from appearing until the actual user asset is supplied.
- Default Android version is 1.0.102 / code103, consistent with the requested review context.

## Validation

PASS: XML/source cross-check of all 30 RemoteViews IDs, duplicate IDs and allowed framework view classes.

PASS: `JAVA_HOME=/workspace/toolchains/jdk-21.0.12.1 bash scripts/test-reminders.sh`, including native widget appearance/timezone/DST boundary tests, production reminder scheduling methods, first-install permission ordering and speech lifecycle checks.

PASS: `python3 tests/reference-widget.py` (12 web viewport/theme states). This tests the web reference card, not native launcher rendering.

Inspected `/workspace/salati-fix/203/android-build.log`: coordinator's debug Android assembly completed successfully. This reviewer did not initiate a release/signing operation.

## Limits / follow-up, not confirmed defects

A physical/emulated launcher is still needed to establish actual RemoteViews typography/fit at the 140dp resize boundary, large accessibility font scales, launcher padding, and upgrade behavior for existing previously smaller widget instances. Static source and successful compilation cannot certify those visual cases. The selected Hijri calendar is ICU `islamic`; this is an algorithmic calendar and may differ from local official moon-sighting dates. There is no evidence in the request requiring a different calendar, so no calendar correctness defect is asserted.

Reviewed files: PrayerWidget.java; prayer_widget.xml; prayer_widget_info.xml; ic_widget_location.xml; widget_background.xml, widget_glass_header.xml, widget_glass_strip.xml, widget_overlay_day.xml, widget_overlay_night.xml, widget_prayer_active.xml; WidgetAppearancePolicy.java and its policy test; app/build.gradle. Existing schedule/countdown implementation was compared against the previous reviewed source. The review does not certify the missing source picture or physical Android behavior.
