const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),Module=require('node:module'),esbuild=require('esbuild');
const cities=require('../city-pages/cities.json'),publisher=require('../monetization/web-publisher.json'),origin='https://salati-world-prayer.sprytitan65.chatgpt.site';
const paths=['/','/privacy.html',...['ar','en'].flatMap(l=>[`/${l}/about.html`,`/${l}/prayer-times/index.html`,`/${l}/prayer-times/calculation-guide.html`,...cities.map(c=>`/${l}/prayer-times/${c.slug}.html`)])];
assert.equal(new Set(cities.map(c=>c.slug)).size,cities.length);
for(const pathname of paths){
 const filename='dist'+(pathname==='/'?'/index.html':pathname),html=fs.readFileSync(filename,'utf8');
 assert.equal((html.match(/<h1\b/g)||[]).length,pathname==='/privacy.html'?2:1,filename);
 assert(html.includes(`<meta name="google-adsense-account" content="${publisher.client_id}">`));
 assert(!/adsbygoogle\.js|<ins\b[^>]*adsbygoogle|fundingchoicesmessages\.google/.test(html),'Publisher verification alone must not start advertising');
 const canonical=[...html.matchAll(/rel="canonical" href="([^"]+)"/g)].map(m=>m[1]);assert.deepEqual(canonical,[origin+pathname]);
 const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);assert.equal(ids.length,new Set(ids).size,'Duplicate HTML ID in '+filename);
 if(pathname!=='/'&&pathname!=='/privacy.html'){
  const lang=pathname.split('/')[1],other=lang==='ar'?'en':'ar';
  assert(html.includes(`hreflang="${lang}" href="${origin+pathname}"`));assert(html.includes(`hreflang="${other}" href="${origin+pathname.replace('/'+lang+'/','/'+other+'/')}"`));
  const schema=JSON.parse(html.match(/<script type="application\/ld\+json">(.*?)<\/script>/s)[1]);assert.equal(schema.url,origin+pathname);assert.equal(schema.inLanguage,lang);assert(schema.breadcrumb.itemListElement.length>=2);
  if(pathname.endsWith('/prayer-times/index.html')){assert.equal(schema['@type'],'CollectionPage');assert.equal(schema.mainEntity.itemListElement.length,cities.length);}
  if(cities.some(c=>pathname.endsWith('/'+c.slug+'.html'))){assert.equal((html.match(/id="time-/g)||[]).length,6);assert.equal((html.match(/<time datetime=/g)||[]).length,7);assert(html.includes('id="city-source"'));assert.equal(schema.about['@type'],'Place');}
  for(const match of html.matchAll(/\b(?:href|src)="([^"]+)"/g)){
   if(match[1].startsWith('mailto:'))continue;const u=new URL(match[1].replace(/&amp;/g,'&'),origin+pathname);if(u.origin!==origin)continue;
   const file='dist'+(u.pathname==='/'?'/index.html':u.pathname);assert(fs.existsSync(file),'Missing local asset or link: '+file+' on '+pathname);
  }
 }
}
assert.equal(fs.readFileSync('dist/ads.txt','utf8'),`google.com, ${publisher.publisher_id}, DIRECT, f08c47fec0942fa0\n`);
const robots=fs.readFileSync('dist/robots.txt','utf8');assert(!/Disallow:\s*\/(?:\s|$)/m.test(robots));
const searchModule=new Module('city-search',module);searchModule._compile(esbuild.buildSync({entryPoints:['city-pages/directory-search.js'],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,'city-search.cjs');
const {matchesCitySearch}=searchModule.exports;
assert(matchesCitySearch('ابوظبي','أبوظبي Abu Dhabi'));assert(matchesCitySearch('الْخُرْطُوم','الخرطوم Khartoum'));assert(matchesCitySearch('MUSCAT ','مسقط Muscat'));assert(!matchesCitySearch('London','مسقط Muscat'));
// Exercise the built browser directory with user input, including empty-result recovery.
let onInput;const cards=cities.map(c=>({dataset:{citySearch:[c.ar,c.en,c.countryAr,c.countryEn].join(' ')},hidden:false})),countries=[...new Set(cities.map(c=>c.countryEn))];
const groups=countries.map(country=>({hidden:false,querySelectorAll:()=>cards.filter((card,i)=>cities[i].countryEn===country)}));
const input={value:'',addEventListener:(event,fn)=>{assert.equal(event,'input');onInput=fn;}},status={textContent:''};
const document={documentElement:{lang:'ar'},getElementById:id=>id==='city-search'?input:status,querySelectorAll:selector=>selector==='[data-city-search]'?cards:groups};
vm.runInNewContext(fs.readFileSync('dist/city-directory.js','utf8'),{document,Intl});
for(const [query,count] of [['MUSCAT',1],['ابوظبي',1],['السودان',1],['not-a-real-city',0],['',cities.length]]){input.value=query;onInput();assert.equal(cards.filter(c=>!c.hidden).length,count);assert(status.textContent.endsWith(new Intl.NumberFormat('ar').format(count)));}
assert(groups.every(group=>!group.hidden));
esbuild.transformSync(fs.readFileSync('dist/city-pages.css','utf8'),{loader:'css'}).warnings.forEach(w=>{throw Error(w.text);});
console.log(`PASS: ${paths.length} static pages, unique IDs, reciprocal languages, truthful schema, local links/assets, weekly tables, bilingual city search and publisher verification without ad requests.`);
