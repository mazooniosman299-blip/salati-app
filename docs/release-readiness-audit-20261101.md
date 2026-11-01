# Salati release-readiness audit — 2026-11-01

**Published version at audit start:** 1.0.116 / Android versionCode 117.
Public APK SHA-256: `58d14923b15ec3a6933af573cc720081780af7578808fd2d9d7f68f087edc6a5`.
Cloudflare production deployment SHA: `de6dd03d4d734a86060760cffa2a702655d5b3b1`, status **success**.

**This branch is NOT the published app.** No version number or public APK is advanced here. Build a new signed APK with incremented versionCode, matching web fingerprint, and do a guarded atomic release before shipping any changes.

## Verified code/state and staged fixes

| Item | Truth from production | Changes in this branch | Release gate |
|---|---|---|---|
| Location pins at 360px | A prior test failed on exact SVG size/position but incorrectly reported no offenders | High-specificity pin normalization and exact diagnostics | Chromium all 251 entries + desktop/mobile |
| Official APK | v1.0.116 asset exists; original certificate and SHA verified by release pipeline | No APK change yet | Next APK signed using original certificate |
| Cloudflare | Production succeeded; unrelated previews failed stale-APK guard | Build CSP is staged | Atomic release only |
| Late adhan | Exact and inexact wakeups both rejected after 5m | Exact still 5m, inexact 15m, prevent playing after newer prayer | Device lock/Doze and delayed alarm logs |
| In-place upgrades | Not tested on a real Android handset | Upgrade tests run in browser | Same-signature APK upgrade over v1.0.116 with app data intact |
| Locked/reboot/battery restrictions | No physical verification; force-stop cannot be bypassed | No unsupported promises | Test multiple phones and report OEM restrictions |
| Human Fajr clip | No documented redistribution permission | Remove unlicensed MP3; use browser and Android native TTS | Rights proof before restoring a human recording |
| Cached MP3 integrity | Size and magic-byte heuristic only | SHA-256, expected size, Android decoder metadata checks | Corruption/recovery JDK and actual device |
| GitHub branch protection | production protected=false | **Unavailable through connector (GitHub admin API 403)** | Admin: Settings → Branches/Rulesets; require PR, status checks, block force-push and deletion; ideally require signed-release gate |
| Stale installation docs | References 1.0.79/1.0.109/1.0.112 | Published v1.0.116 URL/version and SHA documented | Recheck next version artifacts |
| CSP | No explicit generated CSP | CSP plus restrictive headers with inline-script SHA-256 hashes | Test HTTP headers, console logs, forms, audio and third-party pages on preview |
| Color contrast | Static CSS test only | Runtime AA ratio checks across device sizes | Review all actual failures and screenshots |
| AdMob + UMP | SDK, test/prod config and consent guard exist | Run native helper tests | Publisher account fill, consent privacy options, regional EEA/US scenarios on actual Android |
| Crash reporting | No Crashlytics SDK/config | Do not silently connect an external analytics provider | Connect an authorized Firebase project, configure crash reporting/privacy notice, verify test crash and consent policy |

## Required physical Android acceptance before publishing another release

Install existing v1.0.116 on at least one Android 13–16 device, enable alarms, manual offsets, location, saved Quran audio, then update directly to the new APK without uninstalling. Verify all saved settings and offline recordings persist. Test adhan exact permission granted/denied/revoked, screen locked for >=30 minutes, Doze, battery optimized/unrestricted, reboot and timezone change, and compare actual audio start times to scheduled time. Record logs of any skipped alarm; force-stop is an OS limitation, not an app bug that can be bypassed. Repeat on the user's device if available; browser-only tests don't certify this.

For ads, test UMP consent (including "manage options"), explicitly reject/accept, under test-ad IDs before production; a production-ID build alone cannot certify approval, impressions, payout, or privacy compliance.

For Crashlytics, ask for a Firebase project and ensure consent and privacy disclosures before collecting crashes. Native Logcat and locally stored delivery status already exist but are NOT a substitute for backend crash reporting.

## Never-ship-unverified rule

A passing Java compile or Chromium screenshot is not real-device validation, content ownership evidence, Google AdMob approval, GitHub administrative branch protection, or Crashlytics integration. Never report those gates completed without the appropriate evidence.
