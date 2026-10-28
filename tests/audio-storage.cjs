const assert=require('node:assert/strict'),Module=require('node:module'),{buildSync}=require('esbuild');
const compiled=new Module(__filename,module);compiled._compile(buildSync({entryPoints:['audio-controller.js'],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,__filename);
const {PrayerAudio,AUDIO_DEFAULTS}=compiled.exports;
const settings={...AUDIO_DEFAULTS,enabled:true};
function create(storage){return new PrayerAudio({getSettings:()=>settings,onState(){},Context:class {},...(storage===undefined?{}:{storage})});}
let failures=[];
for(const failing of ['read','write']){
 try{
 const audio=create({getItem(){if(failing==='read')throw Error('SecurityError');return null;},setItem(){if(failing==='write')throw Error('QuotaExceededError');}});
 audio.armed=true;audio.ctx={state:'running'};let played=0;audio.play=()=>{played++};
 const now=Date.now(),schedule=[{key:'fajr',time:new Date(now)}];
 audio.previous=now-1000;audio.tick(schedule,now,true);assert.equal(played,1,'Storage failure must not suppress adhan');
 audio.previous=now-1000;audio.tick(schedule,now,true);assert.equal(played,1,'Memory must prevent duplicate adhan when storage fails');
 }catch(e){failures.push(failing+': '+e.message);}
}
Object.defineProperty(globalThis,'localStorage',{configurable:true,get(){throw Error('SecurityError');}});
try{assert.doesNotThrow(()=>create());}catch(e){failures.push('blocked storage getter: '+e.message);}finally{delete globalThis.localStorage;}
assert.deepEqual(failures,[]);
console.log('PASS: blocked storage access/read/write preserve adhan startup, playback and duplicate prevention.');
