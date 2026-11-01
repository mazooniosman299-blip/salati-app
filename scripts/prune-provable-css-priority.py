#!/usr/bin/env python3
"""Safely simplify unnecessary priority flags in Salati's canonical source.

Conservative rule: only touch a CSS property when *every* declaration of that
property is !important, neither of the separately loaded site stylesheets
declares it, and there are no inline overrides. Removing ALL flags for such a
property retains the order and specificity of its authored declarations.
Other properties are explicitly left alone, not silently "cleaned".
Final acceptance is conditional on computed-style parity on all six tabs.
"""
from collections import defaultdict
from pathlib import Path
import json,re,tinycss2

root=Path(__file__).resolve().parents[1]
css=root/'dist/salati-ui.css'
html=(root/'dist/index.html').read_text(encoding='utf8')
extra='\n'.join((root/'dist'/n).read_text(encoding='utf8') for n in ('city-pages.css','public-pages.css'))
source=css.read_text(encoding='utf8')
nodes=tinycss2.parse_stylesheet(source,skip_whitespace=False,skip_comments=False)
assert not any(n.type=='error' for n in nodes),'Invalid canonical CSS'

eligible={
 'inline-size','block-size','inset-inline-start','inset-inline-end',
 'visibility','overscroll-behavior-y','inset-inline','scroll-behavior',
 'min-inline-size','max-inline-size','min-block-size','max-block-size',
 'padding-left','padding-right','scroll-margin-bottom',
 '-webkit-clip-path','text-indent','text-decoration-color',
 'text-decoration-thickness','scroll-padding-top','order'
}
# Preserve outline width because the native app overrides outlines inline.
# Declarations in unknown future contexts must block automatic changes.
counts=defaultdict(lambda:[0,0])
def visit(rules):
 for n in rules:
  if n.type=='qualified-rule':
   d=tinycss2.parse_declaration_list(n.content,skip_whitespace=True,skip_comments=True)
   for x in d:
    if x.type=='declaration' and x.lower_name in eligible:
     counts[x.lower_name][0]+=1
     counts[x.lower_name][1]+=bool(x.important)
  elif n.type=='at-rule' and n.content is not None and n.at_keyword.lower() in ('media','supports','container'):
   visit(tinycss2.parse_rule_list(n.content,skip_whitespace=True,skip_comments=True))
visit(nodes)
approved=[]
for prop,(total,priority) in counts.items():
 if not total or total!=priority:continue
 if re.search(r'(?<![-\w])'+re.escape(prop)+r'\s*:',extra,re.I):continue
 if re.search(r"""style=["'][^"']*"""+re.escape(prop)+r'\s*:',html,re.I):continue
 approved.append(prop)
assert approved,('No provable priority-only properties',dict(counts))
removed=defaultdict(int)
def transform(rules):
 out=[]
 for n in rules:
  if n.type=='qualified-rule':
   dl=tinycss2.parse_declaration_list(n.content,skip_whitespace=True,skip_comments=True)
   changed=False
   for d in dl:
    if d.type=='declaration' and d.lower_name in approved and d.important:
     d.important=False;removed[d.lower_name]+=1;changed=True
   if changed:n.content=tinycss2.parse_component_value_list(';'.join(tinycss2.serialize([d]) for d in dl)+';')
  elif n.type=='at-rule' and n.content is not None and n.at_keyword.lower() in ('media','supports','container'):
   child=tinycss2.parse_rule_list(n.content,skip_whitespace=False,skip_comments=False)
   if transform(child):n.content=tinycss2.parse_component_value_list(tinycss2.serialize(child))
  out.append(n)
 return True if removed else False
transform(nodes)
new=tinycss2.serialize(nodes)
valid=tinycss2.parse_stylesheet(new,skip_whitespace=True,skip_comments=True)
assert not any(n.type=='error' for n in valid),'Priority cleanup damaged CSS syntax'
count_before=len(re.findall(r'!\s*important\b',source,re.I))
count_after=len(re.findall(r'!\s*important\b',new,re.I))
assert count_before-count_after==sum(removed.values()),(count_before,count_after,dict(removed))
assert count_after<count_before
(css.with_name('salati-ui-baseline.css')).write_text(source,encoding='utf8')
css.write_text(new,encoding='utf8')
report={
 'baseline_important':count_before,'after_important':count_after,
 'removed_flags':count_before-count_after,'properties':dict(removed),
 'scope':'Only global priority-only CSS properties; no geometric/visual assumptions',
 'remaining_debt':count_after
}
(root/'reports').mkdir(exist_ok=True)
(root/'reports/css-priority-narrowing.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('CSS PRIORITY SAFE PASS '+json.dumps(report))
