const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('app-source.js','utf8');const render=source.slice(source.indexOf('function renderAudio(){'),source.indexOf('function setupAudio(){'));const start=source.indexOf("$('audioEnable').onclick="),end=source.indexOf(";$('audioResume').onclick",start);assert(start>=0&&end>start);
for(const native of [false,true])for(const initial of [false,true]){
 const nodes=new Map(),node=id=>{if(!nodes.has(id))nodes.set(id,{attributes:{},on:false,setAttribute(k,v){this.attributes[k]=v;},classList:{toggle(k,v){node(id).on=v;}}});return nodes.get(id);};let saved=0,synced=0,armed=0,disabled=0;
 const state={audio:{enabled:initial,voice:'qatami',dua:true,silentMode:true,prayers:{}}};const audio={code:'inactive',armed:false,disable(){disabled++;this.armed=false;}};
 const c={state,audio,$:node,save(){saved++;},queueNativeSync(s,force){assert.equal(s,state);assert(force);synced++;},prepare(){armed++;audio.armed=true;},tr:(a,b)=>a,document:{querySelectorAll:()=>[]},refreshVoicePicker(){},hasNativePrayerAudio:()=>native,audioMessages:{inactive:['جاهز','Ready']},mushaf:null,renderNativeAudio(){},syncNativeAds(){}};
 vm.runInNewContext(render+'\n'+source.slice(start,end),c);c.renderAudio();assert.equal(node('audioEnable').attributes['aria-checked'],String(initial));
 node('audioEnable').onclick();assert.equal(state.audio.enabled,!initial);assert.equal(node('audioEnable').attributes['aria-checked'],String(!initial));assert.equal(node('audioEnable').on,!initial);
 node('audioEnable').onclick();assert.equal(state.audio.enabled,initial);assert.equal(node('audioEnable').attributes['aria-checked'],String(initial));assert.equal(node('audioEnable').on,initial);assert.equal(saved,2);assert.equal(synced,2);assert.equal(armed,1);assert.equal(disabled,1);
}
console.log('PASS: real adhan switch handler enables/disables, arms/stops, persists settings and synchronizes native alarms; ARIA and visual state agree in both directions.');
