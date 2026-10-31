const assert = require('node:assert/strict');
const fs = require('node:fs');
const source = fs.readFileSync('prayer-provider.js','utf8');
const state = {lat:23.588,lon:58.3829,zone:'Asia/Muscat',method:'MuslimWorldLeague',madhab:'Shafi'};
const date = {year:2026,month:10,day:22};
const key = JSON.stringify([state.lat,state.lon,state.zone,state.method,state.madhab])+':2026-10';
const makeRow=day=>['01:00','02:00','08:00','11:00','14:00','15:00'].map(t=>Date.parse('2026-10-'+String(day).padStart(2,'0')+'T'+t+':00Z'));
const row=makeRow(22),days=Object.fromEntries(Array.from({length:31},(_,i)=>['2026-10-'+String(i+1).padStart(2,'0'),makeRow(i+1)]));
async function run(){
 const previous = globalThis.localStorage;
 try{
  for(const [label,ageDays,expected] of [['recent',2,true],['offline-usable',40,true],['expired',46,false],['future-clock',-3,false],['partial-month',2,false]]){
   globalThis.localStorage={getItem:()=>JSON.stringify({[key]:{fetchedAt:Date.now()-ageDays*86400000,days:label==='partial-month'?{'2026-10-22':row}:days}}),setItem(){}};
   const mod=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64')+'#'+label);
   assert.equal(mod.MAX_OFFLINE_CACHE_AGE_MS,45*86400000);
   const times=mod.providerTimes(state,date);
   assert.equal(times!==null,expected,label);
   if(times){assert.equal(+times.fajr,row[0]);assert.equal(mod.providerTimes({...state,zone:'UTC'},date),null,'timezone isolation');assert.equal(mod.providerTimes({...state,madhab:'Hanafi'},date),null,'madhab isolation');}
  }
  console.log('PASS: cache expiry, clock skew, offline grace, and cache-key isolation (5 scenarios).');
 }finally{if(previous===undefined)delete globalThis.localStorage;else globalThis.localStorage=previous;}
}
run().catch(e=>{console.error(e);process.exitCode=1});
