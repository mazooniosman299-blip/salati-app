# SALATI-20261107-MUSCAT-12H-GLOBAL-GUARDS

User-approved exact reference: Muscat November 7, 2026, Oman local 12-hour clock:
Fajr 4:59 AM, Sunrise 6:16 AM, Dhuhr 11:56 AM, Asr 3:07 PM, Maghrib 5:30 PM, Isha 6:42 PM.
Source: https://www.mara.gov.om/arabic/calendar_page2.asp

Do not apply one city's official time to other cities; preserve default astronomical calculation and user custom minute offsets for all unsupported places, mark those values calculated.
Use MUIS Singapore data only for matching 2026 civil dates/geography/method/zone:
https://data.gov.sg/datasets/d_d441e7242e78efc566024dd5b0d9829c/view

The 12-hour convention governs human-readable display, never the UTC epoch used for Android alarm scheduling.
An Asr madhab switch must never alter official source Sunrise or Isha. Do not show official provenance for invalid date, geography or timezone. The automatic GPS-to-city behavior is untouched in this request to prevent untested changes in other locations.

Unpreventable future risks: official calendar policy changes, DST database revisions, new years not backed by source data, local religious authorities with different methods, phone clock/GPS errors and OS alarm restrictions. They cannot be guaranteed away forever. The guard blocks documented regressions and records coverage.

Deployment protection: preview branch ONLY. NO merge to production, no website publication, no Android release until exact-head CI (tests + true screenshots), valid original-key higher-version signed APK + matching website bytes, real in-place Android testing and explicit acceptance.
