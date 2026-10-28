# Offline Arabic reminder recordings

All six packaged MP3 files are newly generated fixed recordings of the Microsoft
Edge `ar-SA-HamedNeural` native Arabic male preset, created on 2026-10-28.
They are generic synthetic speech, with no imam, human reciter, or cloned voice
attribution. They are not downloaded adhan recordings.

| File | Spoken text |
|---|---|
| approach-fajr.mp3 | اقترب موعد صلاة الفجر |
| approach-dhuhr.mp3 | اقترب موعد صلاة الظهر |
| approach-asr.mp3 | اقترب موعد صلاة العصر |
| approach-maghrib.mp3 | اقترب موعد صلاة المغرب |
| approach-isha.mp3 | اقترب موعد صلاة العشاء |
| fajr-phrase.mp3 | الصلاة خير من النوم |

The files are bundled offline. Playback does not use an installed Arabic speech
engine, call a remote speech service, require credentials, or synthesize speech
at runtime.

## Provider and rights provenance

Service: Microsoft Edge online speech, preset `ar-SA-HamedNeural`.
Generation client: https://github.com/rany2/edge-tts
Client software license: LGPL-3.0. This is the client software's license; it does
not itself grant recording/output rights in Microsoft's generated speech.
The generated output remains subject to the provider's applicable terms:
https://www.microsoft.com/servicesagreement
No Creative Commons, MIT, or other independent audio-content license is asserted.
No affiliation or endorsement by Microsoft, an imam, or a reciter is implied.

## Reproduction and processing

`generate_sources.py` documents optional build-time creation with edge-tts.
`prepare_audio.py` converts the approved originals to 44.1 kHz mono MP3 at
96 kbps, removes metadata and normalizes conservatively with 3.5dB peak headroom
before encoding. It does not trim spoken words or change pitch/speed. No music,
noise reduction, voice conversion or reciter imitation was applied.
Generation is optional development tooling; the packaged app needs only MP3s.

`verification.json` records original/output SHA-256, decoded output duration,
sample rate, channel count, decoded peak, and clipping counts.
`transcripts.json` records independent unprompted Whisper medium ASR of all six
original generated files; each returned the intended phrase verbatim.

No subjective human listening was performed in this environment. Numerical and
transcription checks do not establish subjective voice quality or guarantee
perfect pronunciation. The source audio is a native Arabic preset throughout.
