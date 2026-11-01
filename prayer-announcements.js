// Explicit Fajr-phrase announcement, never a prerecorded clip without
// a documented redistribution license. Android has its own native TTS path.
// Browser speech synthesis is foreground-only and may not be available.
const FAJR_PHRASE='الصلاة خير من النوم';
let activeAnnouncement=null;
export class PrayerAnnouncements {
 constructor({getSettings,onState=()=>{},speech=globalThis.speechSynthesis,
   Utterance=globalThis.SpeechSynthesisUtterance,
   setTimer=(callback,delay)=>globalThis.setTimeout(callback,delay),
   clearTimer=timer=>globalThis.clearTimeout(timer)}={}){
  this.getSettings=getSettings;this.onState=onState;
  this.speech=speech;this.Utterance=Utterance;
  this.setTimer=setTimer;this.clearTimer=clearTimer;
  this.generation=0;this.pending=null;this.utterance=null;
 }
 emit(status){this.status=status;try{this.onState(status)}catch{}return {status}}
 init(){return Promise.resolve(this.emit(this.speech&&this.Utterance?'ready':'unavailable'))}
 cancel(){
  this.generation++;
  this.pending?.();this.pending=null;
  try{this.speech?.cancel()}catch{}
  this.utterance=null;
  if(activeAnnouncement===this)activeAnnouncement=null;
 }
 speak(text){
  if(activeAnnouncement&&activeAnnouncement!==this)activeAnnouncement.cancel();
  this.cancel();const generation=this.generation;
  if(text!==FAJR_PHRASE||!this.speech||!this.Utterance)return Promise.resolve(this.emit('unavailable'));
  const value=Number(this.getSettings()?.volume);
  const volume=Number.isFinite(value)?Math.max(0,Math.min(1,value)):1;
  if(volume===0)return Promise.resolve(this.emit('muted'));
  activeAnnouncement=this;
  return new Promise(resolve=>{
   let done=false,timer=null,utterance;
   const finish=status=>{
    if(done)return;done=true;this.clearTimer(timer);
    if(this.pending===cancel)this.pending=null;
    if(this.utterance===utterance)this.utterance=null;
    if(activeAnnouncement===this)activeAnnouncement=null;
    resolve(generation===this.generation||status==='cancelled'?this.emit(status):{status:'cancelled'});
   };
   const cancel=()=>finish('cancelled');
   this.pending=cancel;
   try{
    utterance=new this.Utterance(FAJR_PHRASE);
    this.utterance=utterance;utterance.lang='ar';utterance.rate=0.9;utterance.volume=volume;
    utterance.onend=()=>finish('finished');utterance.onerror=()=>finish('error');
    const voices=this.speech.getVoices?.()||[];
    const arabic=voices.find(v=>String(v.lang).toLowerCase().startsWith('ar'));
    if(arabic)utterance.voice=arabic;
    timer=this.setTimer(()=>{try{this.speech.cancel()}catch{}finish('timeout')},30000);
    this.emit('loading');this.speech.speak(utterance);this.emit('playing');
   }catch{finish('error')}
  });
 }
 beforeAdhan(prayer){
  const settings=this.getSettings();
  if(prayer!=='fajr'||settings.fajrAnnouncement===false||!settings.enabled||settings.prayers?.fajr!==true)
   return Promise.resolve({status:'skipped'});
  return this.speak(FAJR_PHRASE);
 }
}
