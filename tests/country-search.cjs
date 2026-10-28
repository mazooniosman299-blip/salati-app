const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),Module=require('node:module'),esbuild=require('esbuild');
const {Node,makeDocument}=require('./quran-dom.cjs');
function load(file){const m=new Module(file,module);m._compile(esbuild.buildSync({entryPoints:[file],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,file);return m.exports;}
const {WORLD_COUNTRIES,countryOption}=load('world-directory.js'),{choiceMatches}=load('choice-picker.js');
const previous=global.Option;
try{
 global.Option=function(text,value){const node=new Node(1,'option');node.textContent=text;node.value=value;return node;};
 for(const lang of ['ar','en']){
  const options=WORLD_COUNTRIES.map(c=>countryOption(c,lang));assert.equal(options.length,250);
  for(const country of WORLD_COUNTRIES){const option=options.find(o=>o.value===country.code);for(const query of [country.ar,country.en,country.code])assert(choiceMatches(option,query),country.code+' / '+query);assert.equal(option.textContent,country[lang]);assert.equal(option.dataset.subtitle,country[lang==='ar'?'en':'ar']);}
  for(const [code,query] of [['GB','بريطانيا'],['GB','UK'],['US','أمريكا'],['US','USA'],['AE','الإمارات'],['AE','UAE'],['SA','المملكه العربيه السعوديه'],['MM','ميانمار'],['SZ','إسواتيني'],['BY','بيلاروس'],['CZ','Czechia'],['TR','Turkey'],['OM','عُمان'],['DE','أَلْـمَانِيَا'],['PS','Palestine'],['SD','Sudan'],['SS','جنوب السودان'],['XK','Kosova']])assert(choiceMatches(options.find(o=>o.value===code),query),code+' / '+query);
  const select=new Node(1,'select');select.id='country';select.append(...options);select.dispatchEvent=()=>{};
  const document=makeDocument(),list=new Node(1,'div'),count=new Node(1,'small'),search={value:''};
  const source=fs.readFileSync('choice-picker.js','utf8');const fn=source.slice(source.indexOf('function renderList(){'),source.indexOf('export function setupChoicePickers'));
  let closed=false;const context={active:select,search,list,count,document,language:()=>lang,choiceMatches,Event,refreshChoicePickers:()=>{},dialog:{close:()=>{closed=true;}}};vm.runInNewContext(fn+';globalThis.render=renderList;',context);
  context.render();assert.equal(list.querySelectorAll('button').length,250);assert.equal(new Set(list.querySelectorAll('button').map(b=>b.dataset.value)).size,250);assert.equal(list.querySelectorAll('small').length,250);
  search.value='بريطانيا';context.render();const british=list.querySelectorAll('button').find(b=>b.dataset.value==='GB');assert(british);british.onclick();assert.equal(select.value,'GB');assert(closed);
  search.value='country-that-does-not-exist';context.render();assert.equal(list.querySelectorAll('button').length,0);
  select.id='city';select.replaceChildren(...Array.from({length:300},(_,i)=>new global.Option('City '+i,String(i))));search.value='';context.render();assert.equal(list.querySelectorAll('button').length,200);search.value='City 299';context.render();assert.equal(list.querySelectorAll('button').length,1);assert.equal(list.children[0].dataset.value,'299');
 }
 assert(!choiceMatches({textContent:'Sudan',dataset:{}},'South Sudan'));assert(choiceMatches({textContent:'البقرة',dataset:{}},'البقره'));
 console.log('PASS: all 250 locations displayed in both languages; bilingual names, common aliases and codes searchable; selecting a match retains its country code; city search reaches results beyond the first 200.');
}finally{global.Option=previous;}
