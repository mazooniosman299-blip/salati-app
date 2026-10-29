# Native permanent-charcoal correction review

Read-only comparison against stable `02d64f56fdf91d4fd24dd33bd41cd686a7d51421`, using `/workspace/attachments/0aec6fc9-9262-417f-8298-9576f3df6147/Pasted text.txt` as the specification. No application files, signing credentials, publication or audio were changed by this reviewer.

## Result

No confirmed compile/API/resource-binding regression or native blocker found in the reviewed correction. This is a source/host-test conclusion, not a claim of physical Android rendering. Licensed replacement approach audio and real-device background/locked-screen audio testing remain outside these changes and still block full acceptance as instructed by the coordinator.

## Checked changes

- Both default and night Theme.Salati / dialog parents are permanently dark, with matching charcoal resources. MainActivity's custom notification confirmation no longer chooses its surface from device uiMode. Shell `#0B0E13`, glass/dialog `#15181D`, white ink and secondary `#AEBCCB` match the supplied values. Ads native container is RGB(11,14,19).
- All 30 widget Java RemoteViews IDs resolve exactly once in the layout. `widget_countdown_label` is removed from XML and Java; no stale resource or setViewVisibility/setTextColor reference remains. The next-prayer icon remains a valid ImageView binding but is GONE in both XML and Java.
- Location and Gregorian/Hijri dates use identical white #FFFFFF, XML17sp bold sans-serif-medium. Runtime setTextViewTextSize changes all three together to10/12/17sp at the same height thresholds. The APIs used by these changes, including RemoteViews.setTextViewTextSize, are available below minSdk26. Existing ICU date formatter is API24+ and both date formatters explicitly use the saved zone.
- Hijri and the upcoming label now stay visible at compact sizes, as required. Upcoming prayer and countdown remain live from the saved schedule. The removed caption does not alter the chronometer setup, next-prayer lookup, prayer-strip data, alarm refresh/recovery or pending intents.
- The original photo is still the widget scenery, at the same position. Its PNG bytes exactly equal the stable version: SHA256 `e1b480d72a5723a35317fcc5442b1096a1465b32ae475837008eed0e351d9add`. No recoloring or generated-image replacement was found in this native diff.
- Root RTL order still places city/dates on the left and upcoming/countdown on the right. Six times remain in the bottom strip. The new date maxLines4 and removal of ellipsize allow more wrapping without a visible ellipsis, but do not provide unlimited vertical space.

## Small-widget and long-date risk

This remains a validation limitation, not a claimed observed Android failure. The provider supports minimum resize height140dp and minWidth280dp. At that size the date column is about109dp wide; the weighted header has only66dp after12dp card padding,54dp prayer strip and8dp header gap. Its location/icon row needs at least22dp, plus7dp date padding, leaving roughly37dp for both wrapped dates. At height220dp the date size jumps17sp, with about106dp column width and138dp available header height.

A host NotoSansArabic-Bold proxy over400 real Gregorian/Hijri date pairs produced up to3 combined date lines at140dp/10sp and5 at220dp/17sp. An em-only estimate can fit at normal scale, so default-size clipping is not established. Actual Android font leading, launcher padding and accessibility fontScale can increase that height. The runtime size selection uses only widget height, not fontScale or measured text. At larger system font settings the fixed header and maxLines4 can therefore clip long dates or the date block. Test140/170/220dp widget heights, long Arabic month/weekday combinations and large font settings on a launcher before claiming the specification's no-clipping criterion. Successful compilation and the web screenshots do not establish this native visual result.

## Verification

PASS: original-photo byte comparison; duplicate/missing widget-ID cross-check; removed-label binding check; identical city/date XML font/color attributes.

PASS: `JAVA_HOME=/workspace/toolchains/jdk-21.0.12.1 bash scripts/test-reminders.sh` (native widget zone/DST/boundary policies, real scheduler method harness, announcement lifecycle and first-install permissions).

PASS: `python3 tests/theme-consistency.py` (first-party palette/native glass checks).

Inspected current `/workspace/salati-fix/206/android.log`: Android debug build succeeded. No release/signing operation was initiated by this reviewer. There is no connected emulator or physical device for native render/launcher/audio verification.

Reviewed native diff: MainActivity.java, PrayerWidget.java, AdsController.java, prayer_widget.xml, provider metadata, default/night colors and styles, widget drawables and original photo identity; app version metadata remains pending1.0.103/code104 under the original application identity.

## Font-metric helper follow-up

Reviewed the new `PrayerWidget.placeTextSize()` StaticLayout-based helper. Measuring the two actual date strings against the weighted left-column width and fixed header budget is a meaningful improvement over height-only thresholds, and all city/date labels still receive one shared size. TypedValue.applyDimension(SP) honors the Android font converter on newer versions; StaticLayout.Builder, simple break strategy and no-hyphenation are API23+, compatible with min26. Removing date maxLines avoids silent four-line truncation.

Sent two metric-alignment concerns for coordinator follow-up before claiming fully robust sizing: StaticLayout.Builder's default fallback spacing must match target>=28 TextView fallback-font spacing (API28 `setUseLineSpacingFromFallbacks(true)` needs a version guard), and a primary-face `paint.getFontSpacing()` city estimate should be replaced/bounded by actual fallback-script city metrics. The installed SDK api-versions.xml confirms the fallback-spacing builder method was added in28. Arabic system-family fallback makes these relevant. Floor the width calculation if choosing a conservative subpixel bound. The8sp lower bound remains best-effort when an extreme font setting yields no fit; this is not universal physical-render certification. No unsupported API was introduced in the helper as initially reviewed.

### Final helper closure

Read-only final inspection confirms both reported metric mismatches are addressed: the actual configured city text is laid out with its one-line/ellipsis behavior and width minus23dp icon allocation, and city/date layouts share guarded API28 fallback-font line spacing. MinSdk26 devices avoid that28-only builder method. All use the same bold sans-serif-medium TextPaint, SP conversion, SIMPLE breaking/no hyphenation and RTL heuristic; date-column width now floors conservatively. The measured city row retains its22dp icon minimum, and all three visible labels still receive exactly the same selected SP size. No new compile/API blocker found. Inspected coordinator release log: build/lint pipeline completed successfully. The8sp lower bound is still best-effort if no candidate fits; no assertion of universal arbitrary-font-scale fit or physical-launcher rendering is made. Audio licensing and device playback verification remain separate acceptance blockers.
