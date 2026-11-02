#!/usr/bin/env python3
"""Authorized exact KFQC page proof from byte-verified print source.

Only WHITE exterior PDF margin pixels may be removed from the left/right.
Quran script, verse markers, header, ornaments, full page height are untouched.
Not a reproduction or AI generated render.
"""
from pathlib import Path
from PIL import Image, ImageChops
import sys,json,hashlib

SOURCE_SHA="5c4297de1fb6b654f641eed33242408d89432cbecf8a96ff5d297cb45fea7f07"

def sha(data): return hashlib.sha256(data).hexdigest()
def trim_white_horizontal(im,margin=7):
    im=im.convert('RGB')
    w,h=im.size
    masks=[band.point(lambda value: 255 if value<245 else 0) for band in im.split()]
    ink=ImageChops.lighter(ImageChops.lighter(masks[0],masks[1]),masks[2])
    bbox=ink.getbbox()
    if not bbox: raise ValueError('Blank original Mushaf page')
    left=max(0,bbox[0]-margin)
    right=min(w,bbox[2]+margin)
    # Every colored/dark pixel must be INSIDE the cut area.
    for exterior in (ink.crop((0,0,left,h)),ink.crop((right,0,w,h))):
        if exterior.getbbox() is not None:raise ValueError('STOP: original ayah or ornament would be cropped')
    if right-left<0.45*w or h<500:raise ValueError('Unexpectedly small Quran page')
    return im.crop((left,0,right,h)),(left,right)

def main(source_folder,output_folder):
    src=Path(source_folder); out=Path(output_folder)
    m=json.loads((src/'manifest.json').read_text())
    if m['sourceSha256']!=SOURCE_SHA or m['edition']!='KFGQPC Hafs standard39-2 green PDF':
        raise ValueError('Unverified publisher edition')
    out.mkdir(parents=True,exist_ok=True)
    pages=[]
    for p in m['pages']:
        source=(src/p['filename']).read_bytes()
        if sha(source)!=p['sha256'] or len(source)!=p['bytes']:
            raise ValueError('STOP: original Quran page source failed SHA-256')
        quran_page=p['pdfPage']-3
        if not 1<=quran_page<=604:continue
        im=Image.open(src/p['filename'])
        trimmed,bounds=trim_white_horizontal(im)
        target=out/f'page-{quran_page:04}.webp'
        trimmed.save(target,'WEBP',lossless=True,method=6)
        result=target.read_bytes()
        pages.append({'quranPage':quran_page,'pdfPage':p['pdfPage'],
          'filename':target.name,'sha256':sha(result),'bytes':len(result),
          'height':trimmed.height,'width':trimmed.width,
          'whiteMarginTrimOnly':{'left':bounds[0],'right':im.width-bounds[1]}})
    pages.sort(key=lambda p:p['quranPage'])
    manifest={'version':1,'edition':'KFGQPC Hafs standard39-2 green PDF',
       'riwaya':'Hafs','publisher':'King Fahd Glorious Quran Printing Complex',
       'sourceSha256':SOURCE_SHA,'pageCount':len(pages),'pages':pages,
       'integrity':'Checked input and output SHA-256; only exterior WHITE horizontal columns removed',
       'status':'review-only; not yet full 604-page install'}
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    assert any(p['quranPage']==17 for p in pages)
    print('PASS original full-page Quran proof:',len(pages),'verified files, including page 17, no verses clipped')

if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit('Usage: trim-official-quran-pages.py <verified-source-folder> <output-folder>')
    main(sys.argv[1],sys.argv[2])
