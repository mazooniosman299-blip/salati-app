import {duePrayer} from './audio-controller.js';

const PRAYER_NAMES={fajr:'الفجر',dhuhr:'الظهر',asr:'العصر',maghrib:'المغرب',isha:'العشاء'};
const LOCAL_ARABIC=voice=>voice?.localService===true&&/^ar(?:[-_]|$)/i.test(voice.lang||'');

// Web reminders are deliberately foreground only. Speech uses installed voices only.
export class PrayerAnnouncements{
 constructor({getSettings,isBusy=()=>false,onState=()=>{},storage,speech=globalThis.speechSynthesis,Utterance=globalThis.SpeechSynthesisUtterance,now=()=>Date.now(),setTimer=setTimeout,clearTimer=clearTimeout}={}){
  this.getSettings=getSettings;this.isBusy=isBusy;this.onState=onState;this.speech=speech;this.Utterance=Utterance;this.now=now;this.setTimer=setTimer;this.clearTimer=clearTimer;this.previous=now();this.wasVisible=false;this.played=new Set();this.generation=0;this.pending=null;this.utterance=null;
  try{this.storage=storage===undefined?globalThis.localStorage:storage}catch{this.storage=null}
 }
 emit(status){this.status=status;try{this.onState(status)}catch{}return {status}}
 async voice(){
  const find=()=>{try{return this.speech?.getVoices().find(LOCAL_ARABIC)}catch{return null}};
  if(!this.speech||!this.Utterance)return null;
  const available=find();if(available)return available;
  return new Promise(resolve=>{
   let timer,done=false;
   const finish=value=>{if(done)return;done=true;this.clearTimer(timer);this.speech.removeEventListener?.('voiceschanged',changed);if(this.pending===cancel)this.pending=null;resolve(value)};
   const changed=()=>{const voice=find();if(voice)finish(voice)};
   const cancel=()=>finish(null);this.pending=cancel;
   this.speech.addEventListener?.('voiceschanged',changed);
   timer=this.setTimer(()=>finish(find()),600);changed();
  });
 }
 async init(){const gen=this.generation;const voice=await this.voice();return gen===this.generation?this.emit(voice?'ready':'unavailable'):{status:'cancelled'}}
 cancel(){this.generation++;const utterance=this.utterance;this.pending?.();this.pending=null;if(utterance){utterance.onend=null;utterance.onerror=null;this.utterance=null;try{this.speech.cancel()}catch{}}}
 async speak(text){
  this.cancel();const gen=this.generation;const voice=await this.voice();
  if(gen!==this.generation)return {status:'cancelled'};
  if(!voice)return this.emit('unavailable');
  // Never queue behind speech belonging to another feature or application.
  if(this.speech.speaking||this.speech.pending)return this.emit('busy');
  return new Promise(resolve=>{
   let utterance,timer,done=false;
   const finish=status=>{if(done)return;done=true;this.clearTimer(timer);if(this.pending===cancel)this.pending=null;if(utterance){utterance.onend=null;utterance.onerror=null}if(this.utterance===utterance)this.utterance=null;if(status==='timeout'){try{this.speech.cancel()}catch{}}resolve(this.emit(status))};
   const cancel=()=>finish('cancelled');this.pending=cancel;
   try{utterance=new this.Utterance(text);utterance.voice=voice;utterance.lang=voice.lang;utterance.volume=Math.max(0,Math.min(1,Number(this.getSettings()?.volume) || 0));utterance.onend=()=>finish('finished');utterance.onerror=()=>finish('error');this.utterance=utterance;timer=this.setTimer(()=>finish('timeout'),4500);this.emit('speaking');if(gen!==this.generation){finish('cancelled');return}this.speech.speak(utterance)}catch{finish('error')}
  });
 }
 beforeAdhan(prayer){const settings=this.getSettings();if(prayer!=='fajr'||settings.fajrAnnouncement===false||!settings.enabled||settings.prayers?.fajr!==true)return Promise.resolve({status:'skipped'});return this.speak('الصلاة خير من النوم')}
 tick(schedule,now=this.now(),visible=globalThis.document?.visibilityState==='visible'){
  const previous=this.previous,wasVisible=this.wasVisible;this.previous=now;this.wasVisible=visible;
  if(!visible){this.cancel();return}
  if(!wasVisible||this.isBusy()||this.utterance||this.pending)return;
  const settings=this.getSettings();if(!settings.enabled||settings.approachEnabled===false)return;
  const minutes=[5,10,15].includes(Number(settings.approachMinutes))?Number(settings.approachMinutes):5;
  const shifted=schedule.map(prayer=>({...prayer,time:+prayer.time-minutes*60000}));
  const prayer=duePrayer(shifted,previous,now,settings);if(!prayer||!PRAYER_NAMES[prayer.key])return;
  const key='salati-approach-'+prayer.key+'-'+(+prayer.time)+'-'+minutes;
  if(this.played.has(key))return;
  try{if(this.storage?.getItem(key))return}catch{}
  this.played.add(key);if(this.played.size>256)this.played.delete(this.played.values().next().value);
  try{this.storage?.setItem(key,'1')}catch{}
  void this.speak('اقتربت صلاة '+PRAYER_NAMES[prayer.key]);
 }
}
