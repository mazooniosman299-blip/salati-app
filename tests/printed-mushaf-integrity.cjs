const assert=require('node:assert/strict'),fs=require('node:fs'),crypto=require('node:crypto');
const base='dist/quran/printed-1441/',manifest=JSON.parse(fs.readFileSync(base+'manifest.json')),data=JSON.parse(fs.readFileSync('dist/quran/data.json')),seen=new Set();
assert.equal(manifest.images_bundled,604);assert.equal(Object.keys(manifest.files).length,604);
for(let n=1;n<=604;n++){
 const image=fs.readFileSync(base+'pages/'+n+'.png'),regions=JSON.parse(fs.readFileSync(base+'regions/'+n+'.json'));
 assert.equal(crypto.createHash('sha256').update(image).digest('hex'),manifest.files[n]);
 assert.equal(image.readUInt32BE(16),regions.width);assert.equal(image.readUInt32BE(20),regions.height);
 assert.equal(regions.page,n);assert.equal(regions.transform.length,6);assert(regions.transform.every(Number.isFinite));
 const expected=JSON.parse(fs.readFileSync(base+'index.json')).pages[n-1];
 assert.deepEqual(regions.verses.map(v=>v.key),expected,'Artwork targets must match canonical page '+n);
 for(const row of regions.verses){assert(!seen.has(row.key));seen.add(row.key);assert(/^[MLZmlz0-9.,\s-]+$/.test(row.path));}
}
assert.equal(seen.size,6236);assert.deepEqual([...seen],data.pages.flat().map(v=>v.s+':'+v.a),'Every original canonical ayah occurs once, in the same order; printed edition pagination is distinct from old text pagination');for(const file of ['QuranWS-NOTICE.md','QuranWS-LICENSE.txt','CC-BY-4.0.txt'])assert(fs.statSync(base+'licenses/'+file).size>500);
require('./quran.cjs');console.log('PASS printed Mushaf: 604 original image hashes/dimensions, 6236 canonical page-aligned regions, publisher/metadata notices and unchanged Quran text');
