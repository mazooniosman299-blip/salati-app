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
 assert.equal(timetableSource(s,instant).kind,'official');
 for(const [key,want] of Object.entries(expected))assert.equal(local(s)[key],want,s.method+' official '+key);
 const hanafi={...s,madhab:'Hanafi'};
 // Hanafi alters only Asr; sunrise and Isha must still use the same verified local authority.
 for(const [key,want] of Object.entries(expected))assert.equal(local(hanafi)[key],want,s.method+' Hanafi must not change '+key);
 assert.equal(timetableSource(hanafi,instant).kind,'custom',s.method+' must disclose calculated Hanafi Asr');
}
const fakeMuscatZone={...muscat,zone:'Europe/London',zoneMode:'manual'};
assert.equal(timetableSource(fakeMuscatZone,instant).kind,'calculated',
 'A manual foreign timezone must not be falsely labelled official Oman civil time');
const seeb={...muscat,lat:23.67027,lon:58.18911};
assert.equal(timetableSource(seeb,instant).kind,'calculated',
 'Seeb lacks Ministry city calendar. Do not describe Muscat timings as official for Seeb');
console.log('PASS authoritative Sunrise/Isha identical across Asr schools, timezone and Seeb provenance gates.');
