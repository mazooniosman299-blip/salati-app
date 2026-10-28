#!/usr/bin/env python3
"""Normalize approved source files; requires ffmpeg. No runtime network dependency.
Usage: python prepare_audio.py /path/to/198-input-files
Files use the 198-final- naming recorded in SOURCES.md.
"""
import pathlib, subprocess, sys, json, struct, math, hashlib
root=pathlib.Path(__file__).resolve().parent
source=pathlib.Path(sys.argv[1])
clips={name:('final',None) for name in ['approach-fajr','approach-dhuhr','approach-asr','approach-maghrib','approach-isha','fajr-phrase']}
results=[]
for name,(kind,duration) in clips.items():
 p=source/f'198-{kind}-{name}.mp3'
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-f','f32le','-ac','1','-'])
 samples=struct.unpack('<%df'%(len(raw)//4),raw)
 peak=max(abs(x) for x in samples)
 # Keep 3.5 dB of headroom before MP3 re-encoding.
 gain=20*math.log10(10**(-3.5/20)/peak)
 command=['ffmpeg','-v','error','-y','-i',str(p)]
 if duration:command+=['-t',str(duration)]
 command+=['-af',f'volume={gain:.6f}dB','-ar','44100','-ac','1','-c:a','libmp3lame','-b:a','96k','-map_metadata','-1',str(root/f'{name}.mp3')]
 subprocess.run(command,check=True)
 out=root/f'{name}.mp3'
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(out),'-f','f32le','-ac','1','-'])
 samples=struct.unpack('<%df'%(len(raw)//4),raw)
 peak=max(abs(x) for x in samples)
 assert peak<1,'Clipped output'
 results.append({'file':out.name,'duration':len(samples)/44100,'sample_rate':44100,'channels':1,'peak_dbfs':round(20*math.log10(peak),2),'clipped_samples':sum(abs(x)>=1 for x in samples),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'gain_db':round(gain,3)})
(root/'verification.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(results,ensure_ascii=False,indent=2))
