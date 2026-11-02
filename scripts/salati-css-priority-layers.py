#!/usr/bin/env python3
"""Experimental priority-to-layer migration, with pixel/computed-style gates.

Original author-important declarations and normal declarations become two
explicit cascade layers. This preserves selector specificity and relative
source order *within* each priority level, but inline author styles, animations
and external sheets can still change outcomes. NEVER ship without Chromium
computed-style parity AND native Android WebView validation.
"""
from pathlib import Path
from collections import Counter
import json,re,hashlib,tinycss2

root=Path(__file__).resolve().parents[1]
path=root/"dist/salati-ui.css"
source=path.read_text(encoding="utf8")
assert not re.search(r"(?m)^\s*@(?:import|charset|layer)\b",source), "Already layered/imported source requires manual audit"
stats=Counter()

def split(nodes):
    normal=[]
    priority=[]
    for n in nodes:
        if n.type=="qualified-rule":
            selector=tinycss2.serialize(n.prelude)
            decls=tinycss2.parse_declaration_list(n.content,skip_comments=False,skip_whitespace=False)
            assert not any(d.type=="error" for d in decls),("Unparseable CSS rule",selector)
            ordinary=[]
            strong=[]
            for d in decls:
                if d.type!="declaration":
                    assert d.type in ("comment","whitespace"),("Unexpected rule nesting",selector,d.type)
                    continue
                serialized=d.name+":"+tinycss2.serialize(d.value).strip()+";"
                if d.important:
                    strong.append(serialized)
                    stats["migrated_flags"]+=1
                else:
                    ordinary.append(serialized)
                stats["declarations"]+=1
            if ordinary:
                normal.append(selector+"{"+"".join(ordinary)+"}")
            if strong:
                priority.append(selector+"{"+"".join(strong)+"}")
        elif n.type=="at-rule" and n.content is not None and n.lower_at_keyword in ("media","supports","container"):
            lo,hi=split(tinycss2.parse_rule_list(n.content))
            pre="@"+n.at_keyword+" "+tinycss2.serialize(n.prelude)
            if lo:normal.append(pre+"{"+lo+"}")
            if hi:priority.append(pre+"{"+hi+"}")
        else:
            # Keep fonts, keyframes, counter styles, font-face and top-level
            # at-rules intact. These do not participate in the author cascade
            # like individual style declarations.
            raw=tinycss2.serialize([n])
            assert not re.search(r"!\s*important\b",raw,re.I),("Unmapped priority in at-rule",raw[:80])
            normal.append(raw)
    return "".join(normal),"".join(priority)

ast=tinycss2.parse_stylesheet(source,skip_whitespace=False,skip_comments=False)
assert not any(x.type=="error" for x in ast)
lo,hi=split(ast)
assert stats["migrated_flags"]==len(re.findall(r"!\s*important\b",source,re.I))
layered="@layer salati-base,salati-priority;\n@layer salati-base{"+lo+"}\n@layer salati-priority{"+hi+"}"
assert not re.search(r"!\s*important\b",layered,re.I)
assert not any(x.type=="error" for x in tinycss2.parse_stylesheet(layered))
(path.parent/"salati-ui-baseline.css").write_text(source,encoding="utf8")
path.write_text(layered,encoding="utf8")
report={"source_important":stats["migrated_flags"],"layered_important":0,
        "declarations":stats["declarations"],"old_bytes":len(source.encode()),
        "new_bytes":len(layered.encode()),"sha256":hashlib.sha256(layered.encode()).hexdigest(),
        "required_gates":["computed style parity 6 tabs x 6 widths","real native Android screenshot QA"]}
(root/"reports").mkdir(exist_ok=True)
(root/"reports/css-layered-experiment-20261102.json").write_text(json.dumps(report,indent=2))
print("EXPERIMENT ONLY — author-important migrated to 2 cascade layers",report)
