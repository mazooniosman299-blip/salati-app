const assert=require('node:assert/strict'),Module=require('node:module'),esbuild=require('esbuild');
const m=new Module('sync',module);m._compile(esbuild.buildSync({entryPoints:['native-adapter.js'],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,'sync.cjs');
let pending,canceled=false,delivered=[];const old={window:global.window,document:global.document,setTimeout:global.setTimeout,clearTimeout:global.clearTimeout,fetch:global.fetch};
try{
 global.window={SalatiNative:{sync:json=>{delivered.push(JSON.parse(json));return 'ok'}},dispatchEvent:()=>{}};
 global.document={getElementById:()=>null};global.fetch=()=>{throw Error('Must not need the internet')};
 global.setTimeout=fn=>{pending=fn;return 11};global.clearTimeout=()=>{canceled=true};
 const state={lat:23.588,lon:58.3829,zone:'Asia/Muscat',method:'Auto',madhab:'Shafi',name:'مسقط',adjustments:{},audio:{enabled:true,voice:'qatami',volume:.8,dua:true,silentMode:true,prayers:{fajr:true,dhuhr:true,asr:true,maghrib:true,isha:true}}};
 m.exports.queueNativeSync({...state,locationSet:false,lat:null,lon:null},true);assert.equal(delivered.length,0);assert.equal(pending,undefined);
 m.exports.queueNativeSync(state);assert.equal(delivered.length,0);assert(pending);
 m.exports.queueNativeSync(state,true);assert(canceled);assert.equal(delivered.length,1);assert.equal(delivered[0].enabled,true);assert(delivered[0].events.length>1900);
 m.exports.queueNativeSync(state,true);assert.equal(delivered.length,1);
 state.audio.silentMode=false;m.exports.queueNativeSync(state,true);assert.equal(delivered.at(-1).silentMode,false);state.audio.silentMode=true;m.exports.queueNativeSync(state,true);assert.equal(delivered.at(-1).silentMode,true);assert.equal(delivered.length,3);
 state.audio.enabled=false;m.exports.queueNativeSync(state,true);assert.equal(delivered.length,4);assert.equal(delivered[3].enabled,false);
 const elements=new Map();global.document.getElementById=id=>{if(!elements.has(id))elements.set(id,{textContent:'',hidden:false});return elements.get(id)};
 let nativeStatus={ready:true,notificationsAllowed:false,exactAlarmsAllowed:true,nextAlarmTime:Date.now()+60000};global.window.SalatiNative.status=()=>JSON.stringify(nativeStatus);
 state.lang='ar';state.audio.enabled=true;m.exports.renderNativeAudio(state);assert.equal(elements.get('audioStatus').textContent,'');assert.equal(elements.get('audioStatus').hidden,true);assert(elements.get('nativeStatus').textContent.includes('الإشعارات غير مسموحة'));
 nativeStatus.nextAlarmTime=0;m.exports.renderNativeAudio(state);assert(elements.get('audioStatus').textContent.includes('لم يُحفظ'));assert.equal(elements.get('audioStatus').hidden,false);
 console.log('PASS: immediate offline schedule save before app/settings exit, duplicate suppression and disabling audio are persisted without a network request.');
}finally{for(const [key,value]of Object.entries(old))global[key]=value}
