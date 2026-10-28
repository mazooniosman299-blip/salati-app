const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('app-source.js','utf8');
const start=source.indexOf('let state='),end=source.indexOf('let audio,',start);
const helper=source.match(/function persistState\(\)\{[\s\S]*?\n\}/)?.[0]||'';
const save=source.match(/const save=\(\)=>\{.*?\};/)[0];
for(const name of ['QuotaExceededError','SecurityError']){
 let unavailable=true,syncs=0,written;const warning={hidden:true,textContent:''};
 const context={saved:{},AUDIO_DEFAULTS:{prayers:{}},restoreLocation:()=>({locationSet:false}),restorePrayerPreferences:()=>({}),applyRequestedMuscatTimes:s=>s,$:()=>warning,localStorage:{setItem(key,value){if(unavailable)throw Object.assign(Error('unavailable'),{name});written=JSON.parse(value);}},queueNativeSync(){syncs++;}};
 vm.createContext(context);
 assert.doesNotThrow(()=>vm.runInContext(helper+'\n'+source.slice(start,end),context),'Startup must survive '+name);
 vm.runInContext(save+'save()',context);assert.equal(syncs,1,'Native alarm synchronization must survive failed web storage');assert.equal(warning.hidden,false);assert(warning.textContent.includes('تعذّر'));
 unavailable=false;vm.runInContext("state.lang='en';save()",context);assert.equal(syncs,2);assert.equal(written.lang,'en');assert.equal(warning.hidden,true);assert.equal(warning.textContent,'');
}
console.log('PASS: startup/settings survive full or blocked storage, expose failure, retain native sync and recover without deleting saved data.');
