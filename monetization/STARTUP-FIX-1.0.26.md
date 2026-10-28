# Salati 1.0.24 startup investigation

Confirmed code defect: AdsController.update called MobileAds.setAppMuted(true) and setAppVolume(0f) before MobileAds.initialize. Decompiled actual cached play-services-ads-api 25.5.0 with JDK javap. MobileAds.setAppMuted delegates to zzeu.zzh, whose null initialization-manager check throws IllegalStateException: "MobileAds.initialize() must be called prior to setting app muted state." zzeu.zzf has the equivalent precondition for volume. Exception is not caught by the app. The UI can hit this after consent permits ads.

Patch: move both calls into the initialization-completion callback, on UI thread, before banner creation. Keep released recovery build 1.0.25 SDK-free; do not re-enable it merely for this investigation.

APK 1.0.24 manifest independently verified: valid publisher application ID and MobileAdsInitProvider are present; signature matches recovery certificate. minSdk26 exceeds SDK25.5.0 min24. No change to prayer/audio Java implementation between 1.0.24 and recovery.

Limitation: no device crash stack trace, so the exact exception on the user's device is not confirmed. UMP or other device-dependent failures remain possible. No live ads requested during investigation.


1.0.26: AdInitialization enforces worker->initialization callback->UI configuration->banner ordering. Lifecycle guards catch RuntimeException/LinkageError in app SDK calls and callbacks; errors hide and disable ads for the session, record a local-only stack trace, and leave core app functional. An initialization deadline disables stalled ads. This cannot protect against all internal SDK process/native faults or replace physical-device testing.

Validation: production Gradle assembleRelease including release lint; pure Java lifecycle/ordering/failure regression tests and144 ad visibility cases; main prayer/Quran/location/schedule suite; notification focus and silent alarm policy suites; release signature, package/version and actual APK contents. No live ad requests or device test performed.
