const assert=require('node:assert/strict'),Module=require('node:module'),{buildSync}=require('esbuild');
const compiled=new Module(__filename,module);compiled._compile(buildSync({entryPoints:['prayer-announcements.js'],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,__filename);
const {PrayerAnnouncements}=compiled.exports;
const audioModule=new Module(__filename,module);audioModule._compile(buildSync({entryPoints:['audio-controller.js'],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,__filename);
const {PrayerAudio,AUDIO_DEFAULTS}=audioModule.exports;
const flush=async()=>{for(let i=0;i<8;i++)await Promise.resolve()};
function fixture(){
 let now=0,next=0;const timers=new Map(),players=[],states=[],settings={...AUDIO_DEFAULTS,enabled:true};
 class Utterance {constructor(text){this.text=text}}
 const speech={
  getVoices(){return [{lang:'ar-OM'}]},
  speak(utterance){players.push(utterance)},
  cancel(){if(players.length)players.at(-1).cancelled=true}
 };
 const controller=new PrayerAnnouncements({getSettings:()=>settings,speech,Utterance,
  onState:status=>states.push(status),
  setTimer:(fn,ms)=>{timers.set(++next,{fn,at:now+ms});return next},
  clearTimer:id=>timers.delete(id)});
 return {controller,players,states,settings,timers,advance(ms){now+=ms;for(const [id,timer] of [...timers])if(timer.at<=now){timers.delete(id);timer.fn()}}};
}
(async()=>{
 for(const text of ['اقتربت صلاة الفجر','اقتربت صلاة الظهر','اقتربت صلاة العصر','اقتربت صلاة المغرب','اقتربت صلاة العشاء']){
  const f=fixture();assert.equal((await f.controller.speak(text)).status,'unavailable');assert.equal(f.players.length,0);
 }
 const ownerOne=fixture(),ownerTwo=fixture();const cancelledOwner=ownerOne.controller.speak('الصلاة خير من النوم');await flush();
 const currentOwner=ownerTwo.controller.speak('الصلاة خير من النوم');await flush();
 assert(ownerOne.players[0].cancelled,'a second announcement controller must stop the first output');
 assert.equal((await cancelledOwner).status,'cancelled');ownerTwo.players[0].onend();await currentOwner;
 const f=fixture();assert.equal((await f.controller.init()).status,'ready');
 const first=f.controller.beforeAdhan('fajr');await flush();assert.equal(f.players[0].text,'الصلاة خير من النوم');assert.equal(f.players[0].volume,1);const oldEnd=f.players[0].onend;
 const replacement=f.controller.speak('الصلاة خير من النوم');assert.equal((await first).status,'cancelled');await flush();assert(f.players[0].cancelled);assert.equal(f.players[1].text,'الصلاة خير من النوم');oldEnd();assert.equal(f.controller.status,'playing','old callback cannot finish newer playback');f.players[1].onend();assert.equal((await replacement).status,'finished');assert.equal(f.timers.size,0);
 const failed=f.controller.speak('الصلاة خير من النوم');await flush();f.players.at(-1).onerror();assert.equal((await failed).status,'error');assert.equal(f.timers.size,0);
 const timed=f.controller.speak('الصلاة خير من النوم');await flush();f.advance(14000);assert.equal(f.controller.status,'playing','complete human phrase must not be cut at the old synthetic deadline');f.advance(16000);assert.equal((await timed).status,'timeout');assert(f.players.at(-1).cancelled);
 f.settings.fajrAnnouncement=false;assert.equal((await f.controller.beforeAdhan('fajr')).status,'skipped');
 assert.equal((await f.controller.speak('not an approved phrase')).status,'unavailable');
 f.settings.volume=0;assert.equal((await f.controller.speak('الصلاة خير من النوم')).status,'muted');
 const absent=new PrayerAnnouncements({getSettings:()=>f.settings,speech:null,Utterance:null});assert.equal((await absent.init()).status,'unavailable');
 // Actual audio controller preserves selected recording and rejects stale async speech completions.
 const settings={...AUDIO_DEFAULTS,enabled:true,dua:false};let hookCalls=0,complete,cancelled=0;const started=[];
 const audio=new PrayerAudio({getSettings:()=>settings,onState(){},Context:class{},storage:null,beforeAdhan:()=>{hookCalls++;return new Promise(resolve=>complete=resolve)},cancelSpeech:()=>cancelled++});
 audio.armed=true;audio.ctx={state:'running',currentTime:0,createBufferSource:()=>({connect(){},disconnect(){},start(){started.push('adhan')},stop(){}})};audio.gain={gain:{value:1,cancelScheduledValues(){},setValueAtTime(){},linearRampToValueAtTime(){}}};audio.load=async()=>({});
 const playing=audio.play('adhan','fajr');await flush();assert.equal(hookCalls,1);assert.equal(started.length,0);complete();await playing;assert.deepEqual(started,['adhan']);
 const interrupted=audio.play('adhan','fajr');await flush();audio.stop();complete();assert.equal(await interrupted,false);assert.equal(started.length,1);assert(cancelled>=3);
 audio.beforeAdhan=()=>Promise.reject(Error('speech unsupported'));assert.equal(await audio.play('adhan','fajr'),true);assert.equal(started.length,2,'speech errors cannot block adhan');
 console.log('PASS: Fajr-only device TTS with no unlicensed recording, stale callback cancellation, timeout and Fajr ordering.');
})().catch(error=>{console.error(error);process.exitCode=1});
