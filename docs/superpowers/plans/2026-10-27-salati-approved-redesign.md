# Salati approved redesign implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Apply the first design selected by the user to the existing six-section Salati website and Android app.
**Architecture:** Retain all application controllers and persistence. Use an explicit final design stylesheet, accessible existing DOM controls, bundled icons and one generated mosque asset. Remove the globally injected city directory at its build source.
**Tech Stack:** Existing HTML/CSS/ESBuild JavaScript and Android native wrapper.
**Spec:** Selected visual /workspace/generated_images/exec-1a480d70-eb10-430d-9bdf-812f5348e739.png, user-selected via 98190.jpg. User subsequently requested mosque imagery on phones too.

## Global constraints
- Six tabs, one Quran control panel, 6236 unchanged Quran verses/font and continuous/background audio.
- Pure white/black light theme, white-on-black dark theme, Cairo bold UI, blue navigation and gold prayer focus.
- Original fixed signing certificate; never publish private key/password.
- No city-directory panel on any app screen or build reinjection. Standalone city pages remain addressable.

## Review focus
- Phone widths 320/390/760: bottom navigation and Quran follow bar do not overlap controls.
- Arabic/English labels: stable six-tab navigation and shared state.
- Changing prayer/date/location: real current values, no example times embedded.
- Dark theme: readable icons and text across all sections.
- Build regeneration: city links stay absent and all referenced assets are bundled.

## Tasks
- [x] Remove global city panel at HTML/build source; update city-page internal-link verification.
- [x] Apply approved responsive layout, shared component styling, mosque imagery and distinct navigation icons; include mosque photo on phone per user steering.
- [ ] Run application/SEO/build verification and inspect actual browser views if browser tooling is available.
- [ ] Package signed update and source ZIP, verify identity/assets/secrets/hosting limits.
- [ ] Publish only after resolving required visual QA gate; document any infrastructure blocker truthfully.

Automated application and SEO checks passed; signed APK 1.0.87 prepared and byte-exact assets verified. Required visual QA remains blocked, so the user subsequently authorized full publication without browser QA on 2026-10-27.
