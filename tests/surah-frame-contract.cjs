#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const root=path.resolve(__dirname,'..');
const base=path.join(root,'dist/quran/printed-1441');
const registry=JSON.parse(fs.readFileSync(path.join(base,'surah-title-regions.json'),'utf8'));
const index=JSON.parse(fs.readFileSync(path.join(base,'index.json'),'utf8'));
const manifest=JSON.parse(fs.readFileSync(path.join(base,'manifest.json'),'utf8'));
const quran=fs.readFileSync(path.join(root,'quran-printed-pages.js'),'utf8');
const css=fs.readFileSync(path.join(root,'dist/salati-ui.css'),'utf8');
const svg=fs.readFileSync(path.join(base,'ornaments/user-reference-surah-frame.svg'),'utf8');
assert.equal(registry.count,114,'All 114 chapter beginnings, including 1 and 2, required');
assert.deepEqual(registry.opening_pages,[1,2]);
assert.equal(registry.edition,'Madinah 1441, immutable original plates');
const frames=[1,2];
for(let n=3;n<=604;n++){
 const starts=index.pages[n-1].filter(key=>/^[0-9]+:1$/.test(key)).map(key=>Number(key.split(':')[0]));
 const row=registry.pages[n];
 if(!starts.length){assert.equal(row,undefined,'Unexpected chapter frame on page '+n);continue;}
 assert(row,'Missing heading map for printed page '+n);
 assert.equal(row.headings.length,starts.length,'A chapter heading was missed on page '+n);
 const plate=fs.readFileSync(path.join(base,'pages',n+'.png'));
 assert.equal(crypto.createHash('sha256').update(plate).digest('hex'),manifest.files[n],
  'Authentic Quran artwork must not be rewritten '+n);
 assert.equal(row.width,plate.readUInt32BE(16));
 assert.equal(row.height,plate.readUInt32BE(20));
 let lastEnd=-1;
 for(let i=0;i<starts.length;i++){
  const h=row.headings[i];
  assert.equal(h.surah,starts[i],'Wrong original chapter title at '+n);
  assert(Number.isInteger(h.y)&&Number.isInteger(h.h)&&h.h>=52);
  assert(h.y>=0&&h.y+h.h<=row.height,'Frame outside page '+n);
  assert(h.y>lastEnd,'Overlapping chapter plaques on page '+n);
  lastEnd=h.y+h.h;
  frames.push(h.surah);
 }
}
assert.deepEqual(frames.sort((a,b)=>a-b),Array.from({length:114},(_,i)=>i+1));
assert(quran.includes('function addReferenceSurahFrame('));
assert(quran.includes('node.headings.some((heading,i)=>heading.surah!==starts[i])'));
assert(quran.includes("frame.setAttribute('aria-hidden','true')"));
assert(quran.includes('artwork.append(frame)'));
assert(quran.includes('ink.src=image.src')||quran.includes('ink.src=image.src;'));
assert(css.includes('.printed-reference-surah-decoration'));
assert(css.includes('pointer-events:none;'));
const b64=svg.match(/href="data:image\/png;base64,([^"]+)"/)?.[1];
assert(b64,'Reference ornament must embed exactly one original PNG, not CSS shapes');
const image=Buffer.from(b64,'base64');
assert.equal(image.readUInt32BE(16),282);
assert.equal(image.readUInt32BE(20),39);
assert(image.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10])));
assert(image.length>1000,'Original extracted ornament missing');
console.log('PASS reference banner: 114 complete ordered chapter overlays, original 604 PNG SHA, safe nonoverlapping page geometry, original source artwork');
