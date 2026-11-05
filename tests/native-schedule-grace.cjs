// A fresh schedule must not invalidate an already scheduled, still-deliverable
// prayer while the WebView resynchronizes at its due time.
const assert=require('node:assert/strict'),Module=require('node:module'),esbuild=require('esbuild');
const m=new Module(__filename,module);m._compile(esbuild.buildSync({entryPoints:['native-adapter.js'],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,__filename);
const state={lat:23.588,lon:58.3829,zone:'Asia/Muscat',method:'Auto',madhab:'Shafi',name:'مسقط',adjustments:{},audio:{enabled:true,voice:'nufais',volume:1,dua:true,silentMode:true,prayers:{fajr:true,dhuhr:true,asr:true,maghrib:true,isha:true}}};
const before=m.exports.nativeSchedule(state,new Date('2026-10-20T20:00:00Z'),3);
for(const prayer of ['fajr','dhuhr','asr','maghrib','isha']){
 const event=before.events.find(e=>e.prayer===prayer);assert(event,prayer);
 for(const delay of [0,20000,300000,1800000]){
  const config=m.exports.nativeSchedule(state,new Date(event.time+delay),3);
  assert(config.events.some(e=>e.prayer===prayer&&e.time===event.time),`${prayer}: resync at +${delay}ms invalidates a pending alarm within the existing maximum delivery window`);
  assert(config.events.every(e=>e.time>=event.time+delay-1800000),'Never retain an event beyond existing inexact delivery grace');
 }
 assert(!m.exports.nativeSchedule(state,new Date(event.time+1800001),3).events.some(e=>e.time===event.time&&e.prayer===prayer),'Expired event stays expired');
 const disabled={...state,audio:{...state.audio,prayers:{...state.audio.prayers,[prayer]:false}}};
 assert(m.exports.nativeSchedule(disabled,new Date(event.time+20000),3).events.every(e=>e.prayer!==prayer),'Respect explicit prayer disable');
}
console.log('PASS all five prayers retain only still-deliverable selected events during resync; expired and disabled events excluded');
