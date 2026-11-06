# Official publication request — authentic surah headings + printed page book
Date: 2026-11-06. Source: production@a35d26031a3cec39c633412a76efb258db4d6470.

Verbatim release authorization: «ممتاز جدا يلا انشر التحديثات دي رسمي».
Current continuation: «كمل كل شي عندك المشكله الواجهتك بسيطه حلها وكمل  للاخر».

The user explicitly approved official publication of the actual Salati Quran modifications: authentic photo-derived brown frame at all 114 surah openings and the photographed open-book ornament around the bottom folio on all 604 original plates, with Eastern Arabic digits and optically centered visible ink.

Approved screenshot pages 1, 50, 564, 604. The page-one photograph has its own original centered ١. Other pages use the identical book photograph with only the page-one numeral repaired under new dynamic numbers.

No change to the 604 Quran original image hashes, original text, 6236 ayah regions, recitation audio, player, or unrelated app content.

Official project: salati-app (salati-app-ctc.pages.dev); production branch: production.

RELEASE GATES (NEVER BYPASS):
- Use a new original-key signed Android release: package com.salati.prayer, SHA256 signer certificate 559dec66ab13e86be17c661732f1d2b1751a63261ed7d7d353b857f693cf056e. Monotonic version code.
- Signed APK embedded web content and published website must match, with cryptographic manifest/fingerprint proof; current signed 1.0.132 is for previous code and cannot be silently reused.
- Exact-head all mandatory GitHub CI/browser/native/negative publish tests green, origin production branch protection, and successful Cloudflare production deploy.
- Never bypass signing/CI controls, falsely report a physical-device test, or publish an incomplete release.

Known blockers: prior November 5 scope manifest and obsolete tests still assert old cartouche/CSS-only cleanup, while current site fingerprint differs from 1.0.132 signed release. Resolve tests and obtain original signed matching APK before merging and deploying.

STATUS: Authorized by user, source visually verified, publication still pending matching original-key signed artifact and all required checks.
