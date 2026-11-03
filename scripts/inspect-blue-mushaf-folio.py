#!/usr/bin/env python3
"""Visual QA sheet for the actual printed BLUE Madinah Mushaf source PDF.

Shows the TOP and BOTTOM strips of five distinct publisher leaves side by side.
Do not use OCR, synthetic verse text, or auto-guess the printed folio position.
The operator must confirm: surah/juz above, printed page number BELOW.
No manifest is approved by this QA sheet alone.
"""
import argparse
import hashlib
from pathlib import Path

try:
    import fitz
    from PIL import Image, ImageDraw
except ImportError as exc:
    raise SystemExit("Install PyMuPDF and Pillow: pip install pymupdf pillow") from exc

SAMPLES = (1, 2, 3, 17, 604)

def sha256(path: Path):
    value = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()

def image_from_page(page, scale):
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale),
                          colorspace=fitz.csRGB, alpha=False)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pdf", type=Path, required=True)
    p.add_argument("--first-pdf-page", type=int, required=True,
                   help="1-based index of PDF page corresponding to Quran page 1")
    p.add_argument("--expected-sha256", default="",
                   help="Optional externally recorded source hash")
    p.add_argument("--output", type=Path, default=Path("/tmp/salati-blue-folio-proof.png"))
    args = p.parse_args()
    if not args.pdf.is_file():
        p.error("Source PDF not found")
    digest = sha256(args.pdf)
    if args.expected_sha256 and digest.lower() != args.expected_sha256.lower():
        raise SystemExit("STOP: Source PDF does not match the expected digest")
    if args.first_pdf_page < 1:
        p.error("first-pdf-page must be 1 or greater")
    doc = fitz.open(str(args.pdf))
    if args.first_pdf_page + 603 > doc.page_count:
        raise SystemExit("STOP: source PDF does not contain the full 604 Quran-page range")

    tile_w = 400
    tile_h = 360
    canvas = Image.new("RGB", (tile_w * len(SAMPLES), tile_h), "#F0F1F4")
    painter = ImageDraw.Draw(canvas)
    for col, quran_page in enumerate(SAMPLES):
        pdf_page = args.first_pdf_page + quran_page - 1
        page_img = image_from_page(doc[pdf_page - 1], 1.2)
        page_img.thumbnail((380, 740))
        w, h = page_img.size
        top = page_img.crop((0, 0, w, max(1, round(h * .22))))
        bottom = page_img.crop((0, min(h - 1, round(h * .78)), w, h))
        for sub, y in ((top, 40), (bottom, 198)):
            sub.thumbnail((380, 128))
            canvas.paste(sub, (col * tile_w + (tile_w - sub.width) // 2, y))
        painter.text((col * tile_w + 12, 12),
                     f"Quran page {quran_page} | PDF page {pdf_page}",
                     fill="#18243A")
        painter.text((col * tile_w + 12, 175), "Bottom folio proof", fill="#18243A")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(args.output)
    print("Source SHA-256:", digest)
    print("Visual folio contact sheet:", args.output)
    print("Inspect top and bottom of ALL five leaves. No OCR or automatic approval.")
    doc.close()

if __name__ == "__main__":
    main()
