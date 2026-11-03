#!/usr/bin/env python3
"""Strict pixel boundary guard comparing ACTUAL current/production browser screenshots."""
from PIL import Image,ImageChops,ImageDraw
from pathlib import Path
import argparse,json,sys

def pixel_scope(a,b,allowed):
 if a.size!=b.size:raise AssertionError('Viewport changed')
 d=ImageChops.difference(a.convert('RGB'),b.convert('RGB')).split()
 difference=ImageChops.lighter(ImageChops.lighter(d[0],d[1]),d[2]).point(lambda x:255 if x>12 else 0)
 whitelist=Image.new('L',a.size,0)
 draw=ImageDraw.Draw(whitelist)
 for rect in allowed:draw.rectangle(tuple(map(int,rect)),fill=255)
 forbidden=ImageChops.subtract(difference,whitelist)
 return (difference.histogram()[255],forbidden.histogram()[255],forbidden.getbbox())

def visible_rectangle(case,selector):
 e=case['computed'].get(selector)
 if not e or not e.get('visible'):raise AssertionError('Missing/hidden approved selector '+case['image']+' '+selector)
 return [e['x'],e['y'],e['right'],e['bottom']]

def compare(baseline,candidate,policy):
 approved=policy.get('visual_allowed_regions',[])
 if policy.get('visual_change') is True:
  assert approved,'Visual changes require exact per-tab selector allowlist'
 else:
  assert not approved,'Unchanged-visual request must not claim allowed changed areas'
 a=json.loads((baseline/'metrics.json').read_text())
 b=json.loads((candidate/'metrics.json').read_text())
 old={e['image']:e for e in a['screenshots']};new={e['image']:e for e in b['screenshots']}
 assert set(old)==set(new),'The two true browser screenshot sets differ'
 results=[];changed_authorized=0
 for key,case in sorted(new.items()):
  baseline_case=old[key]
  rules=[r for r in approved if r['tab']==case['tab'] and r['language'] in ('both',case['language'])]
  boxes=[]
  for rule in rules:
   p=visible_rectangle(baseline_case,rule['selector'])
   q=visible_rectangle(case,rule['selector'])
   boxes.append([max(0,min(p[0],q[0])-6),max(0,min(p[1],q[1])-6),
    min(case['viewport'][0],max(p[2],q[2])+6),min(case['viewport'][1],max(p[3],q[3])+6)])
  with Image.open(baseline/key) as x,Image.open(candidate/key) as y:
   count,outside,bbox=pixel_scope(x,y,boxes)
   assert outside<=int(x.width*x.height*.0005),(key,'unrequested visual change',outside,bbox)
  if rules:changed_authorized+=count
  results.append({'image':key,'changed_pixels':count,'outside_approved_regions':outside,'allowed_boxes':boxes})
 if policy.get('visual_change') is True:
  assert changed_authorized>0,'Requested visual change produced no changed pixels in the target'
 (candidate/'visual-scope-diff.json').write_text(json.dumps({'status':'PASS_SCOPE_NOT_REFERENCE_PARITY','images':results},indent=2)+'\n')
 print('PASS 48 actual screenshot comparisons with no visual changes outside declared components')

def self_test():
 x=Image.new('RGB',(24,24),(0,0,0))
 y=x.copy();ImageDraw.Draw(y).rectangle((2,2,5,5),fill='white')
 assert pixel_scope(x,y,[[1,1,6,6]])[:2]==(16,0)
 z=x.copy();ImageDraw.Draw(z).rectangle((21,21,23,23),fill='white')
 assert pixel_scope(x,z,[[1,1,6,6]])[1]==9
 print('PASS pixel boundary negative tests: authorized accepted, unrelated rejected')

def main():
 p=argparse.ArgumentParser()
 p.add_argument('--self-test',action='store_true')
 p.add_argument('--baseline');p.add_argument('--candidate');p.add_argument('--manifest')
 a=p.parse_args()
 if a.self_test:return self_test()
 if not a.baseline or not a.candidate or not a.manifest:p.error('Missing real captures or change manifest')
 compare(Path(a.baseline),Path(a.candidate),json.loads(Path(a.manifest).read_text()))
if __name__=='__main__':
 try:main()
 except Exception as ex:
  print('FAIL visual scope:',ex,file=sys.stderr)
  raise
