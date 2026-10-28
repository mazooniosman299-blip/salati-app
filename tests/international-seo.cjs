const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const esbuild=require('esbuild');
const html=fs.readFileSync('dist/index.html','utf8');
const context={module:{exports:{}}}; context.exports=context.module.exports;
vm.runInNewContext(esbuild.transformSync(fs.readFileSync('seo-metadata.js','utf8'),{format:'cjs'}).code,context);
const {updateSeoMetadata,SEO_COPY}=context.module.exports;
for(const lang of ['ar','en']){
 const nodes=new Map(); const doc={title:'',querySelector(s){if(!nodes.has(s))nodes.set(s,{});return nodes.get(s)}};
 updateSeoMetadata(lang,doc);
 assert.equal(doc.title,SEO_COPY[lang].title);
 assert.equal(nodes.get('meta[name="description"]').content,SEO_COPY[lang].description);
 assert.equal(nodes.get('meta[property="og:title"]').content,doc.title);
}
assert(!/hreflang=/i.test(html),'No language URLs exist: do not invent alternates');
assert(!/<[^>]+data-ar="[^"]*"[^>]*><\//.test(html),'Initial translation nodes should not be empty');
const schema=JSON.parse(html.match(/<script type="application\/ld\+json">(.*?)<\/script>/s)[1]);
assert.equal(schema['@type'],'WebSite');
assert.deepEqual(schema.inLanguage,['ar','en']);
assert.equal(schema.url,'https://salati-world-prayer.sprytitan65.chatgpt.site/');
assert(!schema.potentialAction,'No fictional site search endpoint');
console.log('PASS: Arabic/English metadata switching; readable static fallback; honest bilingual WebSite schema; no invented hreflang or search endpoint.');
