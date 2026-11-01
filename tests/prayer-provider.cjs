const assert=require('node:assert/strict'),Module=require('node:module');
const compiled=require('esbuild').buildSync({entryPoints:['prayer-provider.js'],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text;
const m=new Module('offline-provider',module);m._compile(compiled,'offline-provider.cjs');
const {parseCalendar,refreshProvider,providerTimes,timetableRevision}=m.exports;
const state={lat:23.588,lon:58.3829,zone:'Asia/Muscat',method:'MuslimWorldLeague',madhab:'Shafi'};
const keys=['Fajr','Sunrise','Dhuhr','Asr','Maghrib','Isha'];
function calendar(s,y,month,id=3){
 const days=new Date(Date.UTC(y,month,0)).getUTCDate();
 return {code:200,data:Array.from({length:days},(_,i)=>{
  const day=String(i+1).padStart(2,'0'),mo=String(month).padStart(2,'0');
  return {date:{gregorian:{date:`${day}-${mo}-${y}`}},
   meta:{timezone:s.zone,latitude:s.lat,longitude:s.lon,method:{id},school:'STANDARD'},
   timings:Object.fromEntries(keys.map((k,j)=>[k,`${y}-${mo}-${day}T${['05:00','06:00','12:00','15:00','18:00','19:00'][j]}+04:00`]))}
 }))}
}
(async()=>{
 const parsed=parseCalendar(calendar(state,2026,11),state,2026,11);
 assert.equal(Object.keys(parsed.days).length,30,'Legacy offline calendars still parse safely');
 assert.equal(providerTimes(state,{year:2026,month:11,day:21}),null,'No external calendar is loaded');
 const invalid=calendar(state,2026,11);invalid.data[0].meta.latitude=0;
 assert.throws(()=>parseCalendar(invalid,state,2026,11),/wrong-calendar/);
 let networkCalls=0;
 const fetcher=async()=>{networkCalls++;throw Error('Privacy regression: network request');};
 for(const opts of [{},{retryFailed:true}]){
  assert.deepEqual(await refreshProvider(state,{year:2026,month:11,day:21},fetcher,opts),{changed:false,failed:false});
 }
 assert.equal(networkCalls,0,'Even explicit refresh cannot send coordinates');
 assert.equal(timetableRevision(),0);
 console.log('PASS: historical calendar validation retained; remote provider disabled without network access.');
})().catch(e=>{console.error(e);process.exitCode=1});
