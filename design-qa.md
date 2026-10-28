# Salati design QA

Source visual truth: /workspace/generated_images/exec-1a480d70-eb10-430d-9bdf-812f5348e739.png
Selected by user via 98190.jpg. Additional request: show the mosque photo on mobile too.

Browser-rendered implementation screenshot: unavailable.
Viewport targets: desktop 1440×1024, phone 390×844 and 320px narrow viewport, RTL/LTR, light/dark.
Density normalization: not performed; no implementation capture.
Primary interactions and console errors: browser verification blocked; automated checks tracked separately.

**Findings**
- [P1] Visual comparison requires a supported browser. Browser skill read; no Browser js/CUA browser tools or local preview helpers are exposed in this environment. No screenshot comparison or fidelity pass is claimed.

**Implementation Checklist**
- Finish responsive code and automated functional checks.
- Capture both viewports and all six tabs with a supported browser, compare against selected visual in the same comparison input.
- Check fonts, spacing, colors, assets and copy; fix visible issues before a visual QA pass.

final result: blocked

## Publication authorization
The user explicitly requested full publication on 2026-10-27 after the unavailable browser QA was explained. Publication is authorized using completed automated checks and signed-APK verification. This does not turn missing visual evidence into a passed visual comparison; final result remains blocked.

## Responsive correction 1.0.88
User supplied actual light/dark phone screenshots identifying pale hero labels, location whitespace, inconsistent icon sizes and cropped imagery. Reproduced failures by evaluating the real stylesheet cascade against the DOM: legacy light hero #ecf3ef won by specificity; location children inherited flex:1 1 180px in a column; legacy nav SVG 1.2em beat the new generic selector; negative desktop nav margin caused header overlap. Regressions now exercise light/dark at seven width targets plus six actual navigation callbacks in both directions. Removed source conflicts and replaced overlay layout with real header grid; equal 28px icon slots, natural image ratio, countdown DOM ordering and settings label corrected. Automated results are separate from browser rendering. The user's earlier authorization to publish without browser QA remains applicable; no new visual pass is claimed.

## Spacing/navigation correction 1.0.90
User screenshots identified uncapped mobile nav space and desktop tasbih alignment. The design card margin shorthand reset the base centered/adhkar auto margins; the tasbih-card design selector did not exist in HTML. Tests failed against the real DOM/cascade before correcting those selectors. Mobile nav now has an explicit 56px track with a 65px base container and safe-area accounting. MainActivity already pads native content with system insets; native CSS does not add it a second time. Navigation handler tests reproduce and fix cross-tab scroll loss. All automated checks are separate from browser rendering; prior publication authorization applies, and final visual result remains blocked.

## Scoped selection: original first-set image 2, Tasbih/navigation only
The user approved the Tasbih panel and navigation icons from `/workspace/generated_images/exec-3e6f5384-2796-4ebf-8ac1-75902afc59ee.png`, rejected the other components and all later alternatives, then explicitly requested implementation of the chosen parts only. Reference copied into `docs/design/selected-tasbih-navigation.png`. Navigation uses a licensed, bundled consistent Hugeicons stroke set, local blue active state and a compact underline. Tasbih has the large count/progress/thumb pad/reset hierarchy, dark navy surface only in dark mode, white light surface, and unchanged 100-count sequence/persistence. The explanatory method remains in expandable text, with the full final declaration shown at 99/100. All non-Tasbih section markup, launcher assets and native widget source/resources were compared byte-for-byte against the previous release. No supported browser renderer is available; no rendered comparison or visual pass is claimed. Existing user authorization to publish without browser QA remains applicable. Final result remains blocked for visual QA only.

## User correction 1.0.93
User rejected the oversized Tasbih pad. It is now 128×128px with 28px corners, 24px label and a restrained shadow; the 10/20px glow rings were removed and adjacent spacing tightened. Cascade checks verify the intended dimensions in both themes at phone/desktop widths. This is not browser rendering evidence; visual QA remains blocked and prior publication authorization applies.
