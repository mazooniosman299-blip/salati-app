#!/usr/bin/env python3
"""Permanent CSS architecture gate for Salati's canonical dark-only UI.
This is a source-level check; functional device tests are separate.
"""
from pathlib import Path
import re,json
import tinycss2
root=Path(__file__).resolve().parents[1]/'dist'
html=(root/'index.html').read_text()
css=(root/'salati-ui.css').read_text()
sw=(root/'sw.js').read_text()
links=re.findall(r'<link\s+rel="stylesheet"\s+href="([^"]+\.css)"\s*>',html)
assert links==['salati-ui.css'],('Canonical app must not import city-only CSS',links)
assert "'./salati-ui.css'" in sw,'Offline shell must cache canonical CSS'
assert not any(f'-v1.0.{n}.css' in html for n in range(100,120)), 'Versioned UI style leaked into main HTML'
assert 'light-theme.css' not in html,'Dark-only app must not import a light-mode layer'
assert not list(root.glob('style-v1.0.10[0-8].css')),'Retired version families must not be recreated'
ast=tinycss2.parse_stylesheet(css,skip_whitespace=True,skip_comments=True)
errors=[x.message for x in ast if x.type=='error']
assert not errors,errors
priority=len(re.findall(r'!\s*important\b',css,re.I))
assert priority==0,('Canonical CSS must contain zero priority flags',priority)
assert len(css.encode())<=222900,('CSS unreviewed expansion',len(css.encode()))
for key in ['#mushafPlayerSlot','--salati-quran-window-height','nav-icon-button.active','#prayers','.recitation-timeline','background:#242424']:
 assert key in css,('Approved component missing',key)
assert not any(s in html for s in ['href="active-reference-nav-20261101.css"','href="preview-four-ui-changes-20261101.css"','href="design-restoration-v1.0.113.css"'])
assert 'preview-sample-location' not in html, 'Production preview location script must not be imported'
assert not (root/'preview-sample-location-20261101.js').exists(), 'Production must not ship preview-only location code'
print('PASS CSS ARCHITECTURE: one active app stylesheet, zero forced CSS priorities, no preview location code')
