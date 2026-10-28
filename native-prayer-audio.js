// Android owns both previews and scheduled adhan. Never open a Web Audio output here.
export const hasNativePrayerAudio=()=>typeof window.SalatiNative?.previewAdhan==='function';
export class NativePrayerAudio{
 constructor({getSettings,onState}){this.getSettings=getSettings;this.onState=onState;this.active=false;this.armed=false;this.preparing=false;this.previous=Date.now();this.code='inactive';window.addEventListener('salati-native-playback',e=>this.receive(e.detail?.code));queueMicrotask(()=>{try{this.receive(window.SalatiNative.audioState())}catch{this.emit('inactive')}})}
 emit(code){this.code=code;this.onState(code)}
 receive(code){if(!['inactive','loading','ready','adhan','fajr','dua','finished','stopped','error','blocked'].includes(code))return;this.active=['loading','adhan','fajr','dua'].includes(code);this.emit(code)}
 async arm({automatic=false}={}){if(this.active&&!automatic)this.stop(false);this.armed=true;if(!this.active)this.emit('ready');return true}
 setVolume(){if(typeof window.SalatiNative.setAdhanVolume==='function')window.SalatiNative.setAdhanVolume(this.getSettings().volume)}
 stop(report=true){window.SalatiNative.stopAdhan();this.active=false;if(report)this.emit(this.armed?'stopped':'inactive')}
 disable(){this.armed=false;this.stop(false);this.emit('inactive')}
 async play(kind='adhan'){this.active=true;this.emit('loading');try{const s=this.getSettings();window.SalatiNative.previewAdhan(kind,s.voice,s.volume);return true}catch{this.active=false;this.emit('error');return false}}
 tick(){} // AlarmManager is the only scheduler on Android.
}
