const assert=require('node:assert/strict');
const Module=require('node:module'),esbuild=require('esbuild');
function load(path){const m=new Module(path,module);m._compile(esbuild.buildSync({entryPoints:[path],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,path);return m.exports}
const {calculateSchedule,calculateDaySchedule,regionalProfile,resolveCalculationState,calendarParts,PRAYER_KEYS}=load('prayer-engine.js');
const {nativeSchedule}=load('native-adapter.js');
const {cities}=load('cities.js');
const dates=['2026-01-15T12:00:00Z','2026-03-29T12:00:00Z','2026-06-21T12:00:00Z','2026-10-25T12:00:00Z','2026-11-01T12:00:00Z','2027-01-01T12:00:00Z'];
let checked=0,mismatches=0,unknown=0;
const audio={enabled:true,voice:'qatami',volume:.7,dua:true,prayers:{fajr:true,dhuhr:true,asr:true,maghrib:true,isha:true}};
function check(state,now,label){
 const keys=PRAYER_KEYS;
 const tomorrow=calculateSchedule(state,now);
 assert.deepEqual(tomorrow.map(x=>x.key),[...keys,'fajr'],label+' next-day Fajr');
 assert(tomorrow.every(p=>p.time instanceof Date),label+' Date instances');
 const zone=resolveCalculationState(state).zone;
 assert(zone&&typeof zone==='string',label+' timezone');
 let last=-Infinity;
 for(const p of tomorrow.slice(0,6)){
  if(!Number.isFinite(+p.time)){unknown++;continue;}
  assert(+p.time>last,label+' chronological: '+tomorrow.slice(0,6).map(x=>x.key+'='+String(x.time)).join(', '));
  last=+p.time;
 }
 const parts=calendarParts(now,zone);
 const displayed=calculateDaySchedule(state,parts);
 for(let n=0;n<6;n++)assert.equal(+displayed[n].time,+tomorrow[n].time,label+' identical day vs home '+keys[n]);
 const localDay=[parts.year,String(parts.month).padStart(2,'0'),String(parts.day).padStart(2,'0')].join('-');
 const native=nativeSchedule({...state,zone,audio,name:label},now,2);
 const day=native.days.find(d=>d.date===localDay);
 assert(day,label+' native local day');
 for(const p of displayed){
  if(Number.isFinite(+p.time)){
   assert.equal(day[p.key],+p.time,label+' widget and alarm timestamp '+p.key);
   assert(Number.isFinite(day[p.key]),label+' no missing valid prayer');
  }else{
   assert(!Object.hasOwn(day,p.key),label+' do not forge impossible high-latitude times');
  }
 }
 assert(native.events.every(e=>e.prayer!=='sunrise'),label+' sunrise never triggers Adhan');
 for(let n=1;n<native.events.length;n++)assert(native.events[n].time>native.events[n-1].time,label+' Android alarm ordering');
 checked++;
}
for(const city of cities){
 for(let m=0;m<12;m++){
  const date=new Date(Date.UTC(2026,m,15,12));
  const state={lat:city[1],lon:city[2],zone:city[3],method:'Auto',madhab:'Shafi',locationMode:'manual',adjustments:{}};
  check(state,date,city[0]+' month '+m);
 }
}
for(const [label,lat,lon,zone,method] of [
 ['Svalbard',78.2232,15.6267,'Arctic/Longyearbyen','MuslimWorldLeague'],
 ['Tromso',69.6492,18.9553,'Europe/Oslo','MuslimWorldLeague'],
 ['Reykjavik',64.1466,-21.9426,'Atlantic/Reykjavik','MuslimWorldLeague'],
 ['Helsinki',60.1699,24.9384,'Europe/Helsinki','MuslimWorldLeague'],
 ['Kiruna',67.8558,20.2253,'Europe/Stockholm','MuslimWorldLeague'],
 ['Nuuk',64.1814,-51.6941,'America/Nuuk','MuslimWorldLeague'],
 ['Auckland',-36.8485,174.7633,'Pacific/Auckland','MoonsightingCommittee'],
 ['Sydney',-33.8688,151.2093,'Australia/Sydney','MoonsightingCommittee'],
 ['Honolulu',21.3099,-157.8581,'Pacific/Honolulu','NorthAmerica'],
 ['Fiji',-18.1248,178.4501,'Pacific/Fiji','MuslimWorldLeague'],
 ['Tokyo',35.6762,139.6503,'Asia/Tokyo','MuslimWorldLeague'],
 ['Seoul',37.5665,126.9780,'Asia/Seoul','MuslimWorldLeague'],
 ['Santiago',-33.4489,-70.6693,'America/Santiago','MuslimWorldLeague'],
 ['Lima',-12.0464,-77.0428,'America/Lima','MuslimWorldLeague'],
 ['New York',40.7128,-74.006,'America/New_York','NorthAmerica'],
 ['Cairo',30.0444,31.2357,'Africa/Cairo','Egyptian'],
 ['Makkah',21.3891,39.8579,'Asia/Riyadh','UmmAlQura'],
 ['Jakarta',-6.2088,106.8456,'Asia/Jakarta','Kemenag'],
 ['London',51.5072,-.1276,'Europe/London','MuslimWorldLeague'],
 ['Muscat',23.588,58.3829,'Asia/Muscat','Oman'],
 ['Khartoum',15.5007,32.5599,'Africa/Khartoum','MuslimWorldLeague'],
 ['Buenos Aires',-34.6037,-58.3816,'America/Argentina/Buenos_Aires','MuslimWorldLeague']
]){
 for(const iso of dates){
  const state={lat,lon,zone,method,madhab:'Shafi',locationMode:'manual',adjustments:{}};
  check(state,new Date(iso),label+' '+iso);
 }
}
for(const [lat,lon,method] of [[23.588,58.3829,'Oman'],[30.0444,31.2357,'Egyptian'],[25.2048,55.2708,'Dubai'],[40.7128,-74.006,'NorthAmerica'],[-6.2088,106.8456,'Kemenag'],[3.139,101.6869,'Jakim'],[36.8065,10.1815,'Tunisia']]){
 assert.equal(regionalProfile(lat,lon).method,method,'country default at '+lat+','+lon);
}
const state={lat:40.7128,lon:-74.006,zone:'America/New_York',method:'Auto',madhab:'Shafi',locationMode:'manual',adjustments:{}};
const base=calculateSchedule(state,new Date(dates[0])).slice(0,6);
const moved=calculateSchedule({...state,adjustments:{fajr:3,dhuhr:-2,isha:5}},new Date(dates[0])).slice(0,6);
for(let i=0;i<6;i++) assert.equal(+moved[i].time-+base[i].time,([3,0,-2,0,0,5][i])*60000,'manual adjustment '+PRAYER_KEYS[i]);
console.log('PASS worldwide: '+checked+' city/date scenarios; browser, Android widget and native Adhan use identical absolute timestamps.');
console.log('PASS worldwide: UTC dates, DST boundaries, polar sampling, region selection, sunrise exclusion, chronological alarms, six prayer keys, adjustments. '+unknown+' mathematically unavailable prayer times were not fabricated.');
