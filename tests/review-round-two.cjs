const assert=require('node:assert/strict'),Module=require('node:module'),fs=require('node:fs'),vm=require('node:vm'),esbuild=require('esbuild');
function load(file){const m=new Module(file,module);m._compile(esbuild.buildSync({entryPoints:[file],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,file);return m.exports;}
const {restoreSettings}=load('settings-restore.js');
for(const volume of [0,.2,.8,1])assert.equal(restoreSettings({audio:{volume}}).audio.volume,volume,'Keep valid saved volume');
for(const volume of [null,{},'0.2',-1,2,NaN,Infinity])assert.equal(restoreSettings({audio:{volume}}).audio.volume,1);
const {nativeSchedule}=load('native-adapter.js');const state={lat:30,lon:31,zone:'Africa/Cairo',method:'Egyptian',madhab:'Shafi',audio:{enabled:true,volume:.25,voice:'nufais',prayers:{fajr:true}}};
assert.equal(nativeSchedule(state,new Date('2026-10-28T00:00:00Z'),1).volume,.25);
// Exercise the real storage listener with corrupt settings from another window.
const source=fs.readFileSync('app-source.js','utf8'),marker="window.addEventListener('storage',";let listener;
const context={window:{addEventListener:(name,fn)=>listener=fn},state:{audio:restoreSettings({audio:{enabled:true,volume:.4}}).audio},audio:{armed:true,setVolume(){},disable(){}},restoreSettings,prepare(){},renderAudio(){}};
vm.runInNewContext(source.slice(source.indexOf(marker),source.indexOf(';if(state.audio.enabled)prepare(true)',source.indexOf(marker))),context);
listener({key:'salati',newValue:JSON.stringify({audio:{voice:'bad',enabled:'yes',prayers:{fajr:'false'}}})});assert.equal(context.state.audio.voice,'nufais');assert.equal(typeof context.state.audio.enabled,'boolean');assert.equal(context.state.audio.prayers.fajr,true);
// A fresh but corrupt calendar cache must never suppress a corrective fetch.
const id=JSON.stringify([30,31,'Africa/Cairo','Egyptian','Shafi'])+':2026-10';const valid=[5,6,12,15,18,19].map(h=>Date.parse('2026-10-28T'+String(h).padStart(2,'0')+':00:00+02:00'));
(async()=>{try{
 for(const row of [[0,1,2,3,4,5],[...valid].reverse(),valid.map(t=>t+864000000),valid.map(()=>valid[0])]){
  global.localStorage={getItem:()=>JSON.stringify({[id]:{fetchedAt:Date.now(),days:{'2026-10-28':row}}}),setItem(){}};
  const p=load('prayer-provider.js');assert.equal(p.providerTimes(state,{year:2026,month:10,day:28}),null,'Reject corrupt finite cached rows');let fetched=0;
  await p.refreshProvider(state,{year:2026,month:10,day:28},async()=>{fetched++;throw Error('offline')});assert.equal(fetched,0,'Legacy cache failures must never transmit precise coordinates');
 }
}finally{delete global.localStorage;}
console.log('PASS: volume retention/native schedule, malformed cross-window settings, corrupt finite cache rejection with no external location fetch.');})().catch(e=>{console.error(e);process.exitCode=1});
