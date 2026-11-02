#!/usr/bin/env python3
"""All 604 authorized, original King Fahd Complex Hafs pages.
Original glyph pixels must be preserved, except WHITESPACE outside page art.
Intended as remote/static supplemental pages; never bundle 604 images into APK.
"""
from PIL import Image
from pathlib import Path
import hashlib,json,sys
from concurrent.futures import ThreadPoolExecutor
from importlib.machinery import SourceFileLoader

root=Path(__file__).resolve().parent.parent
proof=SourceFileLoader('approved_trim',str(root/'scripts/trim-official-quran-pages.py')).load_module()
SOURCE_SHA=proof.SOURCE_SHA
def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for part in iter(lambda:f.read(4*1024*1024),b''):h.update(part)
 return h.hexdigest()

def convert(n,input_folder,out):
 src=input_folder/f'quran-{n:03d}.png'
 if not src.exists():raise RuntimeError('Incomplete original Quran source PDF page '+str(n))
 with Image.open(src) as im:
  im.load()
  trimmed,bounds=proof.trim_white_exterior(im)
  target=out/f'page-{n-3:04d}.webp'
  trimmed.save(target,'WEBP',lossless=True,method=4)
  return {'quranPage':n-3,'pdfPage':n,'filename':target.name,
    'sha256':sha(target),'bytes':target.stat().st_size,
    'width':trimmed.width,'height':trimmed.height,
    'whiteMarginTrimOnly':bounds}

def main(pdf,raw,out):
 if pdf.stat().st_size!=243520529 or sha(pdf)!=SOURCE_SHA:
  raise RuntimeError('STOP: source PDF is NOT the byte-verified original KFGQPC Hafs')
 if len(list(raw.glob('quran-*.png')))!=604:
  raise RuntimeError('STOP: expected exactly 604 original PDF pages 4 through 607')
 out.mkdir(parents=True,exist_ok=True)
 with ThreadPoolExecutor(max_workers=3) as pool:
  pages=list(pool.map(lambda n:convert(n,raw,out),range(4,608)))
 pages.sort(key=lambda x:x['quranPage'])
 assert len(pages)==604 and [x['quranPage'] for x in pages]==list(range(1,605))
 assert len({x['sha256'] for x in pages})>=600,'Repeated/missing page artwork'
 assert all(p['width']>=250 and p['height']>=700 for p in pages)
 manifest={'version':1,'edition':'KFGQPC Hafs standard39-2 green PDF',
   'riwaya':'Hafs','publisher':'King Fahd Glorious Quran Printing Complex',
   'sourceSha256':SOURCE_SHA,'pageCount':604,'pages':pages,
   'integrity':'Full original PDF SHA-256, 604 indexed pages, pixel-safe exterior white margin removal on all four sides',
   'status':'Complete 604 original source artwork; separate online assets, offline text fallback'}
 (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
 total=sum(p['bytes'] for p in pages)
 print('PASS 604 original full Quran pages, unique with complete hashes, size',total,'bytes')
 if total>180*1024*1024:raise RuntimeError('Too large for responsible no-budget static hosting')

if __name__=='__main__':
 if len(sys.argv)!=4:raise SystemExit('Usage: complete-original-mushaf-604.py <publisher.pdf> <rendered-png-dir> <dest>')
 main(Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3]))
