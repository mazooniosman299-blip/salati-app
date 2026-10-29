"""First-party UI must not reintroduce neutral gray fills or decorations."""
from pathlib import Path
import re
import tinycss2
root=Path(__file__).resolve().parents[1]
def rules(nodes):
 for node in nodes:
  if node.type=='qualified-rule':yield node
  elif node.type=='at-rule' and node.content:yield from rules(tinycss2.parse_rule_list(node.content))
def is_gray(value):
 value=value.lower()
 if len(value) in (3,4):value=''.join(c*2 for c in value)
 r,g,b=[int(value[i:i+2],16) for i in (0,2,4)]
 return max(r,g,b)-min(r,g,b)<=3 and 0<r<255
issues=[]
for name in ['style.css','light-theme.css','salati-design.css','city-pages.css','public-pages.css','reference-layout.css']:
 for rule in rules(tinycss2.parse_stylesheet((root/'dist'/name).read_text())):
  selector=tinycss2.serialize(rule.prelude).strip()
  for declaration in tinycss2.parse_declaration_list(rule.content):
   if declaration.type!='declaration':continue
   if declaration.name in ['box-shadow','text-shadow','filter','mask','-webkit-mask']:continue
   value=tinycss2.serialize(declaration.value)
   for color in re.findall(r'#([a-fA-F0-9]{3,8})\b',value):
    if is_gray(color):issues.append(f'{name}:{declaration.source_line}: {selector}: {declaration.name}=#{color}')
assert not issues,'Neutral grays bypass the shared reference palette:\n'+'\n'.join(issues)
# Protect the complete new approved palette, not merely absence of neutral gray.
approved={'0B0E13','040509','15181D','32383F','FFFFFF','AEBCCB','000000','2563EB','1D4ED8','1E40AF','3B82F6'}
for name in ['style.css','light-theme.css','salati-design.css','city-pages.css','public-pages.css','reference-layout.css']:
 for rule in rules(tinycss2.parse_stylesheet((root/'dist'/name).read_text())):
  selector=tinycss2.serialize(rule.prelude)
  for declaration in tinycss2.parse_declaration_list(rule.content):
   if declaration.type!='declaration':continue
   for value in re.findall(r'#([a-fA-F0-9]{3,8})\b',tinycss2.serialize(declaration.value)):
    if len(value)in(3,4):value=''.join(c*2 for c in value)
    assert value[:6].upper()in approved,f'{name}: legacy color bypasses charcoal palette: #{value}'
print('PASS: every current stylesheet literal belongs to the final explicitly requested matte palette (black reserved for masks/shadows).')

# Native glass surfaces must have a visible cool tint as well (Android ARGB).
import xml.etree.ElementTree as ET
ns='{http://schemas.android.com/apk/res/android}'
for name in ['widget_background.xml','widget_glass_header.xml','widget_glass_strip.xml']:
 tree=ET.parse(root/'android/app/src/main/res/drawable'/name)
 for element in tree.iter():
  for key,value in element.attrib.items():
   if key in [ns+'color',ns+'startColor',ns+'centerColor',ns+'endColor'] and value.startswith('#'):
    rgb=value[-6:];r,g,b=[int(rgb[i:i+2],16) for i in (0,2,4)]
    if element.tag=='stroke':continue
    assert rgb.upper() in ['040509','0B0E13','15181D','32383F','FFFFFF'],f'{name}: unexpected native surface {value}'
print('PASS: shared colors cover all first-party styles and native widget glass surfaces.')
activity=(root/'android/app/src/main/java/com/salati/prayer/MainActivity.java').read_text()
assert '#171717' not in activity and '#CCCCCC' not in activity and '#D4B87F' not in activity,'Native confirmation must use the reference palette, not gray/gold literals'
print('PASS: native confirmation no longer keeps a separate gray/gold palette.')
html=(root/'dist/index.html').read_text()
for tag in re.findall(r'<(?:path|rect|circle|polygon|stop)\b[^>]*>',html):
 for color in re.findall(r'(?:fill|stroke|stop-color)="#([a-fA-F0-9]{3,8})"',tag):
  assert not is_gray(color),'Inline illustration bypasses theme: #'+color
print('PASS: inline Quran and Qibla illustrations have no hardcoded neutral gray.')
