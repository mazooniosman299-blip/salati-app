#!/usr/bin/env python3
"""Scan every tracked source, document and binary archive; intentionally not a semantic proof."""
import ast, json, re, subprocess, sys, zipfile, xml.etree.ElementTree as ET
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
errors=[]; warnings=[]; stats=Counter()
class HTMLCheck(HTMLParser): pass

def fail(file,kind,details=''):
 errors.append({'file':str(file),'kind':kind,'details':str(details)[:250]})
def warn(file,kind,details=''):
 warnings.append({'file':str(file),'kind':kind,'details':str(details)[:250]})

def refs(file,html):
 class LinkCheck(HTMLParser):
  def handle_starttag(self,tag,attributes):
   attrs=dict(attributes)
   if tag not in ('link','script','img'):return
   url=attrs.get('href') if tag=='link' else attrs.get('src')
   if not url or url.startswith(('https:','http:','data:','mailto:','tel:','//','#','blob:')):return
   url=url.split('?')[0].split('#')[0]
   if not url or url.startswith('javascript:'):return
   target=(ROOT/'dist'/url.lstrip('/') if url.startswith('/') else file.parent/url)
   if not target.exists():warn(file.relative_to(ROOT),'missing-local-asset',url)
   else:stats['resolved_asset_refs']+=1
 LinkCheck().feed(html)

for file in sorted(ROOT.rglob('*')):
 if not file.is_file() or any(part in ('.git','node_modules','__pycache__') for part in file.relative_to(ROOT).parts):continue
 rel=file.relative_to(ROOT)
 ext=file.suffix.lower()
 stats['files']+=1;stats['bytes']+=file.stat().st_size
 stats['extension:'+ext]+=1
 if ext in ('.apk','.zip','.jar'):
  try:
   with zipfile.ZipFile(file) as archive:
    if archive.testzip():fail(rel,'archive-crc')
    else:stats['verified_archives']+=1
  except Exception as exc:fail(rel,'archive',exc)
  continue
 if ext not in ('.json','.js','.cjs','.py','.xml','.svg','.html','.css','.md','.txt','.yml','.sh','.gradle','.properties','.example'):continue
 try:content=file.read_text(encoding='utf-8-sig')
 except Exception as exc:fail(rel,'encoding',exc);continue
 if '\x00' in content:fail(rel,'nul-byte');continue
 try:
  if ext=='.json':json.loads(content);stats['valid_json']+=1
  elif ext in ('.xml','.svg'):ET.fromstring(content);stats['valid_xml_svg']+=1
  elif ext=='.py':ast.parse(content,filename=str(rel));stats['valid_python']+=1
  elif ext=='.html':
   HTMLCheck().feed(content);stats['valid_html']+=1
   if rel.parts[0]=='dist':refs(file,content)
  elif ext in ('.js','.cjs'):
   argv=['node','--check'] if ext=='.cjs' else ['node','--input-type=module','--check']
   proc=subprocess.run(argv,input=content,capture_output=True,text=True,timeout=25)
   if proc.returncode:fail(rel,'javascript-syntax',proc.stderr[:200])
   else:stats['valid_javascript']+=1
   if ext=='.js' and rel.parts[0]!='dist':
    pattern=r"""(?:import|export)\s*(?:[^\n;]*?\sfrom\s*)?["'](\.[^"']+)["']|import\(\s*["'](\.[^"']+)["']\s*\)"""
    for match in re.finditer(pattern,content):
     name=match.group(1) or match.group(2)
     path=file.parent/name
     if any(p.is_file() for p in (path,path.with_suffix('.js'),path/'index.js')):stats['valid_relative_imports']+=1
     else:fail(rel,'unresolved-local-import',name)
 except Exception as exc:fail(rel,'parse-error',exc)

manifest=ROOT/'android/app/src/main/AndroidManifest.xml'
if manifest.exists():
 try:
  doc=ET.parse(manifest).getroot();prefix='{http://schemas.android.com/apk/res/android}'
  application=doc.find('application')
  if application.attrib.get(prefix+'usesCleartextTraffic')!='false':warn('AndroidManifest.xml','cleartext-traffic')
  if application.attrib.get(prefix+'allowBackup')!='false':warn('AndroidManifest.xml','backup-not-disabled')
  stats['manifest_permissions']=len(doc.findall('uses-permission'))
 except Exception as exc:fail('AndroidManifest.xml','security-check',exc)

report={'status':'PASS' if not errors else 'FAIL','stats':dict(stats),
 'errors':errors[:100],'error_count':len(errors),'warnings':warnings[:100],'warning_count':len(warnings),
 'limitations':['Structural checks cannot certify behavior, permissions or user experience','APK CRC validation does not prove released APK is built from current source']}
output=ROOT/'reports/full-source-audit-latest.json'
output.parent.mkdir(exist_ok=True)
output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'stats':{k:v for k,v in stats.items() if not k.startswith('extension:')},'errors':errors[:15],'warnings':warnings[:15],'error_count':len(errors),'warning_count':len(warnings)},ensure_ascii=False))
sys.exit(1 if errors else 0)
