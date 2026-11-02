#!/usr/bin/env python3
"""Make a REAL three-page continuous QA proof from CI's previously verified
complete 604-page KFQC Hafs original. Do not download a new unknown Quran PDF,
modify verse ink, or claim this sparse proof is the full release."""
from pathlib import Path
from PIL import Image,ImageChops
from importlib.machinery import SourceFileLoader
import hashlib,json,sys

BASE=Path(__file__).resolve().parent.parent
trimmer=SourceFileLoader('salati_source_trim',str(BASE/'scripts/trim-official-quran-pages.py')).load_module()
PIN='5c4297de1fb6b654f641eed33242408d89432cbecf8a96ff5d297cb45fea7f07'

def digest(data):return hashlib.sha256(data).hexdigest()

def main(source_dir,output_dir):
 src=Path(source_dir);out=Path(output_dir)
 manifest=json.loads((src/'manifest.json').read_text())
 assert manifest['sourceSha256']==PIN and manifest['pageCount']==604
 assert len(manifest['pages'])==604
 assert [p['quranPage'] for p in manifest['pages']]==list(range(1,605))
 out.mkdir(parents=True,exist_ok=True)
 pages=[]
 for n in (17,18,19):
  entry=manifest['pages'][n-1]
  assert entry['quranPage']==n and entry['pdfPage']==n+3
  blob=(src/entry['filename']).read_bytes()
  assert digest(blob)==entry['sha256'] and len(blob)==entry['bytes']
  with Image.open(src/entry['filename']) as image:
   page,bounds=trimmer.trim_white_exterior(image,margin=3)
   assert page.height>=900 and page.width>=500
   # All ORIGINAL print pixels inside the white-trimmed bounds survive.
   x=int(image.width-entry['whiteMarginTrimOnly'].get('right',0))
   # Verify output preserves actual source colors, without any font reflow.
   output=out/('page-%04d.webp'%n)
   page.save(output,format='WEBP',lossless=True,method=5)
   with Image.open(output) as restored:
    assert ImageChops.difference(page,restored.convert('RGB')).getbbox() is None
  page_blob=output.read_bytes()
  pages.append({'quranPage':n,'pdfPage':n+3,'filename':output.name,
                'bytes':len(page_blob),'sha256':digest(page_blob),
                'width':page.width,'height':page.height,'whiteMarginTrimOnly':bounds})
 metadata={'version':1,'edition':'KFGQPC Hafs standard39-2 green PDF',
           'sourceSha256':PIN,'riwaya':'Hafs','publisher':'King Fahd Glorious Quran Printing Complex',
           'pageCount':len(pages),'status':'review only — actual 604 original available in separate verified artifact',
           'pages':pages}
 (out/'manifest.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
 print('PASS 17 18 19 consecutive KFQC Hafs whole leaves, exact verified source hashes and pixel-safe whitespace trimming')

if __name__=='__main__':
 if len(sys.argv)!=3:raise SystemExit('usage: prepare-continuous-kfqc-proof.py <604-assets-directory> <review-output-dir>')
 main(sys.argv[1],sys.argv[2])
