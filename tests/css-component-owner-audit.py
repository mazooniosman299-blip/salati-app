#!/usr/bin/env python3
"""Inventory of unresolved canonical CSS cascade conflicts.
Require future changes to stay below the audited budget, never mask debt
by adding another linked stylesheet or a new !important override.
"""
from collections import defaultdict
from pathlib import Path
import json, re, tinycss2

root=Path(__file__).resolve().parents[1]
css=(root/'dist/salati-ui.css').read_text()
html=(root/'dist/index.html').read_text()
by=defaultdict(list)
metrics={'rule_count':0,'declarations':0}
def clean(tokens):return tinycss2.serialize(tokens).strip()
def walk(nodes,scope=()):
 for n in nodes:
  if n.type=='qualified-rule':
   selector=clean(n.prelude)
   decl=tinycss2.parse_declaration_list(n.content,skip_whitespace=True,skip_comments=True)
   metrics['rule_count']+=1
   for d in decl:
    if d.type!='declaration':continue
    metrics['declarations']+=1
    if d.name.startswith('--'):continue
    by[(scope,selector,d.lower_name)].append((clean(d.value),bool(d.important)))
  elif n.type=='at-rule' and n.content is not None and n.at_keyword.lower() in ('media','supports','container'):
   walk(tinycss2.parse_rule_list(n.content,skip_whitespace=True,skip_comments=True),scope+((n.at_keyword.lower(),clean(n.prelude)),))
walk(tinycss2.parse_stylesheet(css,skip_whitespace=True,skip_comments=True))
duplicates={k:v for k,v in by.items() if len(v)>1}
conflicts={k:v for k,v in duplicates.items() if len(set(v))>1}
important=len(re.findall(r'!\s*important\b',css,re.I))
stats={**metrics,'important':important,'duplicate_selector_property_groups':len(duplicates),
 'conflicting_selector_property_groups':len(conflicts),'duplicate_declarations':sum(len(v)-1 for v in duplicates.values()),
 'css_bytes':len(css.encode())}
assert html.count('href="salati-ui.css"')==1
assert stats['conflicting_selector_property_groups']<=103, ('CSS conflicting selector-property groups regressed',stats)
assert stats['duplicate_selector_property_groups']<=107, ('CSS duplicate selector-property groups regressed',stats)
assert stats['duplicate_declarations']<=134, ('CSS repeated declarations regressed',stats)
assert important<=1959,('CSS priority debt increased beyond 1959',stats)
assert stats['css_bytes']<=222900,('Old CSS overlays reintroduced',stats)
report=root/'reports/css-source-maintainability.json'
report.parent.mkdir(exist_ok=True)
report.write_text(json.dumps(stats,indent=2))
print('PASS CSS SOURCE AUDIT '+json.dumps(stats))
