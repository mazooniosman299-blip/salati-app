#!/usr/bin/env python3
"""Package a complete original printed frame; never draw or repeat a motif."""
from pathlib import Path
import base64,hashlib,json

root=Path(__file__).resolve().parents[1]
reference=root/'design-references/mushaf-frame-20261105'
source=reference/'source-page-564.png'
data=source.read_bytes()
expected='1904db20d73cd1e08fd193397f857f6dd9c83dd7a28d6f2ef99bf45661576b74'
assert hashlib.sha256(data).hexdigest()==expected,'Original printed source changed'
# Geometric exclusion only: current Quran ink comes from the unchanged1441
# plates. Never reuse page564's Quran, header captions, page or hizb numbers.
excluded=[(46,47,530,825),(116,7,96,31),(360,7,156,31),(284,881,49,28),(5,445,34,45)]
mask=''.join(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="black"/>' for x,y,w,h in excluded)
encoded=base64.b64encode(data).decode()
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="622" height="917" viewBox="0 0 622 917"><title>Original printed Madinah frame from QuranHub page564</title><defs><mask id="ornament-only" maskUnits="userSpaceOnUse" x="0" y="0" width="622" height="917"><rect width="622" height="917" fill="white"/>{mask}</mask></defs><image width="622" height="917" href="data:image/png;base64,{encoded}" mask="url(#ornament-only)"/></svg>'''
target=root/'dist/quran/printed-1441/ornaments/authentic-frame.svg'
target.write_text(svg+'\n')
meta={'source':'https://github.com/QuranHub/quran-pages-images/blob/95823e5c5788e150a3f3e89a8536f1bd0c34f2c2/ayat/hafs/564.png','source_sha256':expected,'source_size':[622,917],'source_bytes':len(data),'output':str(target.relative_to(root)),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'method':'Single unchanged original complete printed frame image with geometric exclusions of non-ornamental text/reading area. No new ornamental paths, no repeated pieces, no redrawing. Standard border-image stretch retains existing12/16px layout.','excluded_rectangles':excluded,'licenses':['dist/quran/printed-1441/licenses/QuranHub-LICENSE','dist/quran/printed-1441/licenses/QuranHub-README.md'],'note':'Actual pinned LICENSE is Unlicense; conflicting GPL3 README is retained as well. Not a claim of exact AlMosaly edition.'}
(reference/'SOURCES.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
manifest=root/'dist/quran/printed-1441/ornaments/SOURCES.json'
all_sources=json.loads(manifest.read_text());all_sources['ornaments']['outer_complete_original']=meta;all_sources['hashes']['ornaments/authentic-frame.svg']=meta['sha256'];manifest.write_text(json.dumps(all_sources,ensure_ascii=False,indent=2)+'\n')
print('Packaged complete original frame',meta['sha256'],'no drawn/repeated motifs')
