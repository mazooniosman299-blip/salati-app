#!/usr/bin/env python3
"""Reject the observed early navigation position and incomplete paint before a native tap."""
from pathlib import Path
from PIL import Image,ImageDraw
import subprocess,sys,tempfile

helper=Path(__file__).with_name('android-emulator-screen-preflight.py')
def check(mode,files):
 return subprocess.run([sys.executable,str(helper),mode,*map(str,files)],capture_output=True,text=True)
with tempfile.TemporaryDirectory() as directory:
 folder=Path(directory)
 def frame(name,y,labels=True):
  im=Image.new('RGB',(432,960),(10,14,18));d=ImageDraw.Draw(im)
  d.rounded_rectangle((352,y-24,410,y+24),radius=14,fill=(25,80,180))
  if labels:
   for x in [46,113,180,247,314,381]:
    d.rectangle((x-4,y-14,x+4,y-3),fill='white')
    d.rectangle((x-11,y+8,x+11,y+11),fill='white')
  path=folder/name;im.save(path);return path
 early=frame('early.png',866)
 assert check('ready',[early]).returncode!=0,'Early inset layout was incorrectly accepted as interactive'
 placeholder=frame('placeholder.png',905,False)
 assert check('ready',[placeholder]).returncode!=0,'Blue-only placeholder was incorrectly accepted as a full navigation bar'
 a=frame('a.png',905);b=frame('b.png',905);c=frame('c.png',905)
 assert check('ready',[a]).returncode==0,'Complete settled navigation was rejected'
 stable=check('quran-tap-stable',[a,b,c]);assert stable.returncode==0,stable.stderr
 assert stable.stdout.strip()=='312 905',stable.stdout
 shifted=frame('shifted.png',895)
 assert check('quran-tap-stable',[a,b,shifted]).returncode!=0,'Moving navigation produced a stale native tap'
 assert check('quran-tap-stable',[a,b]).returncode!=0,'Insufficient stable frames accepted'
print('PASS native navigation readiness: incomplete paint, early insets and moving targets rejected; three settled frames give the real tap')
