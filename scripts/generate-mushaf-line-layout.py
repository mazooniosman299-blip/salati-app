#!/usr/bin/env python3
"""Compile licensed Madani line positions without copying Quran text.
Display words are ALWAYS read from immutable dist/quran/data.json.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter, defaultdict
from pathlib import Path
from urllib.request import Request, urlopen
import json, sys, time
ROOT=Path(__file__).resolve().parents[1]
PIN="507eada48f3ffe26a600acf5792a18ba86d6851e"
BASMALA="بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ"
URL="https://raw.githubusercontent.com/ouryhamdalaye/madinah-mushaf-json/"+PIN+"/pages/page-{:03d}.json"
OUT=ROOT/"dist/quran/line-layout.json"
REPORT=ROOT/"reports/quran-line-layout/validation.json"
def canonical_words(v):
    t=v["t"]
    if v["a"]==1 and v["s"] not in (1,9) and t.startswith(BASMALA+" "):
        t=t[len(BASMALA)+1:]
    return t.split()
def get_page(n):
    err=None
    for attempt in range(4):
        try:
            with urlopen(Request(URL.format(n),headers={"User-Agent":"salati-verified-mushaf-layout/1.0"}),timeout=25) as f:
                d=json.loads(f.read(120000))
            if d.get("page")!=n or not isinstance(d.get("lines"),list):
                raise ValueError("Invalid page schema")
            return n,d
        except Exception as e:
            err=e;time.sleep(.6*(attempt+1))
    raise RuntimeError(f"upstream page {n}: {err}")
def main():
    original=json.loads((ROOT/"dist/quran/data.json").read_text())
    assert len(original["pages"])==604 and len(original["surahs"])==114
    verses={(v["s"],v["a"]):v for page in original["pages"] for v in page}
    assert len(verses)==6236
    fetched=[None]*604
    with ThreadPoolExecutor(max_workers=16) as pool:
        futures={pool.submit(get_page,n):n for n in range(1,605)}
        for f in as_completed(futures):
            n,d=f.result();fetched[n-1]=d
    lines=[];observed=defaultdict(list);bad=[];headings=0
    for n,d in enumerate(fetched,1):
        page=[]
        for line in d["lines"]:
            typ=line.get("type")
            if typ=="ayah-line":
                tokens=[]
                for w in line.get("tokens",[]):
                    s,a,k=int(w["s"]),int(w["a"]),int(w["w"])
                    if (s,a) not in verses or k<0:bad.append(f"invalid address p{n}: {s}:{a}:{k}")
                    observed[(s,a)].append(k);tokens.append([s,a,k])
                if not tokens:bad.append(f"empty ayah line on p{n}")
                page.append(["t",*tokens])
            elif typ=="surah-header":
                headings+=1;page.append(["h",None])
            elif typ=="basmala":page.append(["b",None])
            else:bad.append(f"unknown line type p{n}: {typ}")
        lines.append(page)
    # Resolve surah name slots using the NEXT word on this or the next leaf.
    next_s=None
    for page in reversed(lines):
        for row in reversed(page):
            if row[0]=="t":next_s=row[1][0]
            elif row[0] in ("h","b"):
                if not next_s:bad.append("surah heading lacking a following ayah")
                else:row[1]=next_s
    # Additional bismillah row uses only the corresponding original Tanzil
    # verse prefix, never 3rd-party textual content.
    pending=[]
    for n,page in enumerate(lines):
        output=[]
        for row in page:
            if row[0]=="h":
                output.append(row)
                if row[1] not in (1,9):pending.append(row[1])
                continue
            if row[0]=="t" and pending:
                output.extend(["b",s] for s in pending);pending=[]
            output.append(row)
        lines[n]=output
    if pending:bad.append(f"unplaced bismillah {pending}")
    wrong_lines=[(p+1,len(page)) for p,page in enumerate(lines) if len(page)!=(8 if p<2 else 15)]
    mismatched=[]
    for key,v in verses.items():
        expected=list(range(len(canonical_words(v))))
        if observed.get(key)!=expected:
            mismatched.append((f"{key[0]}:{key[1]}",len(expected),len(observed.get(key,[])),observed.get(key,[])[:18]))
    report={"upstream_commit":PIN,"license":"CC-BY-SA-4.0",
      "page_count":len(lines),"surah_headers":headings,
      "line_lengths":dict(Counter(map(len,lines))),
      "bad_line_pages":wrong_lines[:70],"mismatched_verses":len(mismatched),
      "mismatch_sample":mismatched[:45],"schema_errors":bad[:50]}
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print("MADANI_LAYOUT_CHECK:",json.dumps({k:v for k,v in report.items() if k not in ("mismatch_sample","schema_errors")},ensure_ascii=False))
    print("SAMPLE_ERRORS:",json.dumps({"mismatches":mismatched[:12],"bad":bad[:8]},ensure_ascii=False))
    if bad or wrong_lines or mismatched or headings!=114:
        print("REFUSED: layout has not passed every source word and 15-line page check",file=sys.stderr)
        return 2
    payload={"schema":"madani-604-word-line-layout-1","source_commit":PIN,
      "license":"CC-BY-SA-4.0","attribution":"https://github.com/ouryhamdalaye/madinah-mushaf-json",
      "pages":lines}
    OUT.write_text(json.dumps(payload,ensure_ascii=False,separators=(",",":"))+"\n")
    print("PASS 604 pages / 6236 verses / all words accounted for; JSON",OUT.stat().st_size,"bytes")
    return 0
if __name__=="__main__":sys.exit(main())
