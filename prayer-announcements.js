const CLIPS={'الصلاة خير من النوم':'audio/reminders/fajr-user-approved-1.0.103.mp3'};
let activeAnnouncement=null;

// Short, same-origin recordings work without installed voices or a speech service.
// Browser scheduling remains foreground only; Android owns background delivery.
export class PrayerAnnouncements{
 constructor({getSettings,onState=()=>{},Audio=globalThis.Audio,setTimer=(callback,delay)=>globalThis.setTimeout(callback,delay),clearTimer=timer=>globalThis.clearTimeout(timer)}={}){
  this.getSettings=getSettings;this.onState=onState;this.Audio=Audio;this.setTimer=setTimer;this.clearTimer=clearTimer;this.generation=0;this.pending=null;this.player=null;
 }
 emit(status){this.status=status;try{this.onState(status)}catch{}return {status}}
 init(){return Promise.resolve(this.emit(this.Audio?'ready':'unavailable'))}
 cancel(){this.generation++;this.pending?.();this.pending=null;if(activeAnnouncement===this)activeAnnouncement=null;}
 speak(text){
  if(activeAnnouncement&&activeAnnouncement!==this)activeAnnouncement.cancel();
  this.cancel();const gen=this.generation,src=CLIPS[text];
  if(!src||!this.Audio)return Promise.resolve(this.emit('unavailable'));
  const saved=Number(this.getSettings()?.volume),volume=Number.isFinite(saved)?Math.max(0,Math.min(1,saved)):1;
  if(volume===0)return Promise.resolve(this.emit('muted'));
  activeAnnouncement=this;
  return new Promise(resolve=>{
   let player,timer,done=false;
   const finish=status=>{
    if(done)return;done=true;this.clearTimer(timer);
    if(this.pending===cancel)this.pending=null;
    if(player){player.onended=null;player.onerror=null;try{player.pause();player.removeAttribute('src');player.load()}catch{}}
    if(this.player===player)this.player=null;
    if(activeAnnouncement===this)activeAnnouncement=null;
    // A late completion never overwrites state emitted by its replacement.
    resolve(gen===this.generation||status==='cancelled'?this.emit(status):{status:'cancelled'});
   };
   const cancel=()=>finish('cancelled');this.pending=cancel;
   try{
    player=new this.Audio(src);this.player=player;player.preload='auto';player.volume=volume;player.loop=false;
    player.onended=()=>finish('finished');player.onerror=()=>finish('error');
    timer=this.setTimer(()=>finish('timeout'),30000);this.emit('loading');
    // Call play synchronously while a preview click still owns user activation.
    Promise.resolve(player.play()).then(()=>{if(!done&&gen===this.generation)this.emit('playing')},error=>finish(error?.name==='NotAllowedError'?'blocked':'error'));
   }catch{finish('error')}
  });
 }
 beforeAdhan(prayer){const settings=this.getSettings();if(prayer!=='fajr'||settings.fajrAnnouncement===false||!settings.enabled||settings.prayers?.fajr!==true)return Promise.resolve({status:'skipped'});return this.speak('الصلاة خير من النوم')}
}
