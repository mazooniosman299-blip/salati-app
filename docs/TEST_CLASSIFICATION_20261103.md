# Production vs preview test ownership — 2026-11-03

`tests/production-test-matrix.json` is a machine-readable inventory. The existing `salati-permanent-regression-protection.yml` production gate remains unchanged by this governance request: functional, security, exact release fingerprint, browser and native build tests still run. No test was disabled just to remove an inconvenient red result.

**Actually stale preview-specific contracts:** `preview-four-ui-changes-browser.py` requires `preview-four-ui-changes-20261101.css` linked, but `production` only links `salati-ui.css`. `preview-reader-below-ui-20261101.py` captures an earlier reader variant. Neither should become a current mandatory production design reference without user reapproval.

**Review before changing any active assertion:** `four-ui-screenshot-regressions-20261101.py`, `mushaf-legibility-20261101.py`, `user-visual-audit-20261101.py` and `selection-refinement-20261101.py` are real browser scripts; some expectations may conflict with a newer screenshot. Preserve their functional/security checks and independently review each visual assertion before replacing any outdated value.

The new `current-design-visual-proof.py` captures 48 genuine screenshots of all six original tabs in Arabic and English on 320/390/768/1280px, records computed DOM properties, tests navigation/layout/scroll/language persistence, and explicitly does **not** claim parity with an original image we cannot verify. The original image must first be saved and approved in the reference registry. No user-visible UI change is requested in this branch.
