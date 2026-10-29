const assert=require('node:assert/strict'),Module=require('node:module'),{buildSync}=require('esbuild');
const compiled=new Module(__filename,module);compiled._compile(buildSync({entryPoints:['prayer-announcements.js'],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,__filename);
const {PrayerAnnouncements}=compiled.exports;
const audioModule=new Module(__filename,module);audioModule._compile(buildSync({entryPoints:['audio-controller.js'],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,__filename);
const {PrayerAudio,AUDIO_DEFAULTS}=audioModule.exports;
const flush=async()=>{for(let i=0;i<8;i++)await Promise.resolve()};
function fixture(){
 let now=0,next=0;const timers=new Map(),players=[],states=[],settings={...AUDIO_DEFAULTS,enabled:true};
 class Audio {constructor(src){this.src=src;players.push(this);}play(){return Promise.resolve();}pause(){this.paused=true;}removeAttribute(){}load(){}}
 const controller=new PrayerAnnouncements({getSettings:()=>settings,storage:{getItem(){throw Error('blocked')},setItem(){throw Error('blocked')}},Audio,onState:s=>states.push(s),now:()=>now,setTimer:(fn,ms)=>{timers.set(++next,{fn,at:now+ms});return next},clearTimer:id=>timers.delete(id)});
 return {controller,players,states,settings,timers,advance(ms){now+=ms;for(const [id,timer] of [...timers])if(timer.at<=now){timers.delete(id);timer.fn()}}};
}
(async()=>{
 for(const minutes of [5,10,15]){
  const f=fixture();f.settings.approachMinutes=minutes;const schedule=[{key:'dhuhr',time:minutes*60000+1000}];
  f.controller.tick(schedule,999,true);f.controller.tick(schedule,1000,true);await flush();assert.equal(f.players[0]?.src,'audio/reminders/approach-hayya-human-v1.mp3','reminder must play bundled clip without installed Arabic voices');
  f.players[0].onended();f.controller.previous=999;f.controller.tick(schedule,1000,true);await flush();assert.equal(f.players.length,1,'blocked storage still deduplicated');
 }
 for(const reason of ['hidden','busy','disabled','prayer','off','stale','return']){
  const f=fixture(),schedule=[{key:'fajr',time:301000}];f.controller.tick(schedule,999,true);
  if(reason==='busy')f.controller.isBusy=()=>true;
  if(reason==='disabled')f.settings.enabled=false;
  if(reason==='prayer')f.settings.prayers={...f.settings.prayers,fajr:false};
  if(reason==='off')f.settings.approachEnabled=false;
  if(reason==='return')f.controller.tick(schedule,999,false);
  f.controller.tick(schedule,reason==='stale'?31001:1000,reason!=='hidden');await flush();assert.equal(f.players.length,0,reason);
 }
 const f=fixture();assert.equal((await f.controller.init()).status,'ready');
 const first=f.controller.beforeAdhan('fajr');await flush();assert.equal(f.players[0].src,'audio/reminders/fajr-phrase-human-v1.mp3');assert.equal(f.players[0].volume,1);const oldEnd=f.players[0].onended;
 const replacement=f.controller.speak('اقتربت صلاة العصر');assert.equal((await first).status,'cancelled');await flush();assert(f.players[0].paused);assert.equal(f.players[1].src,'audio/reminders/approach-hayya-human-v1.mp3');oldEnd();assert.equal(f.controller.status,'playing','old callback cannot finish newer playback');f.players[1].onended();assert.equal((await replacement).status,'finished');assert.equal(f.timers.size,0);
 const failed=f.controller.speak('الصلاة خير من النوم');await flush();f.players.at(-1).onerror();assert.equal((await failed).status,'error');assert.equal(f.timers.size,0);
 const timed=f.controller.speak('الصلاة خير من النوم');await flush();f.advance(14000);assert.equal(f.controller.status,'playing','complete human phrase must not be cut at the old synthetic deadline');f.advance(16000);assert.equal((await timed).status,'timeout');assert(f.players.at(-1).paused);
 f.settings.fajrAnnouncement=false;assert.equal((await f.controller.beforeAdhan('fajr')).status,'skipped');
 assert.equal((await f.controller.speak('not an approved phrase')).status,'unavailable');
 f.settings.volume=0;assert.equal((await f.controller.speak('الصلاة خير من النوم')).status,'muted');
 const absent=new PrayerAnnouncements({getSettings:()=>f.settings,Audio:null,storage:null});assert.equal((await absent.init()).status,'unavailable');
 // Actual audio controller preserves selected recording and rejects stale async speech completions.
 const settings={...AUDIO_DEFAULTS,enabled:true,dua:false};let hookCalls=0,complete,cancelled=0;const started=[];
 const audio=new PrayerAudio({getSettings:()=>settings,onState(){},Context:class{},storage:null,beforeAdhan:()=>{hookCalls++;return new Promise(resolve=>complete=resolve)},cancelSpeech:()=>cancelled++});
 audio.armed=true;audio.ctx={state:'running',currentTime:0,createBufferSource:()=>({connect(){},disconnect(){},start(){started.push('adhan')},stop(){}})};audio.gain={gain:{value:1,cancelScheduledValues(){},setValueAtTime(){},linearRampToValueAtTime(){}}};audio.load=async()=>({});
 const playing=audio.play('adhan','fajr');await flush();assert.equal(hookCalls,1);assert.equal(started.length,0);complete();await playing;assert.deepEqual(started,['adhan']);
 const interrupted=audio.play('adhan','fajr');await flush();audio.stop();complete();assert.equal(await interrupted,false);assert.equal(started.length,1);assert(cancelled>=3);
 audio.beforeAdhan=()=>Promise.reject(Error('speech unsupported'));assert.equal(await audio.play('adhan','fajr'),true);assert.equal(started.length,2,'speech errors cannot block adhan');
 console.log('PASS: bundled reminders without TTS, foreground crossing, lead choices, storage failure dedup, stale callback cancellation, deadline and Fajr audio ordering.');
})().catch(error=>{console.error(error);process.exitCode=1});
