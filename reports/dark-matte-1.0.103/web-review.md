# Closure review — permanent charcoal correction

Read-only recheck of the two findings in `/workspace/salati-fix/205/web-review.md`, pending1.0.103. No application edits, audio edits or publication. No remaining P2 found in this targeted closure review.

## Closed: photo integration

`dist/reference-layout.css:119` now intersects horizontal10% edge feathering with vertical8% top/3% bottom feathering. Inspected regenerated390px and1366px screenshots: hard photo side/top boundaries are softened into the surrounding card, while the mosque's gold illumination, domes/minarets and centre pixels remain visible. The photo's layout box, source, filter:none and opacity:1 remain unchanged; city/dates stay left, upcoming stack stays right, prayer strip stays below. The previous separate-rectangle finding is closed for these rendered Chromium outputs.

`python3 tests/reference-image.py` passes exact original crop pixel identity, native/web byte identity and offline cache binding. No image file manipulation was introduced to achieve this integration.

## Closed: footer action borders

The final `body.dark button` rule now defines a complete1px solid border instead of only border-color, overriding the old footer border:0 rule. Rendered footer actions have the required quiet edge, charcoal fill and white text. Reset/adjust-reset actions have explicit charcoal/white/border treatment. The prior missing-footer-border finding is closed.

## Verification

Passed again: `python3 tests/dark-matte.py` (seven requested widths, permanent dark, matching city/date type, right-side live stack,6tabs/menus, preserved settings, malformed/blocked storage and dark first-paint fallback), and `python3 tests/reference-image.py`.

Additional external measured probe `/workspace/salati-fix/205/layout-state-probe.py` checks English across all seven widths and footer clearance above bottom navigation across six tabs with simulated24px safe inset. Its Quran lazy sentinel is removed only in the external test page to make final-footer geometry stable; no repository change occurs. No navigation repositioning or new layout regression was found from these edge-mask/border fixes.

This is targeted web closure evidence, not physical Android/WebView/widget certification or a license review. The new licensed approach-reminder recording is still unresolved. Overall completion/publication remains blocked by that audio requirement, regardless of the closed web findings.
