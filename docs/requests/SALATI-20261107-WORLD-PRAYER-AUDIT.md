# SALATI-20261107-WORLD-PRAYER-AUDIT

## User's exact instruction
> حل المشكله دي كامل ومامسقط فقط كل دول العالم راجع توقيته لو لقيت في اختلاف صلحو

## Boundaries and source of truth
- Compare individual religious ministry/authority prayer tables with exact same city/date/madhab, rather than pretending a single universal astronomical method is a legally or religiously official calendar for every country.
- Proven divergence: Muscat, 2026-11-07, official Oman Ministry 04:59,06:16,11:56,15:07,17:30,18:42 vs running app 04:58,06:17,11:55,15:06,17:29,18:42.
- The ministry's entire 2026 November Muscat month was read from https://www.mara.gov.om/arabic/calendar_page2.asp and embedded with explicit date/city validity. Existing October 2026 dates preserved.
- Outside this limited verified official dataset the app continues the already existing country-specific Adhan settings. Do not claim that applying one minute everywhere is safe.
- Global computational audit: preexisting `tests/global-prayer-calendar-audit.cjs` covers 246 inhabited country/territory data files with 2,976 city/month cases plus timezone, manual offset, DST and date-line tests; this is *not* proof of minute-perfect agreement with each country’s authority.
- Country calendars must be added only after reliable authoritative year/month/city/date records and explicit scope/rights are established; fail closed on missing records, do not invent clock times.

## Native release safety
- Runtime code changed. The original signed v1.0.133 APK is NOT byte-compatible with new web scripts; do not publish a web update as though the old APK were updated.
- Preview/review only until full source/browser/native checks and a fresh original-key signed release and website fingerprint have passed. No forced release on arbitrary user acceptance.
