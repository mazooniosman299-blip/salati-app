'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {validateManifest,verifyPlate,gitBlobSha1}=require('../scripts/verify-kfqc-mushaf-source.cjs');
const m=JSON.parse(fs.readFileSync('reference-data/kfqc-hafs-604-plate-manifest.json','utf8'));
assert.equal(validateManifest(m),true);
assert.equal(m.pages.length,604);
assert.equal(m.pages[11].page,12);
assert.match(m.source.revision,/^[a-f0-9]{40}$/);
assert.match(m.source.license,/qurancomplex\.gov\.sa\/rights/);
assert.match(gitBlobSha1(Buffer.from('hello')),/^[a-f0-9]{40}$/);
for(const mutate of [
 o=>{o.pages.pop();},
 o=>{o.pages[11].page=13;},
 o=>{o.pages[0].gitBlobSha1='0'.repeat(40);}, // SHA format passes; content verification must reject.
 o=>{o.pages[0].path='../malicious.svg';},
 o=>{o.source.revision='main';},
 o=>{o.source.license='https://unknown.invalid';}
]){
 const bad=structuredClone(m);
 mutate(bad);
 if(bad.pages.length!==604||bad.pages[11]?.page!==12||
    bad.pages[0]?.path!==m.pages[0].path||bad.source.revision!==m.source.revision||
    bad.source.license!==m.source.license){
    assert.throws(()=>validateManifest(bad));
 }else{
    assert(validateManifest(bad)); // malformed but syntactically plausible hashes need byte check
    assert.throws(()=>verifyPlate(Buffer.from('<svg xmlns="http://www.w3.org/2000/svg"></svg>'),bad.pages[0]));
 }
}
const empty=Buffer.from('<svg xmlns="http://www.w3.org/2000/svg"></svg>');
assert.throws(()=>verifyPlate(empty,m.pages[0]),/Plate bytes differ/);
const html=fs.readFileSync('dist/index.html','utf8');
assert(html.includes('id="qVerses"')&&html.includes('id="mushafPlayerSlot"'));
assert(!html.includes('mushaf-source-preview'), 'No unapproved print-plate demo may replace the current Quran UI');
console.log('PASS KFQC original 604-page manifest, pinned blob IDs, tamper/missing/reorder tests; style #5 not falsely approved');
