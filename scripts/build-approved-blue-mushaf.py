#!/usr/bin/env python3
"""Build exact blue Madinah Mushaf leaves from an operator-verified 1429H PDF.

Never typeset, synthesise, correct or crop Quran ink. Output WEBP lossless and
per-page SHA-256, to be hosted separately from the Android release APK.

Requires: pip install pymupdf pillow
Example:
 python scripts/build-approved-blue-mushaf.py --pdf /private/blue-1429.pdf \
   --expected-sha256 <64 hex chars from inspected source PDF> \
   --first-pdf-page <1-based PDF page holding Quran page 1> \
   --confirm-page-map --output dist/quran-blue-pages
Before running, manually inspect the PDF pages for Quran page 1, 2, 3, 17 and 604.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

try:
    import fitz
    from PIL import Image, ImageChops
except ImportError as exc:
    raise SystemExit("Install PyMuPDF and Pillow: pip install pymupdf pillow") from exc

SOURCE_URL = ("https://d1.islamhouse.com/data/ar/ih_books/chain_01/"
              "Mushaf_AlMadinah/ar_Mushaf_AlMadinah_N_B.pdf")
EDITION = "KFGQPC Hafs 1429H standard blue, printed original"
COUNT = 604

def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as reader:
        for block in iter(lambda: reader.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def crop_exterior_only(image):
    """Only trim outside-ink paper strips; keep every ink pixel, including folio."""
    im = image.convert("RGB")
    r, g, b = im.split()
    ink = ImageChops.lighter(ImageChops.lighter(
        r.point(lambda v: 255 if v < 250 else 0),
        g.point(lambda v: 255 if v < 250 else 0)),
        b.point(lambda v: 255 if v < 250 else 0))
    bounds = ink.getbbox()
    if bounds is None:
        raise ValueError("Blank printed page")
    pad = 8
    x0 = max(0, bounds[0] - pad)
    y0 = max(0, bounds[1] - pad)
    x1 = min(im.width, bounds[2] + pad)
    y1 = min(im.height, bounds[3] + pad)
    if x1 - x0 < im.width * .55 or y1 - y0 < im.height * .60:
        raise ValueError("Unsafe trim: ink bounds unexpectedly small")
    edges = (ink.crop((0, 0, x0, im.height)),
             ink.crop((x1, 0, im.width, im.height)),
             ink.crop((0, 0, im.width, y0)),
             ink.crop((0, y1, im.width, im.height)))
    if any(edge.getbbox() is not None for edge in edges):
        raise ValueError("Ink detected outside proposed page crop")
    return im.crop((x0, y0, x1, y1)), [x0, y0, im.width - x1, im.height - y1]

def blue_ink_fraction(image):
    small = image.convert("RGB")
    small.thumbnail((350, 350))
    pixels = list(small.getdata())
    return sum(1 for r, g, b in pixels if b > r + 24 and b > g + 8 and b > 75) / max(1, len(pixels))

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pdf", required=True, type=Path)
    ap.add_argument("--expected-sha256", required=True)
    ap.add_argument("--first-pdf-page", type=int, required=True,
                    help="1-based PDF page showing the PRINTED Quran page 1")
    ap.add_argument("--confirm-bottom-folio", action="store_true",
                    help="CONFIRM after inspecting printed folio BELOW content for Quran pages 1,2,3,17,604")
    ap.add_argument("--confirm-page-map", action="store_true",
                    help="Explicitly confirm physical Quran pages 1,2,3,17,604 were inspected")
    ap.add_argument("--output", default="dist/quran-blue-pages", type=Path)
    ap.add_argument("--scale", default=1.8, type=float)
    args = ap.parse_args()
    if not args.confirm_page_map:
        ap.error("STOP: physically inspect pages 1, 2, 3, 17, 604 and use --confirm-page-map")
    if not args.confirm_bottom_folio:
        ap.error("STOP: visually inspect and confirm printed page number at the BOTTOM of the original pages 1,2,3,17,604 via --confirm-bottom-folio")
    pin = args.expected_sha256.lower()
    if not re.fullmatch(r"[a-f0-9]{64}", pin):
        ap.error("expected sha256 must be exactly 64 lowercase hexadecimal characters")
    if not args.pdf.is_file():
        ap.error("source PDF not found")
    actual = sha256(args.pdf)
    if pin != actual:
        raise SystemExit("STOP: PDF SHA-256 differs from externally recorded expected hash: " + actual)
    if args.first_pdf_page < 1 or not 1 <= args.scale <= 3:
        ap.error("Invalid first PDF page or scale")
    dest = args.output
    if dest.exists() and any(dest.iterdir()):
        raise SystemExit("STOP: output is not empty; use a fresh destination for reproducibility")
    doc = fitz.open(str(args.pdf))
    if args.first_pdf_page + COUNT - 1 > doc.page_count:
        raise SystemExit("STOP: source PDF does not hold 604 pages from the inspected offset")
    # Preflight two very different Quran leaves; never silently substitute black SVG pages.
    for quran_page in (3, 17):
        src_page = doc.load_page(args.first_pdf_page + quran_page - 2)
        pix = src_page.get_pixmap(colorspace=fitz.csRGB, alpha=False)
        proof = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        if blue_ink_fraction(proof) < .0002:
            raise SystemExit("STOP: source appears to lack a blue printed heading on Quran page " + str(quran_page))
    dest.mkdir(parents=True, exist_ok=True)
    output_pages = []
    try:
        for quran_page in range(1, COUNT + 1):
            pdf_idx = args.first_pdf_page + quran_page - 2
            pix = doc.load_page(pdf_idx).get_pixmap(matrix=fitz.Matrix(args.scale, args.scale),
                                                   colorspace=fitz.csRGB, alpha=False)
            original = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            cropped, trims = crop_exterior_only(original)
            filename = f"page-{quran_page:04d}.webp"
            output = dest / filename
            cropped.save(output, format="WEBP", lossless=True, method=4)
            # No JPEG / lossy interpolation / image-to-image artificial Quran.
            with Image.open(output) as verify:
                if ImageChops.difference(cropped, verify.convert("RGB")).getbbox():
                    raise ValueError("Lossless image pixel roundtrip failed")
            output_pages.append({
                "quranPage": quran_page,
                "pdfPage": pdf_idx + 1,
                "filename": filename,
                "sha256": sha256(output),
                "bytes": output.stat().st_size,
                "width": cropped.width,
                "height": cropped.height,
                "trimExteriorPx": trims,
            })
        if len(output_pages) != COUNT or len({p["sha256"] for p in output_pages}) != COUNT:
            raise ValueError("STOP: 604 unique, sequential Quran leaves are mandatory")
        manifest = {
            "version": 1,
            "edition": EDITION,
            "sourceUrl": SOURCE_URL,
            "sourceSha256": actual,
            "riwaya": "Hafs",
            "firstPdfPage": args.first_pdf_page,
            "pageCount": COUNT,
            "folioPlacement": "bottom",
            "folioAuditPages": [1, 2, 3, 17, 604],
            "folioAuditMethod": "manual visual confirmation of original PDF printed footer, no added page-number overlay",
            "pages": output_pages,
            "status": "local-generation-only; requires visual Quran + Android QA and separate hosting",
        }
        (dest / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print("PASS: 604 unique verified blue Mushaf pages in", dest,
              "total bytes", sum(p["bytes"] for p in output_pages))
    finally:
        doc.close()

if __name__ == "__main__":
    main()
