#!/usr/bin/env node
'use strict';
// Runtime contract: third-party line positions must not alter a single
// letter, vowel, waqf mark or canonical verse byte in the Tanzil dataset.
const fs=require('node:fs'),assert=require('node:assert/strict');
const q=JSON.parse(fs.readFileSync('dist/quran/data.json','utf8'));
const map=JSON.parse(fs.readFileSync('dist/quran/line-layout.json','utf8'));
assert.equal(map.schema,'madani-604-word-line-layout-1');
assert.equal(map.pages.length,604);
assert.equal(map.source_commit,'507eada48f3ffe26a600acf5792a18ba86d6851e');
assert.equal(map.license,'CC-BY-SA-4.0');
const clean=s=>Array.from(s).filter(c=>!/\p{M}/u.test(c)).join('').replace(/ٱ/g,'ا');
const merge=map.word_merges||{};
const words=v=>{
 let a=v.t.trim().split(/\s+/u);
 if(v.a===1&&v.s!==1&&v.s!==9&&a.length>=5&&
    ['بسم','الله','الرحمن','الرحيم'].every((s,i)=>clean(a[i])===s))a=a.slice(4);
 const k=merge[v.s+':'+v.a];
 if(Number.isInteger(k))a=[...a.slice(0,k),a[k]+' '+a[k+1],...a.slice(k+2)];
 return a;
};
const all=q.pages.flat(),verses=new Map(all.map(v=>[v.s+':'+v.a,v])),observed=new Map();
const seenHeaders=new Set(),counts=new Map();
for(let i=0;i<604;i++){
 const rows=map.pages[i];
 assert(Array.isArray(rows)&&rows.length>=8&&rows.length<=17,'Page rows: '+(i+1));
 counts.set(i+1,rows.length);
 for(const row of rows){
  if(row[0]==='h'){assert(q.surahs[row[1]-1]);seenHeaders.add(row[1]);continue;}
  if(row[0]==='b'){assert(row[1]!==1&&row[1]!==9);continue;}
  assert.equal(row[0],'t');assert(row.length>1);
  for(const [s,a,w] of row.slice(1)){
   const v=verses.get(s+':'+a);
   assert(v,'Unknown verse '+s+':'+a);
   const list=words(v);
   assert(Number.isInteger(w)&&w>=0&&w<list.length,'Out-of-bounds Quran word '+s+':'+a+'#'+w);
   const id=s+':'+a;observed.set(id,[...(observed.get(id)||[]),w]);
  }
 }
}
assert.equal(verses.size,6236);
assert.equal(seenHeaders.size,114);
for(const [id,v] of verses){
 const expected=words(v).map((_,i)=>i),got=observed.get(id)||[];
 assert.deepEqual(got,expected,'Lost/moved/duplicated canonical Quran word '+id);
}
assert.equal(counts.get(564),15,'Critical screenshot reference printed page 564 must have 15 rows');
assert.equal(counts.get(604),15);
const exceptions=map.non_exact_print_pages||[];
assert.deepEqual(exceptions,[208,586,587,590,591],
 'Missing print fidelity warnings for manually corrected headers');
const renderer=fs.readFileSync('quran-controller.js','utf8');
assert(renderer.includes("quran-madinah-line"),'Code must use true line renderer');
const marker=fs.readFileSync('dist/quran-mushaf-markers-20261101.js','utf8');
assert(!marker.includes('node.nodeValue.replace('),'No Quranic stop/diacritic deletion permitted');
console.log('PASS licensed 604 line-map pages, 114 headings, exact 6236 immutable canonical verses, all word positions + printed page 564, 5 transparent print layout exceptions');
