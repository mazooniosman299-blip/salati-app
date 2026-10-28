const assert=require('node:assert/strict');const fs=require('node:fs');const crypto=require('node:crypto');
const data=JSON.parse(fs.readFileSync(require('node:path').join(__dirname,'../dist/quran/data.json')));
assert.equal(data.pages.length,604);assert.equal(data.surahs.length,114);const verses=data.pages.flat();assert.equal(verses.length,6236);
let position=0;for(const surah of data.surahs){assert.equal(surah.id,data.surahs.indexOf(surah)+1);for(let a=1;a<=surah.total_verses;a++){const verse=verses[position++];assert.equal(verse.s,surah.id);assert.equal(verse.a,a);assert.ok(verse.t.length>0)}}
for(const [surah,ayah,page]of [[1,1,1],[2,1,2],[2,255,42],[18,1,293],[78,1,582],[114,6,604]])assert.ok(data.pages[page-1].some(v=>v.s===surah&&v.a===ayah));
assert.ok(data.pages.every(p=>p.length>0));assert.match(data.attribution,/Tanzil/);
const digest=crypto.createHash('sha256').update(JSON.stringify(verses.map(v=>[v.s,v.a,v.t]))).digest('hex');
assert.equal(digest,'751a225b945721b972eabef2ccedab2aaea8cd1036f5362d14cb15f26d9c3d77');
// Independently checked against quran-meta 7.0.0 Hafs: every verse's page/juz,
// every page's first/last verse, and every surah's count, starting page and type.
const fingerprint=value=>crypto.createHash('sha256').update(JSON.stringify(value)).digest('hex');
assert.equal(fingerprint(data.pages.map(page=>page.map(v=>[v.s,v.a,v.j]))),'04a31aa44247c4ea5b0d8b12dc61953b06a500bb4183f347a7f8d88bc68f6cdc');
assert.equal(fingerprint(data.surahs.map(s=>[s.id,s.total_verses,s.page,s.type])),'f93e757d727255fca1c4f2652697ca4858bf37ac1db0c2ef1b4d0ff348e37d2e');
console.log('Quran: all 604 page boundaries, 114 surah metadata records, 6236 ordered verses and juz assignments, and unchanged text fingerprint verified.');
