#!/usr/bin/env python3
"""Remove only earlier declarations proven shadowed by an EXACT later selector,
property, layer, and conditional context. Do NOT flatten media queries, change
specificity, merge layers, remove inside-rule fallbacks or invent CSS priority.

Safeguarded by 36 real-browser computed-style and geometry comparisons before
the candidate may be committed. NEVER run directly against production.
"""
from collections import defaultdict,Counter
from pathlib import Path
import json,tinycss2,re
root=Path(__file__).resolve().parents[1]
path=root/'dist/salati-ui.css'
original=path.read_text(encoding='utf8')
assert original.startswith('@layer salati-base,salati-priority;')
assert not re.search(r'!\s*important\b',original,re.I)
ast=tinycss2.parse_stylesheet(original,skip_whitespace=False,skip_comments=False)
assert not any(x.type=='error' for x in ast)
groups=defaultdict(list)
qualified=[]
def traverse(nodes,layer='(unlayered)',conditions=()):
 for n in nodes:
  if n.type=='qualified-rule':
   selector=tinycss2.serialize(n.prelude).strip()
   d=tinycss2.parse_declaration_list(n.content,skip_comments=False,skip_whitespace=False)
   assert not any(x.type=='error' for x in d),(selector,'bad declaration')
   rule_id=len(qualified)
   qualified.append((n,d))
   for idx,item in enumerate(d):
    if item.type=='declaration' and not item.name.startswith('--'):
     key=(layer,conditions,selector,item.lower_name)
     groups[key].append((rule_id,idx))
  elif n.type=='at-rule' and n.content is not None and n.lower_at_keyword in ('layer','media','supports','container','scope','starting-style'):
   keyword=n.lower_at_keyword
   pre=tinycss2.serialize(n.prelude).strip()
   child_layer=(pre if layer=='(unlayered)' else layer+'.'+pre) if keyword=='layer' else layer
   child_cond=conditions if keyword=='layer' else conditions+((keyword,pre),)
   traverse(tinycss2.parse_rule_list(n.content,skip_whitespace=False,skip_comments=False),child_layer,child_cond)
traverse(ast)
removed=defaultdict(set)
for key,found in groups.items():
 # Earlier SAME-RULE declarations may be intentional syntax fallbacks.
 # Remove earlier occurrences ONLY when a separate later rule has the
 # identical selector, conditional context and cascade layer.
 last_rule=max(i for i,_ in found)
 for rule,idx in found:
  if rule!=last_rule:
   removed[rule].add(idx)
assert sum(len(x) for x in removed.values())>20,'Unexpected CSS ownership inventory'
# Reparse nested token blocks to preserve the exact authored structure when
# removal is not needed; update *only* the qualified rules with redundant decls.
counter=0
qindex=0
def rewrite(nodes):
 global qindex,counter
 for n in nodes:
  if n.type=='qualified-rule':
   rid=qindex;qindex+=1
   if rid in removed:
    decls=tinycss2.parse_declaration_list(n.content,skip_whitespace=False,skip_comments=False)
    keep=[d for j,d in enumerate(decls) if j not in removed[rid]]
    assert len(keep)<len(decls)
    # Preserve punctuation and source comments. Declaration serialization
    # includes terminal semicolons; empty rules are valid CSS.
    n.content=tinycss2.parse_component_value_list(tinycss2.serialize(keep))
    counter+=len(removed[rid])
  elif n.type=='at-rule' and n.content is not None and n.lower_at_keyword in ('layer','media','supports','container','scope','starting-style'):
   children=tinycss2.parse_rule_list(n.content,skip_whitespace=False,skip_comments=False)
   before=qindex
   rewrite(children)
   if qindex>before and any(index>=before and index<qindex for index in removed):
    n.content=tinycss2.parse_component_value_list(tinycss2.serialize(children))
rewrite(ast)
assert counter==sum(len(x) for x in removed.values()),(counter,removed)
optimized=tinycss2.serialize(ast)
assert len(optimized)<len(original),(len(optimized),len(original))
assert optimized.startswith('@layer salati-base,salati-priority;')
assert not re.search(r'!\s*important\b',optimized,re.I)
assert not any(x.type=='error' for x in tinycss2.parse_stylesheet(optimized))
(path.parent/'salati-ui-baseline.css').write_text(original,encoding='utf8')
path.write_text(optimized,encoding='utf8')
report={'original_bytes':len(original.encode()),'optimized_bytes':len(optimized.encode()),
        'removed_shadowed_declarations':counter,'qualified_rules':len(qualified),
        'remaining_inside_rule_fallbacks':'preserved',
        'scope_safety':'identical selector, layer, @media/@supports/@container conditions',
        'approval_requires':'36 Chromium computed-style/geometry comparisons and native Android test'}
(root/'reports').mkdir(exist_ok=True)
(root/'reports/css-dedupe-20261102.json').write_text(json.dumps(report,indent=2)+'\n')
print('CSS DEDUP CANDIDATE (NOT YET APPROVED)',report)
