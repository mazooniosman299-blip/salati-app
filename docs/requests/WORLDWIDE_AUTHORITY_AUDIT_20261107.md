# Worldwide official prayer-time audit — 2026-11-07 (RELEASE BLOCKER)

## Requested outcome
User instructed to demonstrate correct prayer times for the entire world **before** any official publication. The app must not be represented as worldwide authority-certified based only on astronomical computations, international city coverage, or 12-hour formatting.

## Independent authority evidence, tested against exact candidate PR #60 calculation engine
Date: **2026-11-07**, city-local civil date; default method, Shafi Asr, zero minute adjustment; expected times quoted from independent country government/religious authority, not from the app or the Adhan library.

| Location | Official fajr / sunrise / dhuhr / asr / maghrib / isha (24h internal) | Actual candidate engine | Delta candidate minus official (minutes) |
|---|---|---|---|
| İstanbul, Türkiye | 06:08 / 07:35 / 12:53 / 15:35 / 18:01 / 19:22 | 06:08 / 07:35 / 12:53 / 15:34 / 18:00 / 19:22 | 0 / 0 / 0 / -1 / -1 / 0 |
| Kuala Lumpur, Malaysia | 05:48 / 06:56 / 13:00 / 16:21 / 18:58 / 20:10 | 05:37 / 06:57 / 12:57 / 16:19 / 18:57 / 20:08 | -11 / +1 / -3 / -2 / -1 / -2 |
| Cairo, Egypt | 04:45 / 06:13 / 11:39 / 14:41 / 17:03 / 18:23 | 04:45 / 06:14 / 11:40 / 14:41 / 17:04 / 18:23 | 0 / +1 / +1 / 0 / +1 / 0 |

Original independent references:
- Türkiye Diyanet: https://namazvakitleri.diyanet.gov.tr/tr-TR/9541/istanbul-icin-namaz-vakti
- Federal Territory Mufti / JAKIM official full 2026 Kuala Lumpur and Putrajaya PDF, page 12 November row 07: https://www.muftiwp.gov.my/images/falak/takwim/jadual-waktu-solat/KL-dan-Putrajaya/JADUAL_WAKTU_SOLAT_2026_WP_KL_PUTRAJAYA.pdf
- Egyptian General Authority for Survey: https://www.esa.gov.eg/praytimes.aspx
- Egyptian Dar al-Ifta: https://www.dar-alifta.org/ar/prayer
- Oman Ministry Muscat, Nov 2026 verified 30 days: https://www.mara.gov.om/calendar_page2.asp
- Singapore MUIS official 2026, 365 days: https://data.gov.sg/datasets/d_d441e7242e78efc566024dd5b0d9829c/view

## Verified cause for the major Malaysia Fajr discrepancy
The engine configures **Jakim** as Fajr solar depression **20°**. Malaysian federal and state religious authorities decided in 2019/2020 to use **18°** for the start of Subuh; a change resulting in approximately 8 minutes later dawn. Confirmed from actual government sources:
- Federal Territory Mufti: https://muftiwp.gov.my/en/artikel/bayan-linnas/3858-bayan-linnas-khas-isu-tambahan-waktu-8-minit-bagi-permulaan-azan-subuh-dan-hukum-solat-subuh-sebelum-masuk-waktu
- Selangor Mufti: https://www.muftiselangor.gov.my/2023/10/27/pandangan-hukum-syarak-penilaian-semula-nilai-altitud-matahari-di-bawah-ufuk-bagi-penentuan-awal-waktu-solat-subuh-di-negeri-selangor/

IMPORTANT: Malaysia also uses **prayer zones**, not arbitrary city-center GPS reference points; the national/zone calculation criteria require zone-specific reference coordinates (Federal Territory Mufti FAQ). Correcting the Fajr angle alone does not prove the full six local official clocks. Before an Android release, model Malaysian zones, ensure correct official 2026 and future-year tables, and verify independent daily/seasonal cases. Do not apply an arbitrary blanket offset; that may break other regions.

## Current coverage, limits and release decision
- Exact official source fixture coverage in existing PR: Muscat Nov 2026 (30 civil days) and Singapore 2026 (365).
- Previously tested 250 country/territory directory entries (246 with city records), 2,976 astronomical calendar/date-zone cases: **calculational safety tests, not independent official country prayer-time certification**.
- Additional independent authorities: İstanbul, Kuala Lumpur, Cairo 2026-11-07 each contain at least one nonzero minute deviation; output and exact minute deltas preserved in Actions artifact.
- Remaining cities/dates and authorities not verified. High-latitude Islamic conventions and future DST law changes require explicit regional policies.
- No newly signed matching original-key APK/AAB or physical HONOR acceptance proof for the changed source. Other GitHub release checks have failed on source/dist fingerprint consistency. **NO PUBLISH, NO MERGE, NO DEPLOY.**

## Reproducibility
Run `node tests/independent-world-authority-audit.cjs` on this PR. It deliberately fails closed when independent authority clocks disagree, emits `reports/world-authority/independent-reference-2026-11-07.json`, and the no-deploy workflow uploads that file even after failure.

Partial fixes in a single city do **not** satisfy the user’s conditional requirement for worldwide correctness. Never describe 12-hour display, astronomical plausibility, or a 250-country list as a worldwide official timetable certificate.

## Resolution of reproduced cases — subsequent review commits (NO PUBLISH)

The original November 7 benchmark showed correct source-vs-app minute differences in Cairo, Istanbul and Kuala Lumpur. These rows remain above as the before-state historical evidence, **not current candidate output**.

The candidate review branch now includes:
- `official-cairo.js`: 30 official November 2026 Cairo rows from Egyptian Dar al-Ifta/Egyptian Survey, confined to the Cairo reference centre and Cairo civil timezone.
- `official-istanbul.js`: 30 official November 2026 Istanbul rows from Diyanet, confined to the Istanbul reference centre and Turkey timezone.
- `official-malaysia-wly01.js`: 30 official November 2026 Kuala Lumpur/Putrajaya WLY01 rows from Federal Territory Mufti/JAKIM, with conservatively bounded eligibility; no false claim for Malaysian zones elsewhere.
- Corrected JAKIM fallback Fajr depression from obsolete 20° to officially accepted 18°, without blanket minute offsets.
- Previously verified Muscat November (30 days) and Singapore calendar-year 2026 (365 days).
- Source selection retains raw GPS positions and never treats a snapped nearest city as proof of official calendar eligibility.
- Regression tests cover **485 official city/date rows** (30+30+30+30+365), 12-hour display, mobile adhan timestamps, manually selected methods, Hanafi Asr isolation, timezone, daylight saving and no unauthorized sunrise adhan.
- `tests/independent-world-authority-audit.cjs` compares the formerly failing exact Nov 7 Turkey/Malaysia/Egypt government fixtures against the source engine; it was included in successful dedicated workflow run 42336204017.
- Actual Playwright Chromium screenshots from same reviewed source show ten cases (five cities × Arabic/English) and pass exact six-time DOM comparisons; captured run 42336204017, artifact 13559845356.

**STILL BLOCKED:** A one-month authority calendar for five cities does NOT certify 171,114 city entries or future years. GPS precision, city prayer-zone memberships, changes in official authorities and calculation methods, and high latitude allowances require per-area verification. No newly original-key-signed matching Android APK/AAB has been produced, physical Android test is absent, and existing protected source-versus-APK fingerprint checks reject this unpublished code. This work is preview-only: **do not merge or publish official production**.
