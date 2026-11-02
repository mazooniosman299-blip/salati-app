#!/usr/bin/env python3
"""Render only genuine publisher PDF pages into lossless WEBP review samples.

Never alter Qur'an text, lines, ayah ornaments or page borders, and NEVER
publish on the Salati production website/APK. PDF leaf numbers here are PDF
indices, not claimed to equal the printed mushaf page numbering.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from PIL import Image

SOURCE_SHA256 = "5c4297de1fb6b654f641eed33242408d89432cbecf8a96ff5d297cb45fea7f07"
SOURCE_SIZE = 243520529
SAMPLES = (5, 6, 7, 8, 10, 12, 20, 25, 40)
def digest(file):
    result = hashlib.sha256()
    with open(file, 'rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()

def main(pdf_name, directory):
    pdf = Path(pdf_name)
    out = Path(directory)
    if pdf.stat().st_size != SOURCE_SIZE or digest(pdf) != SOURCE_SHA256:
        raise RuntimeError("STOP: official green edition PDF checksum/size mismatch")
    pages = subprocess.check_output(["pdfinfo", str(pdf)], text=True)
    count = int(next(x.split(":", 1)[1].strip() for x in pages.splitlines() if x.startswith("Pages:")))
    if not 604 <= count <= 700:
        raise RuntimeError("Unexpected official green PDF page count: " + str(count))
    out.mkdir(parents=True, exist_ok=True)
    records = []
    for index in SAMPLES:
        if index > count:
            raise RuntimeError("Source sample out of bounds")
        dest = out / f"pdf-{index:04d}"
        subprocess.run(["pdftoppm", "-f", str(index), "-l", str(index),
                        "-singlefile", "-scale-to", "1120", "-png",
                        str(pdf), str(dest)], check=True, timeout=150)
        png = dest.with_suffix(".png")
        target = dest.with_suffix(".webp")
        with Image.open(png) as img:
            if img.width < 250 or img.height < 300:
                raise RuntimeError(f"PDF page {index} was blank/invalid")
            img.save(target, format="WEBP", lossless=True, method=5)
            width, height = img.size
        png.unlink()
        records.append({"pdfPage": index, "filename": target.name,
                        "sha256": digest(target), "bytes": target.stat().st_size,
                        "width": width, "height": height})
    manifest = {
        "edition": "KFGQPC Hafs standard39-2 green PDF",
        "sourceUrl": "https://qurancomplex.gov.sa/wp-content/uploads/isdarat/hafs/standard39-2.pdf",
        "publisher": "King Fahd Glorious Quran Printing Complex",
        "sourceSha256": SOURCE_SHA256,
        "sourceBytes": SOURCE_SIZE,
        "totalPDFPages": count,
        "pageIndicesAre": "PDF leaf positions, not verified Quran 604-page indices",
        "referenceMatch": "UNVERIFIED: not approved as exact user-selected style 5",
        "render": "pdftoppm -scale-to 1120 -> WEBP lossless",
        "pages": records
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"PASS: {len(records)} authentic publisher leaves extracted from SHA256-pinned {count}-leaf PDF into {out}")
if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: render-official-green-review.py <official-verified-pdf> <review-output-dir>")
    main(sys.argv[1], sys.argv[2])
