// Sunrise/Isha source-gate regression: run against candidate BEFORE making fixes.
const assert=require('node:assert/strict');
const Module=require('node:module'),esbuild=require('esbuild');
const built=esbuild.buildSync({entryPoints:['prayer-engine.js'],bundle:true,platform:'node',format:'cjs',write:false});
const mod=new Module('sunrise-isha-provenance',module);
mod._compile(built.outputFiles[0].text,'sunrise-isha-provenance.cjs');
const {calculateDaySchedule,timetableSource}=mod.exports;
const muscat={lat:23.588,lon:58.3829,zone:'Asia/Muscat',method:'Oman',madhab:'Shafi',adjustments:{}};
const singapore={lat:1.3521,lon:103.8198,zone:'Asia/Singapore',method:'Singapore',madhab:'Shafi',adjustments:{}};
const instant=new Date('2026-11-07T12:00:00Z'),day={year:2026,month:11,day:7};
const local=(s)=>Object.fromEntries(calculateDaySchedule(s,day).map(({key,time})=>[key,new Intl.DateTimeFormat('en-GB',{timeZone:s.zone,hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).format(time)]));
const verified=[
 [muscat,{sunrise:'06:16',isha:'18:42'}],
 [singapore,{sunrise:'06:47',isha:'20:03'}]
];
for(const [s,expected] of verified){
 const regular=local(s),hanafi=local({...s,madhab:'Hanafi'});
 console.log('BEFORE_FIX',JSON.stringify({method:s.method,regular:{sunrise:regular.sunrise,isha:regular.isha,asr:regular.asr},hanafi:{sunrise:hanafi.sunrise,isha:hanafi.isha,asr:hanafi.asr},expected}));
}
console.log('BEFORE_FIX_FOREIGN_ZONE',timetableSource({...muscat,zone:'Europe/London',zoneMode:'manual'},instant).kind);
for(const [s,expected] of verified){
 assert.equal(timetableSource(s,instant).kind,'official');
 for(const [key,want] of Object.entries(expected))assert.equal(local(s)[key],want,s.method+' official '+key);
 const hanafi={...s,madhab:'Hanafi'};
 // Hanafi alters only Asr; sunrise and Isha must still use the same verified local authority.
 for(const [key,want] of Object.entries(expected))assert.equal(local(hanafi)[key],want,s.method+' Hanafi must not change '+key);
 assert.equal(timetableSource(hanafi,instant).kind,'custom',s.method+' must disclose calculated Hanafi Asr');
}
// Exhaustive authority regression: 30 Oman November dates and all 365 MUIS dates.
const fs=require('node:fs');
const omRows=JSON.parse(fs.readFileSync('official-muscat.js','utf8').split('export const MUSCAT_NOVEMBER_2026=')[1].split(';')[0]);
const sgRows=JSON.parse(fs.readFileSync('official-singapore.js','utf8').split('export const SINGAPORE_MUIS_2026=')[1].split(';')[0]);
const minuteText=n=>String(Math.floor(n/60)).padStart(2,'0')+':'+String(n%60).padStart(2,'0');
let verifiedDates=0;
for(const [st,days] of [
 [muscat,Object.entries(omRows).map(([day,minutes])=>({p:{year:2026,month:11,day:+day},minutes}))],
 [singapore,Object.entries(sgRows).map(([key,minutes])=>{const [y,m,d]=key.split('-').map(Number);return {p:{year:y,month:m,day:d},minutes}})]
]){
 for(const {p,minutes} of days){
  const hanafi={...st,madhab:'Hanafi'};
  const calculated=Object.fromEntries(calculateDaySchedule(hanafi,p).map(({key,time})=>[key,new Intl.DateTimeFormat('en-GB',{timeZone:st.zone,hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).format(time)]));
  assert.equal(calculated.sunrise,minuteText(minutes[1]),st.method+' Hanafi sunrise '+JSON.stringify(p));
  assert.equal(calculated.isha,minuteText(minutes[5]),st.method+' Hanafi Isha '+JSON.stringify(p));
  verifiedDates++;
 }
}
assert.equal(verifiedDates,395,'No skipped date in protected authority ranges');
console.log('PASS: all '+verifiedDates+' official dates preserve correct sunrise and Isha under Hanafi school.');
// Android's actual synchronized timetable must use the same corrected times.
const adapter=new Module('sunrise-isha-android',module);
adapter._compile(esbuild.buildSync({entryPoints:['native-adapter.js'],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,'sunrise-isha-android.cjs');
const {nativeSchedule}=adapter.exports;
for(const [st,expected] of verified){
 const hanafi={...st,madhab:'Hanafi',audio:{enabled:true,prayers:{fajr:true,dhuhr:true,asr:true,maghrib:true,isha:true},voice:'default',volume:1,dua:false,silentMode:true}};
 const payload=nativeSchedule(hanafi,instant,1);
 const row=payload.days.find(d=>d.date==='2026-11-07');
 assert(row,'Android timed alarms must contain day 7');
 for(const [key,want] of Object.entries(expected)){
  assert.equal(new Intl.DateTimeFormat('en-GB',{timeZone:st.zone,hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).format(new Date(row[key])),want,'Android date-alarm mismatch '+st.method+'/'+key);
 }
 assert(payload.events.some(e=>e.prayer==='isha'&&e.time===row.isha),'Isha Android event must use the verified authority timestamp');
 assert(!payload.events.some(e=>e.prayer==='sunrise'),'Sunrise must never become an Adhan alarm');
}
const fakeMuscatZone={...muscat,zone:'Europe/London',zoneMode:'manual'};
assert.equal(timetableSource(fakeMuscatZone,instant).kind,'calculated',
 'A manual foreign timezone must not be falsely labelled official Oman civil time');
const seeb={...muscat,lat:23.67027,lon:58.18911};
assert.equal(timetableSource(seeb,instant).kind,'calculated',
 'Seeb lacks Ministry city calendar. Do not describe Muscat timings as official for Seeb');
console.log('PASS authoritative Sunrise/Isha identical across Asr schools, timezone and Seeb provenance gates.');
