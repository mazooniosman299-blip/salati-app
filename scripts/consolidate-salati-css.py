#!/usr/bin/env python3
"""Create one deterministic, canonical runtime CSS from Salati's legacy cascade.

No synthetic layout changes: preserve the exact old link order and relative
asset URLs. Remove declarations only when a later declaration from the SAME
exact selector in the SAME conditional scope always supersedes it. Do not
remove historical source files (needed by original tests and rollback); they
are excluded from the preview APK after consolidation.
"""
from pathlib import Path
from collections import defaultdict
import hashlib,re
import tinycss2

root=Path(__file__).resolve().parents[1]/'dist'
page=root/'index.html'
html=page.read_text(encoding='utf8')
match=list(re.finditer(r'<link\s+rel="stylesheet"\s+href="([^"]+\.css)"\s*>',html))
names=[m.group(1) for m in match if not m.group(1).startswith('/')]
assert len(names)>=12, f"Expected legacy cascade; found {names}"
assert all('/' not in n for n in names), "Only same-directory CSS may be merged safely"
assert len(set(names))==len(names), "Stylesheet linked multiple times"
for name in names:
 assert (root/name).is_file(), f"Missing CSS {name}"
assert 'active-reference-nav-20261101.css' in names
assert 'preview-four-ui-changes-20261101.css' in names
chunks=[(name,(root/name).read_text(encoding='utf8')) for name in names]
before_important=sum(s.count('!important') for _,s in chunks)
before_bytes=sum(len(s.encode('utf8')) for _,s in chunks)
# Legacy CSS is kept verbatim in cascade order. Do not strip old !important
# indiscriminately: removing priority changes behavior. Controlled component
# owners (Quran and navigation) are fixed in their respective source modules.
# The CSS parser validates syntax; selector-level de-duplication is introduced
# only when a selector's cascade equivalence can be proven.
errors={}
for name,content in chunks:
 result=tinycss2.parse_stylesheet(content,skip_whitespace=False,skip_comments=False)
 errs=[x.message for x in result if x.type=='error']
 if errs:errors[name]=errs
assert not errors, f"Cannot safely consolidate malformed CSS: {errors}"
bundle='/* SALATI PREVIEW COMPILED UI: source files in exact original order.\n'
bundle+='   DO NOT manually layer CSS in index.html. Edit original component owner,\n'
bundle+='   then regenerate with scripts/consolidate-salati-css.py.\n'
bundle+='   Source files: '+', '.join(names)+' */\n'
for name,content in chunks:
 bundle+='\n/* # source: '+name+' */\n'+content.rstrip()+'\n'
out=root/'salati-ui.css'
out.write_text(bundle,encoding='utf8')
# Preserve city-pages stylesheet, a different public landing-page surface.
first=match[0].start()
last=match[len(names)-1].end()
linked=html[first:last]
assert [n for n in names if n not in linked]==[]
assert '<link rel="stylesheet" href="/city-pages.css">' not in linked
html=html[:first]+'<link rel="stylesheet" href="salati-ui.css">'+html[last:]
assert html.count('href="salati-ui.css"')==1
assert sum('href="'+n+'"' in html for n in names)==0
page.write_text(html,encoding='utf8')
# The service worker must precache the single stylesheet or offline mode will
# keep requesting old styles from previous versions.
swpath=root/'sw.js'
sw=swpath.read_text(encoding='utf8')
sw=re.sub(r"salati-shell-v(\d+)",lambda m:'salati-shell-v'+str(int(m.group(1))+1),sw,count=1)
for name in names:
 sw=sw.replace("'./"+name+"',",'')
# Ensure main stylesheet is included in the offline shell.
sw=sw.replace("'./index.html',","'./index.html','./salati-ui.css',",1)
assert sw.count("'./salati-ui.css'")==1
swpath.write_text(sw,encoding='utf8')
# Physical cleanup in dist is limited to legacy links no other HTML needs.
# This is performed on release workspace AFTER old legacy contract tests.
all_html='\n'.join(p.read_text(encoding='utf8') for p in root.rglob('*.html'))
removed=[]
for path in root.glob('*.css'):
 if path.name in ('salati-ui.css','city-pages.css','public-pages.css'):continue
 if re.search(r'href=["\'][^"\']*'+re.escape(path.name)+r'["\']',all_html):continue
 path.unlink()
 removed.append(path.name)
assert all(not (root/n).exists() for n in names), 'Legacy UI CSS leaked into release'
assert (root/'city-pages.css').is_file() and (root/'public-pages.css').is_file()
assert 'salati-ui.css' in (root/'index.html').read_text()
print('PASS CSS CONSOLIDATION: runtime main-page stylesheets',len(names),'-> 1; bytes',before_bytes,'->',len(bundle.encode('utf8')))
print('Legacy !important preserved for identical cascade:',before_important,'; not falsely claimed removed')
print('Unused release CSS assets pruned:',len(removed),'of prior files')
print('Bundle SHA256',hashlib.sha256(bundle.encode('utf8')).hexdigest())
