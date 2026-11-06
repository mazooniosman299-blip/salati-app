#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),crypto=require('node:crypto');
const base='dist/quran/printed-1441/';
const files=[
 ['ornaments/user-book-page1.webp','d916bad90d659de4963b690bcf830bb9e4e1f9f65cd1642104619707da14d99c'],
 ['ornaments/user-book-digit-seam.webp','e8b1a7643f2adb2a42951e4f5cf4ec78c193c4497c92d9a369386df643c0eacb']
];
for(const [path,sha] of files){
 const contents=fs.readFileSync(base+path);
 assert.equal(contents.toString('ascii',0,4),'RIFF','Real user screenshot image expected');
 assert.equal(contents.toString('ascii',8,12),'WEBP');
 assert.equal(crypto.createHash('sha256').update(contents).digest('hex'),sha,'No replacement with drawn/guessed artwork');
}
const source=fs.readFileSync('quran-printed-pages.js','utf8');
const style=fs.readFileSync('dist/salati-ui.css','utf8');
const manifest=JSON.parse(fs.readFileSync(base+'manifest.json','utf8'));
const footer=/body\.dark #mushaf\.printed-reader \.original-printed-page \.printed-page-index\{([^}]+)\}/.exec(style);
assert(footer,'Footer scoping must target only actual printed pages');
assert(footer[1].includes('width:56px;height:51px'),'Photo-matched book size was not preserved');
assert(footer[1].includes('pointer-events:none'),'Never steal ayah clicks');
const graphic=/\.printed-page-index::before\{([^}]+)\}/.exec(style);
assert(graphic&&graphic[1].includes('ornaments/user-book-page1.webp'),'Every page must use the exact reference book');
assert(graphic[1].includes('ornaments/user-book-digit-seam.webp'),'Remove only central black ١ from pages 2–604');
assert(!graphic[1].includes('ornaments/user-book-blank.webp'),'No differently reconstructed full-book image');
assert(graphic[1].includes('background-size:13.513514% 43.564356%, 100% 100%;'),'Seam repair must be registered to exact source-image coordinates');
assert(graphic[1].includes('transform:none;'),'Never mirror the exact reference');
const page1=/\.printed-page-index\.printed-reference-page-one::before\{([^}]+)\}/.exec(style);
assert(page1&&page1[1].includes('ornaments/user-book-page1.webp'),'First printed page must show photographed centered ١');
const ink=/\.printed-page-index>\.printed-page-index-digits\{([^}]+)\}/.exec(style);
assert(ink&&ink[1].includes('left:calc(50% + 1.5px);top:39%'),'Optical ink centering measured from genuine screenshot, not guessed CSS box');
assert(ink[1].includes('font:400 20px/1 AmiriQuran,serif'),'Readability at 56x51 folio size');
assert(ink[1].includes('background:transparent;'),'No opaque plaque');
const originalOne=/\.printed-page-index\.printed-reference-page-one>\.printed-page-index-digits\{([^}]+)\}/.exec(style);
assert(originalOne&&originalOne[1].includes('opacity:0;'),'Do not double print page one numeral');
assert(source.includes("if(number===1)label.classList.add('printed-reference-page-one');"));
assert(!source.includes("printed-page-index-single-digit"),'Never shove Arabic ١ to the right again');
assert(source.includes("folioDigits.textContent=String(number).replace(/[0-9]/g,d=>'٠١٢٣٤٥٦٧٨٩'[Number(d)])"),'Keep Eastern-Arabic numerals on all 604 pages');
for(let i=1;i<=604;i++){
 const plate=fs.readFileSync(base+'pages/'+i+'.png');
 assert.equal(crypto.createHash('sha256').update(plate).digest('hex'),manifest.files[i],
  'Source Quran page must never change: '+i);
}
console.log('PASS photo-authentic open-book with true centered ١, 604 untouched plates, correct dynamic Arabic numbers, no mirroring/opaque overlays');
