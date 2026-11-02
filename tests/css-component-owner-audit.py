#!/usr/bin/env python3
"""Fail-closed inventory of the ACTUALLY LOADED Salati CSS cascade.

Unlike the retired audit, recurse into @layer as well as @media/@supports/
@container. Keep the layer *and* conditional context for every declaration;
report intentional and potentially conflicting repeated ownership honestly.
No amount of "zero duplicates" may be reported if no inner rules were visited.
"""
from collections import defaultdict
from pathlib import Path
import json, re, tinycss2

root=Path(__file__).resolve().parents[1]
dist=root/'dist'
html=(dist/'index.html').read_text(encoding='utf-8')
linked=re.findall(r'<link\b[^>]*\brel="stylesheet"[^>]*\bhref="([^"]+)"',html)
assert linked==['salati-ui.css'],('Unexpected secondary stylesheet on application homepage',linked)
assert 'preview-sample-location-20261101' not in html,'Preview-only location setter imported into production'
assert not re.search(r'\bstyle="[^"]*!\s*important\b',html,re.I),'Inline forced priority still active'
all_source={}
for name in ('salati-ui.css','city-pages.css'):
    all_source[name]=(dist/name).read_text(encoding='utf-8')
inline_css=re.findall(r'<style\b[^>]*>(.*?)</style>',html,flags=re.S|re.I)
assert len(inline_css)==1,'Unexpected inline CSS on homepage'
all_source['index.html#first-paint']=inline_css[0]

by=defaultdict(list)
metrics={'rule_count':0,'declarations':0,'nested_layers_seen':0,
         'layer_rules':defaultdict(int),'at_rules':defaultdict(int),'source_rules':defaultdict(int)}
syntax_errors=[]
def clean(tokens):
    return tinycss2.serialize(tokens).strip()
def walk(nodes,filename,scope=(),layer='(unlayered)'):
    for n in nodes:
        if n.type=='error':
            syntax_errors.append((filename,scope,n.message))
        elif n.type=='qualified-rule':
            selector=clean(n.prelude)
            metrics['rule_count']+=1
            metrics['source_rules'][filename]+=1
            metrics['layer_rules'][layer]+=1
            for d in tinycss2.parse_declaration_list(n.content,skip_whitespace=True,skip_comments=True):
                if d.type=='error':
                    syntax_errors.append((filename,scope,d.message));continue
                if d.type!='declaration':continue
                metrics['declarations']+=1
                if d.name.startswith('--'):continue
                by[(filename,layer,scope,selector,d.lower_name)].append(
                    (clean(d.value),bool(d.important)))
        elif n.type=='at-rule':
            keyword=n.at_keyword.lower()
            metrics['at_rules'][keyword]+=1
            if n.content is None:
                continue
            prelude=clean(n.prelude)
            if keyword=='layer':
                metrics['nested_layers_seen']+=1
                child_layer=prelude if layer=='(unlayered)' else layer+'.'+prelude
                walk(tinycss2.parse_rule_list(n.content,skip_whitespace=True,skip_comments=True),
                     filename,scope,child_layer)
            elif keyword in ('media','supports','container','scope','starting-style'):
                walk(tinycss2.parse_rule_list(n.content,skip_whitespace=True,skip_comments=True),
                     filename,scope+((keyword,prelude),),layer)
            # @font-face and @keyframes are not component selector ownership.

for source,code in all_source.items():
    walk(tinycss2.parse_stylesheet(code,skip_whitespace=True,skip_comments=True),source)
assert not syntax_errors,('CSS parsing errors (first 12)',syntax_errors[:12])
assert metrics['nested_layers_seen']>=3,('Audit skipped nested layers',metrics['nested_layers_seen'])
assert metrics['layer_rules']['salati-base']>500,('Base layer was not traversed',dict(metrics['layer_rules']))
assert metrics['layer_rules']['salati-priority']>100,('Priority layer was not traversed',dict(metrics['layer_rules']))
assert metrics['source_rules']['city-pages.css']>10,'City pages stylesheet omitted'
assert metrics['source_rules']['index.html#first-paint']>=1,'First-paint CSS omitted'
assert metrics['rule_count']>=700,'Too few rules inspected for canonical CSS'

duplicate={key:values for key,values in by.items() if len(values)>1}
conflicts={key:values for key,values in duplicate.items() if len(set(values))>1}
priority_counts={name:len(re.findall(r'!\s*important\b',code,re.I)) for name,code in all_source.items()}
assert all(value==0 for value in priority_counts.values()),('Forced CSS priorities remain in current homepage/city sources',priority_counts)
assert '@layer salati-first-paint' in inline_css[0],'Critical first-paint style must be explicitly layered'
assert all(k[1]=='salati-first-paint' for k in by if k[0]=='index.html#first-paint')
assert 'city-pages.css' not in linked,'Do not import unrelated public-page CSS into app UI'

def describe(items):
    entries=[]
    for (source,layer,conditions,selector,property_name),declarations in items.items():
        entries.append(dict(source=source,layer=layer,conditions=list(conditions),selector=selector,
                            property=property_name,values=declarations))
    return entries
report_data={
    'sources':list(all_source),'homepage_links':linked,
    'rule_count':metrics['rule_count'],'declarations':metrics['declarations'],
    'nested_layers_seen':metrics['nested_layers_seen'],
    'layer_rules':dict(metrics['layer_rules']),
    'source_rules':dict(metrics['source_rules']),
    'at_rules':dict(metrics['at_rules']),
    'priority_counts':priority_counts,
    'duplicate_selector_property_groups':len(duplicate),
    'conflicting_selector_property_groups':len(conflicts),
    'duplicate_declarations':sum(len(v)-1 for v in duplicate.values()),
    'conflicts':describe(conflicts),
    'css_bytes':len(all_source['salati-ui.css'].encode('utf-8'))
}
report=root/'reports/css-source-maintainability.json'
report.parent.mkdir(parents=True,exist_ok=True)
report.write_text(json.dumps(report_data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Visible technical debt, not an invented "zero conflicts" claim.
print('CSS AUDIT '+json.dumps({k:v for k,v in report_data.items() if k!='conflicts'},ensure_ascii=False))
baseline_path=root/'tests/css-component-owner-baseline.json'
if baseline_path.exists():
    baseline=json.loads(baseline_path.read_text())
    for key in ('conflicting_selector_property_groups','duplicate_selector_property_groups','duplicate_declarations'):
        assert report_data[key]<=baseline[key],('CSS ownership debt increased',key,report_data[key],baseline[key])
else:
    print('WARNING: no reviewed ownership budget yet; report remains evidence only')
