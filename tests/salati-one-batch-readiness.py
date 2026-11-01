#!/usr/bin/env python3
"""One-batch release gate: stylesheet debt, native wiring and original user UI.

No declaration of zero defects: native Android and original signing are separate
checkpoints. This test guards against silently re-introduced cascade layers.
"""
from pathlib import Path
from collections import Counter
import re,json
import tinycss2
root=Path(__file__).resolve().parents[1]
dist=root/'dist'
html=(dist/'index.html').read_text()
css=(dist/'salati-ui.css').read_text()
report=json.loads((root/'reports/css-one-batch-20261102.json').read_text())
links=re.findall(r'<link\s+rel="stylesheet"\s+href="([^"]+)"',html)
assert links==['salati-ui.css','/city-pages.css'],links
assert report['redundant_declarations_removed']>0, report
assert report['optimized_important']<=report['baseline_important'], report
assert css.count('!important')<=1991
assert 'height:var(--salati-quran-window-height,auto)' in css
assert 'id="mushafPlayerSlot"' in html and html.index('id="qSheet"')<html.index('id="mushafPlayerSlot"')
assert 'nav-icon-button.active' in css
assert 'grid-template-columns:repeat(6,minmax(0,1fr))' in css
assert 'active-reference-nav-20261101.css' not in html
assert not any(root.glob('dist/style-v1.0.10?.css'))
assert "'./salati-ui.css'" in (dist/'sw.js').read_text()
info=(root/'android/app/src/main/res/xml/prayer_widget_info.xml').read_text()
widget=(root/'android/app/src/main/res/layout/prayer_widget.xml').read_text()
assert 'targetCellWidth="5"' in info
assert 'resizeMode="horizontal|vertical"' in info
assert 'android:paddingLeft="6dp"' in widget
assert 'android:paddingRight="6dp"' in widget
assert (root/'tests/worldwide-prayer-integrity-20261101.cjs').is_file()
print('PASS one-batch source readiness:',report['redundant_declarations_removed'],
  'cascade overrides safely discarded; remaining priority flags',report['optimized_important'])
