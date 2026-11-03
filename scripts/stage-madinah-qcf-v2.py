#!/usr/bin/env python3
"""Stage the COMPLETE official-style Madinah QCF V2 fonts/pages for a REVIEW BUILD.
Quran words and private-use glyphs come from the published KFGQPC/QUL
v2-15-lines layout mirror, source pinned to commit dad9cf67588ab66c914c155924d8a3699704a03d.
Page fonts come from Quran Foundation's documented QCF V2 CDN, locally bundled
to avoid relying on external access in Android WebView.

The immutable original Tanzil dataset is independently checked against all
6236 verse markers. Never alter the original Quran text or embed generated art.
Never run in production without Quran typography visual QA and approval.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.request import Request,urlopen
from collections import Counter
import json,sys,time,re
ROOT=Path(__file__).resolve().parents[1]
PIN="dad9cf67588ab66c914c155924d8a3699704a03d"
DATA_BASE="https://raw.githubusercontent.com/manaf/KFGQPC-Madinah-Mushaf/"+PIN+"/data/pages/page-{:03d}.json"
FONT_BASE="https://verses.quran.foundation/fonts/quran/hafs/v2/woff2/p{}.woff2"
DEST=ROOT/"dist/quran/qcf-v2"
FONT_DEST=ROOT/"dist/fonts/qcf-v2"
REPORT=ROOT/"reports/madinah-qcf-v2/validation.json"
def download(url,max_bytes=2000000):
    err=None
    for attempt in range(4):
        try:
            with urlopen(Request(url,headers={"User-Agent":"Salati-Quran-Madinah-Preview/1.0"}),timeout=30) as r:
                value=r.read(max_bytes+1)
            if not value or len(value)>max_bytes:raise ValueError("invalid asset size")
            return value
        except Exception as exc:
            err=exc;time.sleep(.4*(attempt+1))
    raise RuntimeError(f"{url}: {err}")
def get_page(n):
    doc=json.loads(download(DATA_BASE.format(n),max_bytes=130000).decode("utf-8"))
    if doc.get("page")!=n or not isinstance(doc.get("lines"),list):
        raise ValueError(f"page schema invalid {n}")
    data=[]
    for row in doc["lines"]:
        typ=row.get("type")
        if typ=="text":
            words=[]
            for w in row.get("words",[]):
                loc=w.get("location");code=w.get("qpcV2")
                if not loc or not re.fullmatch(r"\d{1,3}:\d{1,3}:\d{1,3}",loc):
                    raise ValueError(f"bad word address {n}: {loc}")
                if not code or any(ord(c)<0xE000 for c in code):
                    raise ValueError(f"invalid private-use word glyph {n} {loc}: {code!r}")
                kind=w.get("kind")
                if kind not in ("marker","word"):raise ValueError("unrecognized verse glyph kind")
                words.append([loc,code,1 if kind=="marker" else 0])
            if not words:raise ValueError(f"empty Quran text line {n}")
            data.append(["t",words])
        elif typ=="surah_name":data.append(["h",int((row.get("decor")or{})["surah"])])
        elif typ=="basmallah":data.append(["b"])
        elif typ=="blank":data.append(["_"])
        else:raise ValueError(f"unknown line type {n}: {typ}")
    if len(data)!=15:raise ValueError(f"expected 15 original QCF row slots on page {n}, got {len(data)}")
    return n,data
def get_font(n):
    raw=download(FONT_BASE.format(n),max_bytes=2000000)
    if raw[:4]!=b"wOF2":raise ValueError("not a WOFF2 font file for page "+str(n))
    return n,raw
def main():
    source=json.loads((ROOT/"dist/quran/data.json").read_text())
    verses={(v["s"],v["a"]) for pg in source["pages"] for v in pg}
    assert len(verses)==6236 and len(source["pages"])==604
    DEST.mkdir(parents=True,exist_ok=True);FONT_DEST.mkdir(parents=True,exist_ok=True)
    seen=set();counts=Counter();statuses=[]
    with ThreadPoolExecutor(max_workers=20) as pool:
        tasks={pool.submit(get_page,n):n for n in range(1,605)}
        for future in as_completed(tasks):
            n,lines=future.result()
            for row in lines:
                if row[0]!="t":continue
                for loc,code,marker in row[1]:
                    s,a,_=map(int,loc.split(":"))
                    if (s,a) not in verses:raise ValueError(f"unknown verse key {s}:{a} from QCF {n}")
                    if marker:counts[(s,a)]+=1
            (DEST/f"page-{n:03d}.json").write_text(
                json.dumps({"page":n,"lines":lines},ensure_ascii=False,separators=(",",":"))+"\n")
            statuses.append(n)
    assert len(statuses)==604
    # Every original verse must have exactly one genuine QCF V2 ayah-end marker.
    not_one=[(f"{s}:{a}",counts[(s,a)]) for s,a in verses if counts[(s,a)]!=1]
    if not_one:raise ValueError(f"QCF glyph mapping failed verse marker parity: {not_one[:20]}")
    print("PASS QCF page layout: 604 pages and 6236 exactly matched verse-end markers")
    # Font files are local in the APK. Reproducible only from documented Quran Foundation CDN.
    with ThreadPoolExecutor(max_workers=16) as pool:
        tasks={pool.submit(get_font,n):n for n in range(1,605)}
        for future in as_completed(tasks):
            n,raw=future.result()
            (FONT_DEST/f"p{n}.woff2").write_bytes(raw)
    total_fonts=sum(p.stat().st_size for p in FONT_DEST.glob("p*.woff2"))
    meta={"source":"QCF V2 (Madinah Mushaf)","source_commit":PIN,
          "pages":604,"verses":len(verses),"fonts":604,
          "font_bytes":total_fonts,
          "font_source":"https://verses.quran.foundation/fonts/quran/hafs/v2/woff2/",
          "data_source":"https://github.com/manaf/KFGQPC-Madinah-Mushaf",
          "rights":"KFGQPC copyright; per digital software usage policy at https://dm.qurancomplex.gov.sa/rights/"}
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n")
    (DEST/"MANIFEST.json").write_text(json.dumps(meta,ensure_ascii=False,separators=(",",":"))+"\n")
    print("PASS staged 604 original QCF v2 fonts, bytes:",total_fonts)
    return 0
if __name__=="__main__":
 try:sys.exit(main())
 except Exception as err:
    print("REFUSED QCF typesetting because source/rights/asset parity was not proved:",err,file=sys.stderr)
    sys.exit(2)
