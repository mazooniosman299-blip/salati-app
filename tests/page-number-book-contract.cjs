#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),crypto=require('node:crypto');
const base='dist/quran/printed-1441/';
const artwork=fs.readFileSync(base+'ornaments/page-book-from-reference.png');
const originalManifest=JSON.parse(fs.readFileSync(base+'manifest.json'));
const source=fs.readFileSync('quran-printed-pages.js','utf8');
const style=fs.readFileSync('dist/salati-ui.css','utf8');
assert.equal(crypto.createHash('sha256').update(artwork).digest('hex'),
 '61ac923fd2845262c336f2dc36f0c1935279a7bf2dd8a95d3b1c4214b55544fa',
 'Exact owner-provided open-book frame must be retained unchanged');
assert.equal(artwork.subarray(0,8).toString('hex'),'89504e470d0a1a0a');
assert.equal(artwork.readUInt32BE(16),63);
assert.equal(artwork.readUInt32BE(20),58);
assert(style.includes('body.dark #mushaf.printed-reader .original-printed-page .printed-page-index{'));
const match=style.match(/body\.dark #mushaf\.printed-reader \.original-printed-page \.printed-page-index\{([^}]+)\}/);
assert(match,'Missing isolated page-bottom-only style');
assert(match[1].includes('page-book-from-reference.png'),'Must use genuine original screenshot-derived book');
assert(match[1].includes('pointer-events:none'),'No disruption to Quran ayah taps');
assert(match[1].includes('color:#241810'),'Keep print digit contrast');
assert(source.includes("label.className='printed-page-index'"));
assert(source.includes("folioDigits.textContent=String(number).replace(/[0-9]/g,d=>'٠١٢٣٤٥٦٧٨٩'[Number(d)])"),'All 604 bottom folios must use Eastern Arabic digits without touching ayah numbering');
assert(source.includes("folioDigits.className='printed-page-index-digits'"),'The folio glyph must be optically centered independent of the book spine');
assert(style.includes('.printed-page-index>.printed-page-index-digits{'),'Only one bottom-folio plaque may be positioned over the book');
assert(match[1].includes('font:400 19px/1 AmiriQuran,serif;'),'Must use the embedded Mushaf-style Amiri Quran font, not Cairo');
assert(source.includes("page.append(label);page.classList.add('original-printed-page')"),'Page footer must remain under real image');
for(let n=1;n<=604;n++){
 const original=fs.readFileSync(base+'pages/'+n+'.png');
 assert.equal(crypto.createHash('sha256').update(original).digest('hex'),originalManifest.files[n],
  'Never alter the original Quran plate '+n);
}
console.log('PASS user open-book page number: all 604 original pages unchanged; Arabic digits remain dynamic; isolated bottom-only art; exact image checksum');
