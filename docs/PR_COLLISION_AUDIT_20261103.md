# Open PR collision review — 2026-11-03

Inspected current open PRs with actual GitHub changed filename lists. **Both #35 and #36 modify live `dist/index.html` and `dist/salati-ui.css`**. They contain distinct Quran reader/player implementations; they are both draft, unmerged, and start from production SHA `f47ca69`.

| Pull request | Purpose | Shared live files | Decision |
|---|---|---|---|
| [#35](https://github.com/mazooniosman299-blip/salati-app/pull/35) | Full printed page / green-preview variant, alternative player arrangements | `dist/index.html`, `dist/salati-ui.css` | HOLD: requires precise latest user screenshot, source rights, and reconciled implementation |
| [#36](https://github.com/mazooniosman299-blip/salati-app/pull/36) | Real Quran playback controls / immersive app UI | `dist/index.html`, `dist/salati-ui.css` | HOLD: incompatible variants must not overwrite each other; original signing proof needed |
| [#37](https://github.com/mazooniosman299-blip/salati-app/pull/37) | AI instruction governance, source mapping, visual evidence and tests | Neither live runtime file | Safe to review independently; NOT an approval for #35/#36 |

A new **live GitHub PR collision guard** checks current PR changed files against every other open PR targeting production and blocks shared executable paths. It does not automatically merge any project work or label conflicting mockups as user-approved. The actual newest user-approved placement for the Quran player must be reconciled with authentic reference before implementing either candidate.

No runtime files or existing production releases were changed in #37.
