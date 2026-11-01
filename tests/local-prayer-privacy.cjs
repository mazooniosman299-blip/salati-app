const assert=require('node:assert/strict'),fs=require('node:fs'),Module=require('node:module');
const engineSource=fs.readFileSync('prayer-engine.js','utf8');
const providerSource=fs.readFileSync('prayer-provider.js','utf8');
const appSource=fs.readFileSync('app-source.js','utf8');
const privacy=fs.readFileSync('dist/privacy.html','utf8');
const html=fs.readFileSync('dist/index.html','utf8');
assert(!engineSource.includes("from './prayer-provider.js'"),'No remote provider in runtime engine');
assert(!providerSource.includes('fetcher('),'Retired provider must not send any request');
assert(!providerSource.includes('api.aladhan.com/v1/calendar'),'Retired provider must not retain coordinate-bearing API URL');
assert(appSource.includes("removeItem('salati-prayer-calendars-v1')"),'Remove old exact-coordinate provider cache');
assert(privacy.includes('لا يرسل صلاتي إحداثيات')&&privacy.includes('does not send your coordinates'));
assert(html.includes('لا يرسل التطبيق الإحداثيات')&&html.includes('coordinates and prayer calculation settings are not sent'));
const compiled=require('esbuild').buildSync({entryPoints:['prayer-engine.js'],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text;
assert(!compiled.includes('api.aladhan.com'),'No remote provider URL in production prayer engine');
const m=new Module('local-prayers',module);m._compile(compiled,'local-prayers.cjs');
const {calculateSchedule,calculateDaySchedule,refreshTimetables}=m.exports;
const locations=[
 {lat:23.588,lon:58.3829,zone:'Asia/Muscat',method:'Oman',madhab:'Shafi'},
 {lat:30.0444,lon:31.2357,zone:'Africa/Cairo',method:'Egyptian',madhab:'Shafi'},
 {lat:40.7128,lon:-74.006,zone:'America/New_York',method:'NorthAmerica',madhab:'Shafi'},
 {lat:24.86,lon:67.01,zone:'Asia/Karachi',method:'Karachi',madhab:'Hanafi'}
];
(async()=>{
 const oldFetch=globalThis.fetch;
 let calls=0;globalThis.fetch=async()=>{calls++;throw Error('Unexpected external network request')};
 try{
  for(const s of locations){
   const now=new Date('2026-11-01T08:00:00Z');
   const entries=calculateSchedule(s,now);
   assert.equal(entries.length,7);
   assert(entries.every(x=>Number.isFinite(+x.time)),'Local astronomical prayer times remain valid');
   const fixed=calculateDaySchedule({...s,adjustments:{fajr:3}},{year:2026,month:11,day:1});
   const base=calculateDaySchedule(s,{year:2026,month:11,day:1});
   assert.equal(+fixed[0].time-+base[0].time,180000,'User minute adjustments retained');
   const customFetcher=async()=>{calls++;throw Error('Remote provider should not be called')};
   assert.deepEqual(await refreshTimetables(s,now,customFetcher,{retryFailed:true}),{changed:false,failed:false});
  }
  assert.equal(calls,0,'No external network requests even during manual refresh');
 }finally{if(oldFetch===undefined)delete globalThis.fetch;else globalThis.fetch=oldFetch;}
 console.log('PASS: local-only prayer calculations, method choice, offsets and zero coordinate-bearing network calls.');
})().catch(e=>{console.error(e);process.exitCode=1});
