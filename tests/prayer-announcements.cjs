const assert=require('node:assert/strict'),Module=require('node:module'),{buildSync}=require('esbuild');
const compiled=new Module(__filename,module);compiled._compile(buildSync({entryPoints:['prayer-announcements.js'],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,__filename);
const {PrayerAnnouncements}=compiled.exports;
const audioModule=new Module(__filename,module);audioModule._compile(buildSync({entryPoints:['audio-controller.js'],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,__filename);
const {PrayerAudio,AUDIO_DEFAULTS}=audioModule.exports;
const flush=async()=>{for(let i=0;i<8;i++)await Promise.resolve()};
function fixture({voices=[{lang:'ar-SA',localService:true}],storage={getItem(){throw Error('blocked')},setItem(){throw Error('blocked')}}}={}){
 let now=0,next=0;const timers=new Map(),listeners=new Set(),spoken=[],settings={...AUDIO_DEFAULTS,enabled:true},speech={getVoices:()=>voices,speaking:false,pending:false,cancelled:0,addEventListener:(event,fn)=>listeners.add(fn),removeEventListener:(event,fn)=>listeners.delete(fn),speak:u=>spoken.push(u),cancel(){this.cancelled++}};
 const controller=new PrayerAnnouncements({getSettings:()=>settings,storage,speech,Utterance:class{constructor(text){this.text=text}},now:()=>now,setTimer:(fn,ms)=>{timers.set(++next,{fn,at:now+ms});return next},clearTimer:id=>timers.delete(id)});
 return {controller,speech,spoken,settings,listeners,timers,advance(ms){now+=ms;for(const [id,timer] of [...timers])if(timer.at<=now){timers.delete(id);timer.fn()}},voices};
}
(async()=>{
 for(const minutes of [5,10,15]){
  const f=fixture();f.settings.approachMinutes=minutes;const schedule=[{key:'dhuhr',time:minutes*60000+1000}];
  f.controller.tick(schedule,999,true);f.controller.tick(schedule,1000,true);await flush();assert.equal(f.spoken[0].text,'اقتربت صلاة الظهر');
  f.spoken[0].onend();f.controller.previous=999;f.controller.tick(schedule,1000,true);await flush();assert.equal(f.spoken.length,1,'memory deduplicates blocked storage');
 }
 for(const reason of ['hidden','busy','disabled','prayer','off','stale','return']){
  const f=fixture(),schedule=[{key:'fajr',time:301000}];f.controller.tick(schedule,999,true);
  if(reason==='busy')f.controller.isBusy=()=>true;
  if(reason==='disabled')f.settings.enabled=false;
  if(reason==='prayer')f.settings.prayers={...f.settings.prayers,fajr:false};
  if(reason==='off')f.settings.approachEnabled=false;
  if(reason==='return')f.controller.tick(schedule,999,false);
  f.controller.tick(schedule,reason==='stale'?31001:1000,reason!=='hidden');await flush();assert.equal(f.spoken.length,0,reason);
 }
 const unavailable=fixture({voices:[{lang:'ar-SA',localService:false},{lang:'en-US',localService:true}]});const missing=unavailable.controller.beforeAdhan('fajr');await flush();unavailable.advance(600);assert.equal((await missing).status,'unavailable');assert.equal(unavailable.spoken.length,0);assert.equal(unavailable.listeners.size,0);
 const delayed=fixture({voices:[]});const initialized=delayed.controller.init();delayed.voices.push({lang:'ar',localService:true});for(const fn of delayed.listeners)fn();assert.equal((await initialized).status,'ready');assert.equal(delayed.timers.size,0);
 const f=fixture();const first=f.controller.beforeAdhan('fajr');await flush();assert.equal(f.spoken[0].text,'الصلاة خير من النوم');f.controller.cancel();assert.equal((await first).status,'cancelled');assert.equal(f.speech.cancelled,1);assert.equal(f.timers.size,0);
 const timed=f.controller.beforeAdhan('fajr');await flush();f.advance(4500);assert.equal((await timed).status,'timeout');assert.equal(f.speech.cancelled,2);
 f.settings.fajrAnnouncement=false;assert.equal((await f.controller.beforeAdhan('fajr')).status,'skipped');assert.equal(f.spoken.length,2);
 const absent=new PrayerAnnouncements({getSettings:()=>f.settings,speech:null,Utterance:null,storage:null});assert.equal((await absent.init()).status,'unavailable');
 // Actual audio controller preserves selected recording and rejects stale async speech completions.
 const settings={...AUDIO_DEFAULTS,enabled:true,dua:false};let hookCalls=0,complete,cancelled=0;const started=[];
 const audio=new PrayerAudio({getSettings:()=>settings,onState(){},Context:class{},storage:null,beforeAdhan:()=>{hookCalls++;return new Promise(resolve=>complete=resolve)},cancelSpeech:()=>cancelled++});
 audio.armed=true;audio.ctx={state:'running',currentTime:0,createBufferSource:()=>({connect(){},disconnect(){},start(){started.push('adhan')},stop(){}})};audio.gain={gain:{value:1,cancelScheduledValues(){},setValueAtTime(){},linearRampToValueAtTime(){}}};audio.load=async()=>({});
 const playing=audio.play('adhan','fajr');await flush();assert.equal(hookCalls,1);assert.equal(started.length,0);complete();await playing;assert.deepEqual(started,['adhan']);
 const interrupted=audio.play('adhan','fajr');await flush();audio.stop();complete();assert.equal(await interrupted,false);assert.equal(started.length,1);assert(cancelled>=3);
 audio.beforeAdhan=()=>Promise.reject(Error('speech unsupported'));assert.equal(await audio.play('adhan','fajr'),true);assert.equal(started.length,2,'speech errors cannot block adhan');
 console.log('PASS: local Arabic speech, foreground crossing, lead choices, dedup, cancellation, bounded speech and Fajr audio ordering.');
})().catch(error=>{console.error(error);process.exitCode=1});
