# Salati dark matte correction

Authoritative spec: user Pasted text.txt (2026-10-29). User explicitly authorized implementation without repeated questions, specified the visual and execution approach, and forbids publishing a nonconforming release.

Preserve existing structure/functionality, original mosque image pixels, left city/dates, right next prayer, lower six-time strip, six-tab bottom navigation and Mushaf-only player. No new assets/design alternatives.

1. Keep rollback tag salati-1.0.102-stable. Pin single dark palette #0B0E13/#040509/#15181D/#32383F with white main text and #AEBCCB secondary. Remove theme switch/system preference branches and normalize legacy saved light preference without dropping other settings. Cover loading shell, public pages, CSS/SVG and Android resources.
2. Match both date text styles to city (white, size/weight/family) at each existing breakpoint, allow wrapping without clipping. Remove countdown caption and next-prayer decorative icon so right column has title, live prayer name and white countdown only. Preserve grid areas/photo pixels and time-engine logic. Mirror native widget dates and compact layout safely.
3. Apply charcoal tokens to all controls/disabled/active/hover/focus/dialog states, tasbih/qibla and native controls, retaining hit targets and bottom safe-area padding. Keep disabled controls visible.
4. Add failing dark-only/rendered-layout acceptance test, then implement and verify at 360/390/412/768/1024/1366/1920 pixels, RTL/LTR, menus, corrupted/blocked storage and legacy light preference. Update superseded dual-theme fixtures; retain playback, Quran text, prayer/location/notification regressions.
5. Research real-human replacement audio with explicit redistribution rights. Only integrate documented, licensed recordings; keep Quran/adhan untouched. Add attribution/license and validate words, single playback owner, Fajr-only routing, volume/options, preview and offline assets. If suitable licensed approach recording cannot be obtained, record blocker and DO NOT publish incomplete release.
6. Build Android with original certificate and increased versionCode. Verify native resource pixels and packaged assets. Record unavailable physical-device/lock-screen verification honestly. Pass independent review and all relevant automated/browser checks before GitHub/Sites publication; verify deployment and APK link through available capability. Stop publication on unmet mandatory acceptance.

Review focus: persisted dark=false; blocked/corrupt localStorage; long bilingual dates in narrow widget; native compact date clipping; paused Quran metadata and error-state persistence. Device screen-lock behavior requires a real device and is never inferred from a build/harness pass.
