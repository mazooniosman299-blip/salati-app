"""Decode every shipped adhan/dua completely; non-audio trailing packets fail.

ffmpeg without -xerror can print corrupt-frame errors yet exit0. Require both
a zero exit status and empty error output, not metadata/duration alone.
"""
from pathlib import Path
import json,subprocess,shutil
root=Path(__file__).resolve().parents[1]
ffmpeg=shutil.which('ffmpeg')
if not ffmpeg:
 from imageio_ffmpeg import get_ffmpeg_exe
 ffmpeg=get_ffmpeg_exe()
assert ffmpeg,'ffmpeg required for full packaged recording validation'
rows=[]
for name in ['nufais-clean-v3.mp3','qatami-original-v4.ogg','makkah-clean-v3.mp3','aqsa-clean-v3.mp3','wasilah.mp3']:
 result=subprocess.run([ffmpeg,'-xerror','-v','error','-i',str(root/'dist/audio'/name),'-f','null','-'],capture_output=True,text=True)
 assert result.returncode==0 and not result.stderr.strip(),(name,result.returncode,result.stderr)
 rows.append({'file':name,'strict_full_decode':'PASS'})
out=root/'reports/packaged-recordings';out.mkdir(parents=True,exist_ok=True)
(out/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
print('PASS complete strict decoding of all4 adhan recordings and post-adhan dua, zero invalid packets')
