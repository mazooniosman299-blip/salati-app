#!/usr/bin/env python3
"""Reassemble the immutable signed release from public Git blobs; no keys are stored here."""
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
parts=ROOT/"apk-release-parts"/"v1.0.112"
manifest=json.loads((parts/"manifest.json").read_text(encoding="utf-8"))
output=ROOT/"dist"/"downloads"/manifest["filename"]
output.parent.mkdir(parents=True,exist_ok=True)
tmp=output.with_suffix(".apk.staging")
files=[parts/f"part{i:02d}.bin" for i in range(manifest["partCount"])]
if not all(f.is_file() for f in files):
    sys.exit("Missing one or more immutable release parts")
digest=hashlib.sha256()
size=0
with tmp.open("wb") as destination:
    for i,file in enumerate(files):
        with file.open("rb") as source:
            while True:
                chunk=source.read(1024*1024)
                if not chunk: break
                digest.update(chunk)
                size+=len(chunk)
                destination.write(chunk)
if size!=manifest["size"] or digest.hexdigest()!=manifest["sha256"]:
    tmp.unlink(missing_ok=True)
    sys.exit("Signed APK reconstruction failed SHA-256 or byte-count check")
tmp.replace(output)
print(f"Verified signed APK: {output.name}, {size} bytes, SHA-256 {digest.hexdigest()}")
