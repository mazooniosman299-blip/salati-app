Read-only review of the current uncommitted 1.0.107 patch against 451f8f784e19448313a6d309d2ce3dc97a2c7f76. No source edits or builds performed. Chromium probes used the current versioned assets with service workers blocked.

Important findings

1. P2 — Navigation/selection shortcuts inherit the blue action material. `dist/reference-layout.css:144` does not exclude `[data-adhkar-category]` or `.location-back`. The four Dhikr category controls render #2563EB even though they select which content is displayed; selecting Evening changes aria-pressed but all four retain the blue fill/frame. In Settings → Location → select Oman, the “All countries” back control also renders #2563EB. Its transparent navigation override at `dist/reference-layout.css:235` loses to the more specific general selector. Exclude these controls from normal/hover/pressed action styling and verify their charcoal navigation material. Coordinator has accepted the category finding and is addressing it.

2. P2 — Active navigation loses the keyboard focus frame. The new active material selector at `dist/reference-layout.css:259` has equal specificity to the explicit focus rule at `dist/reference-layout.css:249` and occurs later. With keyboard focus on inactive Mushaf its frame is rgba(255,255,255,.65); pressing Enter keeps :focus-visible true but resets the frame to .14 with outline:none and the same inset sheen as an unfocused tab. The already active Times tab has the same issue. Retain the existing .65 focus frame after the reference material rules; this needs no outer halo or material redesign.

Other reviewed scope

The separate action tokens do not recolor the control/media tokens. Quran selector fields and main navigation stay charcoal; qTransport stays a dark disc with a 44px interactive box. Tasbih exposes a count command and reset command, with no separate mode selector in its DOM. Quran text size, bookmark, stop, and preview commands correctly fall into the action scope. Existing footer gap/date placement/search/menus rules were not changed in the reviewed diff. Android widget source is unchanged; no physical-phone validation claim is made.

Closure re-review

Both important findings are resolved in the current source. `dist/reference-layout.css:144`, `:151`, and `:152` now exclude `[data-adhkar-category]` and `.location-back` from normal, hover, and pressed action colors. The final focus-visible rule at `dist/reference-layout.css:267` comes after the active navigation material and restores the existing rgba(255,255,255,.65) frame with no outer outline. The versioned reference-layout-v1.0.107.css is byte-identical to reference-layout.css.

Reviewed the added rendered assertions: action-scope checks category fills and the visible country-back control; glass-material-scope checks the active navigation focus frame at all four viewport widths. Current `/workspace/salati-fix/212/actions.log` and `glass.log` both report PASS. No remaining important findings in the requested action/glass scope. No rebuild or source edits performed during closure review.
