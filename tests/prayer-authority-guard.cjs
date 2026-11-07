'use strict';
// Fail closed on known prayer-time regressions. Never assert worldwide authority
// coverage from astronomical arithmetic alone.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const Module=require('node:module');
const esbuild=require('esbuild');
function bundle(file){
 const m=new Module(file,module);
 m._compile(esbuild.buildSync({entryPoints:[file],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,file+'.cjs');
 return m.exports;
}
const e=bundle('prayer-engine.js');
const {nativeSchedule}=bundle('native-adapter.js');
const muscat={lat:23.588,lon:58.3829,zone:'Asia/Muscat',method:'Oman',madhab:'Shafi',locationMode:'manual',adjustments:{}};
const singapore={lat:1.3521,lon:103.8198,zone:'Asia/Singapore',method:'Singapore',madhab:'Shafi',locationMode:'manual',adjustments:{}};
const kualaLumpur={lat:3.139,lon:101.6869,zone:'Asia/Kuala_Lumpur',method:'Jakim',madhab:'Shafi',locationMode:'manual',adjustments:{}};
const cairo={lat:30.0444,lon:31.2357,zone:'Africa/Cairo',method:'Egyptian',madhab:'Shafi',locationMode:'manual',adjustments:{}};
const keys=['fajr','sunrise','dhuhr','asr','maghrib','isha'];
const day={year:2026,month:11,day:7},instant=new Date('2026-11-07T08:00:00Z');
const pad=n=>String(n).padStart(2,'0');
const clock=n=>pad(Math.floor(n/60))+':'+pad(n%60);
const wall=(t,z)=>new Intl.DateTimeFormat('en-GB',{timeZone:z,hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).format(t);
function shown(s,d=day){
 return Object.fromEntries(e.calculateDaySchedule(s,d).map(p=>[p.key,wall(p.time,s.zone)]));
}
const expected={
 muscat:['04:59','06:16','11:56','15:07','17:30','18:42'],
 singapore:['05:27','06:47','12:50','16:11','18:51','20:03'],
 kualaLumpur:['05:48','06:56','13:00','16:21','18:58','20:10'],
 cairo:['04:45','06:13','11:39','14:41','17:03','18:23']
};
for(const [city,s] of [['muscat',muscat],['singapore',singapore],['kualaLumpur',kualaLumpur],['cairo',cairo]]){
 assert.deepEqual(keys.map(k=>shown(s)[k]),expected[city],city+' must match published authority exactly');
 assert.equal(e.timetableSource(s,instant).kind,'official',city+' official provenance');
 assert.equal(e.timetableSource({...s,madhab:'Hanafi'},instant).kind,'custom',city+' mixed Asr provenance');
 for(const k of keys.filter(k=>k!=='asr'))assert.equal(shown({...s,madhab:'Hanafi'})[k],shown(s)[k],city+' Asr school must not alter '+k);
 const changes={sunrise:2,isha:-3};
 const adjusted=shown({...s,adjustments:changes});
 const original=e.calculateDaySchedule(s,day);
 assert.equal(adjusted.sunrise,wall(new Date(+original[1].time+120000),s.zone),city+' sunrise preference');
 assert.equal(adjusted.isha,wall(new Date(+original[5].time-180000),s.zone),city+' Isha preference');
 const payload=nativeSchedule({...s,audio:{enabled:true,prayers:{fajr:true,dhuhr:true,asr:true,maghrib:true,isha:true},silentMode:true,volume:1}},instant,1);
 const androidDay=payload.days.find(d=>d.date==='2026-11-07');
 assert(androidDay,city+' Android schedule omitted local date');
 assert.equal(wall(new Date(androidDay.isha),s.zone),expected[city][5],city+' Android Isha mismatch');
 assert(!payload.events.some(x=>x.prayer==='sunrise'),city+' sunrise must not become an Adhan alarm');
}
const min2time=n=>clock(n);
const nov=JSON.parse(fs.readFileSync('official-muscat.js','utf8').split('export const MUSCAT_NOVEMBER_2026=')[1].split(';')[0]);
const sg=JSON.parse(fs.readFileSync('official-singapore.js','utf8').split('export const SINGAPORE_MUIS_2026=')[1].split(';')[0]);
const wly=JSON.parse(fs.readFileSync('official-malaysia-wly01.js','utf8').split('export const WLY01_NOVEMBER_2026=')[1].split(';')[0]);
const egypt=JSON.parse(fs.readFileSync('official-cairo.js','utf8').split('export const CAIRO_NOVEMBER_2026=')[1].split(';')[0]);
assert.equal(Object.keys(nov).length,30,'Missing November Muscat official day');
assert.equal(Object.keys(sg).length,365,'Missing 2026 Singapore official day');
assert.equal(Object.keys(wly).length,30,'Missing November Malaysian WLY01 official day');
assert.equal(Object.keys(egypt).length,30,'Missing November Cairo official day');
assert.equal(e.prayerParameters(kualaLumpur,new Date('2026-11-07T12:00Z')).fajrAngle,18,'Malaysia JAKIM dawn must use official 18 degree rule, not obsolete 20');
for(let i=1;i<=30;i++){
 const rows=e.calculateDaySchedule(muscat,{year:2026,month:11,day:i});
 assert.deepEqual(rows.map(x=>wall(x.time,muscat.zone)),nov[i].map(min2time),'Muscat day '+i);
}
for(let i=1;i<=30;i++){
 const rows=e.calculateDaySchedule(kualaLumpur,{year:2026,month:11,day:i});
 assert.deepEqual(rows.map(x=>wall(x.time,kualaLumpur.zone)),wly[i].map(min2time),'JAKIM WLY01 day '+i);
}
for(let i=1;i<=30;i++){
 const rows=e.calculateDaySchedule(cairo,{year:2026,month:11,day:i});
 assert.deepEqual(rows.map(x=>wall(x.time,cairo.zone)),egypt[i].map(min2time),'Cairo day '+i);
}
for(const [date,minutes] of Object.entries(sg)){
 const [year,month,day]=date.split('-').map(Number);
 const rows=e.calculateDaySchedule(singapore,{year,month,day});
 assert.deepEqual(rows.map(x=>wall(x.time,singapore.zone)),minutes.map(min2time),'Singapore '+date);
}
const nonMuscat=[
 {...muscat,lat:23.67,lon:58.19},
 {...muscat,locationMode:'city-calendar',authorityLat:23.67,authorityLon:58.19},
 {...muscat,zone:'Asia/Dubai',zoneMode:'manual'},
 {...muscat,lat:17.0194,lon:54.1108}
];
for(const s of nonMuscat)assert.equal(e.timetableSource(s,instant).kind,'calculated','Do not falsely claim Muscat ministry authority');
assert.equal(e.timetableSource(muscat,new Date('2026-12-07T08:00:00Z')).kind,'calculated','Do not reuse November authority outside verified date');
assert.equal(e.timetableSource(singapore,new Date('2027-01-07T08:00:00Z')).kind,'calculated','Do not reuse 2026 Singapore table in 2027');
assert.equal(e.timetableSource(kualaLumpur,new Date('2026-12-07T08:00:00Z')).kind,'calculated','Do not reuse Malaysia November table in December');
assert.equal(e.timetableSource(cairo,new Date('2026-12-07T08:00:00Z')).kind,'calculated','Do not reuse Cairo November table in December');
assert.equal(e.timetableSource({...cairo,lat:30.16,lon:31.4},instant).kind,'calculated','Never label all Greater Cairo as Cairo-center official');
assert.equal(e.timetableSource({...kualaLumpur,lat:3.1,lon:101.6},instant).kind,'calculated','Never claim WLY01 for neighboring Malaysian locations without zone proof');
assert.equal(e.timetableSource({...kualaLumpur,locationMode:'auto',lat:3.1391,lon:101.687},instant).kind,'official','Near-KL real GPS should be eligible for correct official zone');
assert.equal(e.timetableSource({...muscat,locationMode:'auto',lat:23.5881,lon:58.383},instant).kind,'official','Near-Muscat real GPS should retain official source');
assert.equal(e.timetableSource({...muscat,locationMode:'auto',lat:23.67,lon:58.19},instant).kind,'calculated','Raw Seeb GPS must never be disguised as Muscat official');
assert.equal(e.timetableSource({...singapore,lat:1.4927,lon:103.7414},instant).kind,'calculated','Never apply Singapore calendar in Johor');
assert.equal(e.timetableSource({...singapore,zone:'Asia/Kuala_Lumpur'},instant).kind,'calculated','Never claim Singapore civil authority in unrelated zone');
// Verify that the ACTUAL app display uses 12-hour time without changing instants.
const src=fs.readFileSync('app-source.js','utf8');
const a=src.indexOf('function timeParts(t){'),b=src.indexOf('let refreshingCalendar=',a);
assert(a>=0&&b>a,'Cannot inspect real app clock formatter');
function uiTime(date,zone,lang){
 return vm.runInNewContext(src.slice(a,b)+'\ntimeParts(now)',{Intl,state:{zone,lang},now:date});
}
for(const [s,exp] of [[muscat,{fajr:'4:59',sunrise:'6:16',dhuhr:'11:56',asr:'3:07',maghrib:'5:30',isha:'6:42'}],[singapore,{fajr:'5:27',sunrise:'6:47',dhuhr:'12:50',asr:'4:11',maghrib:'6:51',isha:'8:03'}],[kualaLumpur,{fajr:'5:48',sunrise:'6:56',dhuhr:'1:00',asr:'4:21',maghrib:'6:58',isha:'8:10'}],[cairo,{fajr:'4:45',sunrise:'6:13',dhuhr:'11:39',asr:'2:41',maghrib:'5:03',isha:'6:23'}]]){
 for(const p of e.calculateDaySchedule(s,day)){
  const show=uiTime(p.time,s.zone,'ar');
  assert.equal(show.clock,exp[p.key],s.zone+' '+p.key+' must display 12-hour clock');
  const localHour=Number(new Intl.DateTimeFormat('en-GB',{timeZone:s.zone,hour:'2-digit',hourCycle:'h23'}).format(p.time));
  assert.equal(show.period,localHour>=12?'مساءً':'صباحًا',s.zone+' AM/PM error '+p.key);
 }
}
console.log('PASS: 455 source-authority dates, 12-hour rendered clock, 4 local zones, Hanafi Asr isolation, Android Isha alarm, manual offsets, geography/date expiry, no sunrise Adhan.');
