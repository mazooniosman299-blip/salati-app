const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('app-source.js','utf8'),start=source.indexOf('function renderCount(){'),end=source.indexOf('\nrenderCities();',start);
const actions=source.slice(source.indexOf("$('counter').onclick="),source.indexOf(";$('privacy').onclick"));
for(const lang of ['ar','en']){
 const nodes=new Map(),$=id=>{if(!nodes.has(id))nodes.set(id,{style:{setProperty(k,v){this[k]=v;}},attributes:{},setAttribute(k,v){this.attributes[k]=v;}});return nodes.get(id);};
 let saves=0;const state={lang,count:0},context={state,$,save(){saves++;},tr:(ar,en)=>lang==='ar'?ar:en};vm.createContext(context);vm.runInContext(source.slice(start,end)+'\n'+actions,context);
 context.renderCount();assert.equal($('tasbihCount').textContent,0);if(lang==='ar')assert.equal($('dhikrLabel').textContent,'سبحان الله');
 for(let n=1;n<=100;n++){$('counter').onclick();assert.equal(state.count,n);assert.equal($('tasbihProgress').attributes['aria-valuenow'],n);assert.equal($('tasbihProgress').style['--progress'],n+'%');assert.equal($('counter').disabled,n===100);if(n===33&&lang==='ar')assert.equal($('dhikrLabel').textContent,'الحمد لله');if(n===66&&lang==='ar')assert.equal($('dhikrLabel').textContent,'الله أكبر');if(n===99)assert.equal($('tasbihDeclaration').hidden,false);}
 $('counter').onclick();assert.equal(state.count,100);$('reset').onclick();assert.equal(state.count,0);assert.equal($('counter').disabled,false);assert.equal($('tasbihDeclaration').hidden,true);assert.equal(saves,102);
}
console.log('PASS: Tasbih preserves all 100 counts, phase changes, progress/ARIA, limit/reset and persistence in both languages.');
