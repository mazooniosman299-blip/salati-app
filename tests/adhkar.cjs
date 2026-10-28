const assert=require('node:assert/strict'),fs=require('node:fs'),Module=require('node:module'),esbuild=require('esbuild');
const {Node,makeDocument}=require('./quran-dom.cjs'),collection=require('../adhkar-collection.json');
const compiled=new Module('adhkar-test',module);compiled._compile(esbuild.buildSync({entryPoints:['adhkar-controller.js'],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,'adhkar-test.cjs');
const {filterAdhkar,repetitionFor,AdhkarProgress,setupAdhkar}=compiled.exports;
assert.equal(collection.version,1);assert(collection.items.length>=65);assert.equal(collection.categories.length,14);
const categories=new Set(collection.categories.map(c=>c.id)),ids=new Set(),texts=new Set();
const normalize=text=>text.normalize('NFKD').replace(/[\u0300-\u036f\u064b-\u065f\u0670\u0640]/g,'').replace(/\s+/g,' ').trim();
for(const item of collection.items){
 assert.match(item.id,/^[a-z][a-z0-9-]+$/);assert(!ids.has(item.id));ids.add(item.id);
 assert(item.titleAr&&item.titleEn&&item.text.trim()===item.text&&item.text.length>0);const normalized=normalize(item.text);assert(!texts.has(normalized),'Duplicate dhikr: '+item.id);texts.add(normalized);
 assert(Array.isArray(item.categories)&&item.categories.length);for(const c of item.categories)assert(categories.has(c),c);
 assert(item.repeat===null||Number.isInteger(item.repeat)&&item.repeat>0&&item.repeat<=1000);
 for(const [category,value]of Object.entries(item.repeatByCategory||{})){assert(item.categories.includes(category));assert(value===null||Number.isInteger(value)&&value>0&&value<=1000);}
 for(const source of [item.source,...(item.sources||[])]){assert(source.label.trim());const url=new URL(source.url);assert.equal(url.protocol,'https:');assert(['sunnah.com','hadeethenc.com','dorar.net','risala.prh.gov.sa','binbaz.org.sa','hadithm6.ma'].includes(url.hostname));assert(!url.pathname.includes('/search'));}
}
for(const category of collection.categories){assert(category.ar&&category.en);assert(filterAdhkar(category.id,'').length>0,category.id);}
// Reviewed contextual counts must not leak into another occasion.
for(const [id,category,count]of [['name-no-harm','morning',3],['glory-and-praise','evening',100],['glory-number-creation','morning',3],['after-prayer-forgiveness','after-prayer',3],['tasbih','after-prayer',33],['tasbih','travel',null],['tahmid','sleep',33],['tahmid','general',null],['takbir','after-prayer',33],['takbir','sleep',34],['takbir','travel',null],['oneness-declaration','morning',100],['oneness-declaration','after-prayer',1],['surah-ikhlas','morning',3],['surah-ikhlas','after-prayer',null],['illness-site-of-pain','illness',7],['illness-visiting-seven','illness',7],['weather-seeking-rain','weather',3]])assert.equal(repetitionFor(collection.items.find(item=>item.id===id),category),count,id+' / '+category);
const quran=JSON.parse(fs.readFileSync('dist/quran/data.json','utf8')),verses=quran.pages.flat();
for(const [id,surah]of [['surah-ikhlas',112],['surah-falaq',113],['surah-nas',114],['surah-kafirun',109]])assert.equal(collection.items.find(item=>item.id===id).text,verses.filter(v=>v.s===surah).map(v=>v.t).join('\n'));
assert.equal(collection.items.find(item=>item.id==='ayat-kursi').text,verses.find(v=>v.s===2&&v.a===255).t);
assert.equal(collection.items.find(item=>item.id==='baqarah-final-verses').text,verses.filter(v=>v.s===2&&v.a>=285).map(v=>v.t).join('\n'));
assert.equal(filterAdhkar('','').length,collection.items.length);assert(filterAdhkar('morning','').some(item=>item.text.includes('أصبح')||item.text.includes('أَصْبَح')));assert(filterAdhkar('','الصباح').length>0);assert.equal(filterAdhkar('','no-matching-dhikr-12345').length,0);
const storageData=new Map(),storage={getItem:key=>storageData.get(key)||null,setItem:(key,value)=>storageData.set(key,value)};let day='2026-10-23';const progress=new AdhkarProgress({storage,day:()=>day});
const contextual={id:'contextual-test',repeat:null,repeatByCategory:{morning:3,evening:3,'after-prayer':null}};
assert.equal(repetitionFor(contextual,'morning'),3);assert.equal(repetitionFor(contextual,'after-prayer'),null);assert.equal(repetitionFor(contextual,''),null);
for(let i=0;i<8;i++)progress.increment(contextual,'morning');assert.equal(progress.value(contextual,'morning'),3);assert.equal(progress.value(contextual,'evening'),0);
const restored=new AdhkarProgress({storage,day:()=>day});assert.equal(restored.value(contextual,'morning'),3);restored.reset([contextual],'morning');assert.equal(restored.value(contextual,'morning'),0);
progress.increment(contextual,'evening');day='2026-10-24';assert.equal(progress.increment(contextual,'morning'),1);assert.equal(progress.value(contextual,'evening'),0);assert.equal(new AdhkarProgress({storage,day:()=>day}).value(contextual,'morning'),1);
const bad=new AdhkarProgress({storage:{getItem:()=>'{broken',setItem:()=>{throw Error('quota');}},day:()=>day});assert.equal(bad.increment(contextual,'morning'),1);
const old={document:global.document,Option:global.Option,localStorage:global.localStorage,navigator:global.navigator};
(async()=>{try{
 const document=makeDocument(),create=document.createElement;document.createElement=tag=>{const element=create(tag);element.classList.toggle=(name,force)=>{if(force)element.classList.add(name);else element.classList.remove(name);return !!force;};return element;};
 global.document=document;global.Option=function(text,value){const node=new Node(1,'option');node.textContent=text;node.value=value;return node;};global.localStorage=storage;
 const shortcuts=document.getElementById('adhkarShortcuts');for(const category of ['morning','evening','after-prayer','sleep']){const button=new Node(1,'button');button.dataset.adhkarCategory=category;shortcuts.append(button);}
 let lang='ar',copied='';Object.defineProperty(global,'navigator',{configurable:true,value:{clipboard:{writeText:async value=>{copied=value;}}}});
 const ui=setupAdhkar({getLang:()=>lang}),list=document.getElementById('adhkarList'),category=document.getElementById('adhkarCategory'),search=document.getElementById('adhkarSearch');
 assert.equal(category.value,'morning');assert.equal(list.children.length,filterAdhkar('morning','').length);
 const card=list.children.find(card=>repetitionFor(collection.items.find(item=>item.id===card.dataset.adhkar),'morning')>1);assert(card);const counter=card.querySelector('.adhkar-counter'),reset=card.querySelector('.adhkar-reset'),item=collection.items.find(item=>item.id===card.dataset.adhkar);
 assert(!counter.disabled);counter.onclick();assert(counter.textContent.includes(new Intl.NumberFormat('ar').format(1)));reset.onclick();assert(counter.textContent.includes(new Intl.NumberFormat('ar').format(0)));
 const copyButton=card.querySelector('.adhkar-actions').querySelectorAll('button').find(button=>button.textContent==='نسخ');await copyButton.onclick();assert(copied.startsWith(item.text+'\n'));assert(copied.includes(item.source.label));
 shortcuts.children[1].onclick();assert.equal(category.value,'evening');assert.equal(search.value,'');assert.equal(list.children.length,filterAdhkar('evening','').length);
 lang='en';ui.refresh();assert.equal(category.value,'evening');assert.equal(search.placeholder,'Search adhkar…');
 search.value='no-matching-dhikr-12345';search.oninput();assert.equal(list.querySelectorAll('article').length,0);assert(document.getElementById('adhkarReset').disabled);
 const html=fs.readFileSync('dist/index.html','utf8');assert(html.includes('الأذكار اليومية'));assert(!html.includes('أدعية من القرآن الكريم'));assert(!html.includes('duaCategory'));assert(html.includes('data-ar="الموقع"'));
 console.log(`PASS: ${collection.items.length} distinct daily adhkar in 14 categories, source links and repetition metadata, Arabic search, category counters, persistence, daily reset, malformed storage, displayed text/copy and old Quran-only library replacement.`);
}finally{for(const [key,value]of Object.entries(old)){if(key==='navigator')Object.defineProperty(global,key,{configurable:true,value});else global[key]=value;}}})().catch(error=>{console.error(error);process.exitCode=1;});
