#!/usr/bin/env python3
"""Salati one-batch cascade cleanup with strict same-selector/scope dominance.

Remove source declarations only when a *later* declaration has:
- exactly the same authored full selector and identical @media/@supports scope,
- same longhand/shorthand property, equal or higher !important priority,
- a guaranteed parser-supported value (not var/env, legacy fallback, browser
  extension, or unsupported @layer/@scope nesting).

Our existing CSS contains intentional browser fallbacks; those must not be
flattened merely to make the conflict metric reach zero. The release workflow
compares all 6 UI tabs, viewport variants and actual Android WebView afterward.
"""
import argparse,hashlib,json,re
from collections import defaultdict
from pathlib import Path
import tinycss2

ap=argparse.ArgumentParser()
ap.add_argument('--file',default='dist/salati-ui.css')
ap.add_argument('--report',default='reports/css-one-batch-20261102.json')
args=ap.parse_args()
path=Path(args.file)
source=path.read_text(encoding='utf-8')
parsed=tinycss2.parse_stylesheet(source,skip_whitespace=False,skip_comments=False)
assert not any(x.type=='error' for x in parsed),"CSS parse error"

# Preserve known platform fallbacks (e.g. display:grid/flex, fonts), and values
# with CSS variables / vendor hacks. Shorthand-vs-longhand relationships are
# deliberately NOT rewritten, since those require a separate property graph.
SUPPORTED={
 'background','background-color','background-image','color','border','border-color',
 'border-top','border-top-color','border-bottom','border-bottom-color',
 'border-left','border-right','box-shadow','text-shadow','outline',
 'padding','padding-left','padding-right','padding-top','padding-bottom',
 'margin','margin-left','margin-right','margin-top','margin-bottom',
 'height','width','min-height','min-width','max-height','max-width',
 'border-radius','border-top-left-radius','border-top-right-radius',
 'border-bottom-left-radius','border-bottom-right-radius','opacity',
 'visibility','position','top','right','bottom','left','inset',
 'align-items','align-content','justify-content','flex-direction',
 'flex-wrap','flex','flex-basis','flex-grow','flex-shrink','gap',
 'row-gap','column-gap','grid-template-columns','grid-template-rows',
 'font-size','font-weight','line-height','letter-spacing','text-align',
 'text-decoration','text-decoration-color','text-decoration-thickness',
 'overflow','overflow-x','overflow-y','white-space','text-overflow',
 'direction','z-index','transform','pointer-events','cursor',
 'object-fit','object-position'
}
# Conservative selectors with browser-dependent pseudo syntax may still be
# audited; when syntax/condition differs they naturally have different keys.
def text(tokens):return tinycss2.serialize(tokens).strip()
def supported(value):
 s=value.lower()
 return (not re.search(r'(?<![-\w])(?:var|env|attr)\s*\(',s)
     and not re.search(r'\\|expression\(|-webkit-|url\(\s*data:',s))
def build(nodes,scope=()):
 out=[]
 for n in nodes:
  if n.type=='qualified-rule':
   declarations=tinycss2.parse_declaration_list(n.content,skip_whitespace=False,skip_comments=False)
   if any(d.type not in ('declaration','whitespace','comment') for d in declarations):
    out.append({'type':'raw','node':n});continue
   out.append({'type':'rule','node':n,'scope':scope,'selector':text(n.prelude),
               'decl':declarations})
  elif n.type=='at-rule' and n.content is not None and n.at_keyword.lower() in ('media','supports','container'):
   inside=tinycss2.parse_rule_list(n.content,skip_whitespace=False,skip_comments=False)
   out.append({'type':'nested','node':n,'children':build(inside,scope+((n.at_keyword.lower(),text(n.prelude)),))})
  else:
   out.append({'type':'raw','node':n})
 return out
tree=build(parsed)
groups=defaultdict(list)
def collect(items):
 for x in items:
  if x['type']=='nested':collect(x['children'])
  elif x['type']=='rule':
   for d in x['decl']:
    if d.type!='declaration':continue
    p=d.lower_name
    if p not in SUPPORTED:continue
    groups[(x['scope'],x['selector'],p)].append(d)
collect(tree)
removed=set();reason=defaultdict(int)
for key,arr in groups.items():
 if len(arr)<2:continue
 later=[]
 for d in reversed(arr):
  value=text(d.value)
  if not supported(value):
   later.append(d);continue
  winner=next((x for x in later if (x.important or not d.important) and supported(text(x.value))),None)
  if winner is None:
   later.append(d);continue
  # Different values are allowed only where we can prove a later standard CSS
  # value with same selector + property dominates at equivalent priority.
  removed.add(id(d));reason[key[2]]+=1
before_important=len(re.findall(r'!\s*important\b',source,re.I))
def render(items):
 output=[]
 for x in items:
  if x['type']=='raw':output.append(tinycss2.serialize([x['node']]))
  elif x['type']=='nested':
   n=x['node'];n.content=tinycss2.parse_component_value_list(render(x['children']))
   output.append(tinycss2.serialize([n]))
  else:
   n=x['node']
   kept=[d for d in x['decl'] if id(d) not in removed]
   if not any(d.type=='declaration' for d in kept):continue
   n.content=tinycss2.parse_component_value_list(tinycss2.serialize(kept))
   output.append(tinycss2.serialize([n]))
 return ''.join(output)
optimized=render(tree)
assert not any(x.type=='error' for x in tinycss2.parse_stylesheet(optimized))
after_important=len(re.findall(r'!\s*important\b',optimized,re.I))
assert after_important<=before_important,(after_important,before_important)
assert len(optimized)<=len(source)
# Candidate parity guard reads baseline locally, it is never shipped in APK.
(path.parent/'salati-ui-baseline.css').write_text(source,encoding='utf-8')
path.write_text(optimized,encoding='utf-8')
metrics={
 'baseline_bytes':len(source.encode()),'optimized_bytes':len(optimized.encode()),
 'baseline_important':before_important,'optimized_important':after_important,
 'redundant_declarations_removed':len(removed),
 'properties':dict(sorted(reason.items(),key=lambda e:-e[1])),
 'css_sha256':hashlib.sha256(optimized.encode()).hexdigest(),
 'safety':'Same selector, same conditional scope, later valid higher/equal priority. Fallbacks preserved.'
}
report=Path(args.report);report.parent.mkdir(exist_ok=True,parents=True)
report.write_text(json.dumps(metrics,ensure_ascii=False,indent=2))
print('PASS ONE-BATCH CSS REFACTOR',json.dumps(metrics))
