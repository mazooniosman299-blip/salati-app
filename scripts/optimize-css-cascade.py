#!/usr/bin/env python3
"""Conservative canonical CSS AST optimization, with a measurable cascade audit.
Only drop a declaration when the SAME complete selector in the SAME exact
conditional scope has a later declaration of the same property at equal or
higher cascade priority. Skip @layer, @scope, @keyframes, font-face, custom
properties and unsupported nested semantics. Pixel/computed-style regression
must also pass before release. Never blindly delete !important.
"""
from collections import defaultdict
from pathlib import Path
import argparse, json, hashlib, re
import tinycss2

def clean_text(seq):
 return tinycss2.serialize(seq).strip()
def name(node):
 return ('@'+node.at_keyword.lower()) if node.type=='at-rule' else node.type
class Container:
 def __init__(self,nodes,context=(),parent=None):
  self.nodes=[];self.context=context;self.parent=parent
  for n in nodes:
   if n.type in ('whitespace','comment'):continue
   if n.type=='qualified-rule':
    declarations=tinycss2.parse_declaration_list(n.content,skip_whitespace=True,skip_comments=True)
    # Preserve keyframes and any exotic nested rules as authored.
    if all(d.type=='declaration' for d in declarations) and not any(c.startswith('@keyframes') for c in context):
     self.nodes.append({'kind':'rule','node':n,'context':context,
       'selector':clean_text(n.prelude),'decl':declarations})
    else:self.nodes.append({'kind':'other','node':n})
   elif n.type=='at-rule' and n.content is not None and n.at_keyword.lower() in ('media','supports','container'):
    ctx=context+('@'+n.at_keyword.lower()+' '+clean_text(n.prelude),)
    self.nodes.append({'kind':'nested','node':n,'child':Container(tinycss2.parse_rule_list(n.content,skip_whitespace=True,skip_comments=True),ctx,self)})
   else:self.nodes.append({'kind':'other','node':n})
 def iter_rules(self):
  for item in self.nodes:
   if item['kind']=='rule':yield item
   elif item['kind']=='nested':yield from item['child'].iter_rules()
 def render(self):
  out=[]
  for item in self.nodes:
   if item['kind']=='rule':
    decl=[x for x in item['decl'] if id(x) not in removed]
    if not decl:continue
    item['node'].content=tinycss2.parse_component_value_list(';'.join(tinycss2.serialize([d]) for d in decl)+';')
    out.append(item['node'])
   elif item['kind']=='nested':
    child=item['child'].render()
    if not child:continue
    item['node'].content=tinycss2.parse_component_value_list(child)
    out.append(item['node'])
   else:out.append(item['node'])
  return tinycss2.serialize(out)

parser=argparse.ArgumentParser()
parser.add_argument('--path',default='dist/salati-ui.css')
parser.add_argument('--report',default='reports/css-cascade-audit.json')
args=parser.parse_args()
file=Path(args.path)
source=file.read_text(encoding='utf8')
nodes=tinycss2.parse_stylesheet(source,skip_whitespace=True,skip_comments=True)
errors=[n.message for n in nodes if n.type=='error']
assert not errors,('Invalid CSS',errors)
tree=Container(nodes)
groups=defaultdict(list)
for rule in tree.iter_rules():
 # CSS custom properties are case-sensitive and must not be touched.
 # Keep fallback vendor and other properties intact.
 for d in rule['decl']:
  if d.name.startswith('--'):continue
  prop=d.lower_name
  if prop.startswith('-'):continue
  value=clean_text(d.value)
  # Keep browser support fallbacks, such as display:flex;display:grid.
  groups[(rule['context'],rule['selector'],prop)].append((d, value))
removed=set();shadowed=0;exact=0;priority=0;conflicts=0
for key,declarations in groups.items():
 if len(declarations)<2:continue
 # Iterate last to first; this is the only order of equal-specificity
 # declarations that is safe across the original unlayered CSS cascade.
 later=[]
 for decl,val in reversed(declarations):
  # Ignore vendor-sensitive and var fallback cases to protect WebViews.
  eligible=(not re.search(r'\b(?:var|env)\(',val) and
            not re.search(r'^(?:display|font|font-family|background|background-image|background-color|animation|transition)$',key[2]))
  winner=next(((new,v) for new,v in later if (new.important or not decl.important)),None)
  if winner and eligible:
   if winner[1]!=val:conflicts+=1
   else:exact+=1
   if decl.important:priority+=1
   removed.add(id(decl));shadowed+=1
  else:later.append((decl,val))
# NOTE: the removed rule's selector may be a comma list. Exact selector text
# is required, so all components still have identical cascade specificity/order.
optimized=tree.render()
valid=tinycss2.parse_stylesheet(optimized,skip_whitespace=True,skip_comments=True)
assert not any(n.type=='error' for n in valid)
assert optimized.count('{')==optimized.count('}'), 'Unbalanced output'
old_important=len(re.findall(r'!\s*important\b',source,re.I))
new_important=len(re.findall(r'!\s*important\b',optimized,re.I))
assert new_important<=old_important, (old_important,new_important,priority)  # serialization also removes comments
assert len(optimized)<len(source)
file.with_name('salati-ui-baseline.css').write_text(source,encoding='utf8')
file.write_text(optimized,encoding='utf8')
out={'baseline_bytes':len(source.encode()),'optimized_bytes':len(optimized.encode()),
 'baseline_important':old_important,'optimized_important':new_important,
 'declarations_removed':shadowed,'priority_declarations_removed':priority,'total_important_mentions_removed':old_important-new_important,
 'replaced_with_different_value':conflicts,'removed_with_same_value':exact,
 'exact_selector_property_groups':len(groups),
 'css_sha256':hashlib.sha256(optimized.encode()).hexdigest()}
target=Path(args.report);target.parent.mkdir(parents=True,exist_ok=True)
target.write_text(json.dumps(out,indent=2),encoding='utf8')
print('CSS AUDIT '+json.dumps(out))
