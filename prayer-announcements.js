import {duePrayer} from './audio-controller.js';

const PRAYER_NAMES={fajr:'الفجر',dhuhr:'الظهر',asr:'العصر',maghrib:'المغرب',isha:'العشاء'};
const CLIPS=Object.fromEntries(Object.entries(PRAYER_NAMES).map(([key,name])=>['اقتربت صلاة '+name,'audio/reminders/approach-'+key+'.mp3']));
CLIPS['الصلاة خير من النوم']='audio/reminders/fajr-phrase.mp3';

// Short, same-origin recordings work without installed voices or a speech service.
// Browser scheduling remains foreground only; Android owns background delivery.
export class PrayerAnnouncements{
 constructor({getSettings,isBusy=()=>false,onState=()=>{},storage,Audio=globalThis.Audio,now=()=>Date.now(),setTimer=(callback,delay)=>globalThis.setTimeout(callback,delay),clearTimer=timer=>globalThis.clearTimeout(timer)}={}){
  this.getSettings=getSettings;this.isBusy=isBusy;this.onState=onState;this.Audio=Audio;this.now=now;this.setTimer=setTimer;this.clearTimer=clearTimer;this.previous=now();this.wasVisible=false;this.played=new Set();this.generation=0;this.pending=null;this.player=null;
  try{this.storage=storage===undefined?globalThis.localStorage:storage}catch{this.storage=null}
 }
 emit(status){this.status=status;try{this.onState(status)}catch{}return {status}}
 init(){return Promise.resolve(this.emit(this.Audio?'ready':'unavailable'))}
 cancel(){this.generation++;this.pending?.();this.pending=null;}
 speak(text){
  this.cancel();const gen=this.generation,src=CLIPS[text];
  if(!src||!this.Audio)return Promise.resolve(this.emit('unavailable'));
  const saved=Number(this.getSettings()?.volume),volume=Number.isFinite(saved)?Math.max(0,Math.min(1,saved)):1;
  if(volume===0)return Promise.resolve(this.emit('muted'));
  return new Promise(resolve=>{
   let player,timer,done=false;
   const finish=status=>{
    if(done)return;done=true;this.clearTimer(timer);
    if(this.pending===cancel)this.pending=null;
    if(player){player.onended=null;player.onerror=null;try{player.pause();player.removeAttribute('src');player.load()}catch{}}
    if(this.player===player)this.player=null;
    // A late completion never overwrites state emitted by its replacement.
    resolve(gen===this.generation||status==='cancelled'?this.emit(status):{status:'cancelled'});
   };
   const cancel=()=>finish('cancelled');this.pending=cancel;
   try{
    player=new this.Audio(src);this.player=player;player.preload='auto';player.volume=volume;
    player.onended=()=>finish('finished');player.onerror=()=>finish('error');
    timer=this.setTimer(()=>finish('timeout'),12000);this.emit('loading');
    // Call play synchronously while a preview click still owns user activation.
    Promise.resolve(player.play()).then(()=>{if(!done&&gen===this.generation)this.emit('playing')},error=>finish(error?.name==='NotAllowedError'?'blocked':'error'));
   }catch{finish('error')}
  });
 }
 beforeAdhan(prayer){const settings=this.getSettings();if(prayer!=='fajr'||settings.fajrAnnouncement===false||!settings.enabled||settings.prayers?.fajr!==true)return Promise.resolve({status:'skipped'});return this.speak('الصلاة خير من النوم')}
 tick(schedule,now=this.now(),visible=globalThis.document?.visibilityState==='visible'){
  const previous=this.previous,wasVisible=this.wasVisible;this.previous=now;this.wasVisible=visible;
  if(!visible){this.cancel();return}
  if(!wasVisible||this.isBusy()||this.player||this.pending)return;
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
