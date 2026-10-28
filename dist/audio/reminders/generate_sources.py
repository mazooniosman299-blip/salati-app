#!/usr/bin/env python3
"""Optional build-time generation. Install edge-tts; output never generated at runtime.
Usage: python generate_sources.py /tmp/salati-audio-sources
Then: python prepare_audio.py /tmp/salati-audio-sources
The speech provider must be reachable and its applicable terms must be respected.
"""
import asyncio, pathlib, sys
import edge_tts
PHRASES={
 'approach-fajr':'اقترب موعد صلاة الفجر',
 'approach-dhuhr':'اقترب موعد صلاة الظهر',
 'approach-asr':'اقترب موعد صلاة العصر',
 'approach-maghrib':'اقترب موعد صلاة المغرب',
 'approach-isha':'اقترب موعد صلاة العشاء',
 'fajr-phrase':'الصلاة خير من النوم',
}
async def main():
 out=pathlib.Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
 for name,text in PHRASES.items():
  await edge_tts.Communicate(text,'ar-SA-HamedNeural').save(str(out/f'198-final-{name}.mp3'))
asyncio.run(main())
