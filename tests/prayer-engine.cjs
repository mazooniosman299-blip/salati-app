const assert=require('node:assert/strict');const fs=require('node:fs');const Module=require('node:module');const built=require('esbuild').buildSync({entryPoints:['prayer-engine.js'],bundle:true,platform:'node',format:'cjs',write:false});const engine=new Module('prayer-engine-test',module);engine._compile(built.outputFiles[0].text,'prayer-engine-test.cjs');const{calculateSchedule,regionalProfile,timetableSource}=engine.exports;const cities=JSON.parse(fs.readFileSync('cities.js','utf8').replace('export const cities=','').replace(/;\s*$/,''));
const muscat={lat:23.588,lon:58.3829,method:'Auto'};const format=t=>new Intl.DateTimeFormat('en-GB',{timeZone:'Asia/Muscat',hour:'2-digit',minute:'2-digit'}).format(t);
assert.deepEqual(calculateSchedule(muscat,new Date('2026-10-21T08:00:00Z')).slice(0,6).map(p=>format(p.time)),['04:51','06:07','11:57','15:15','17:42','18:52']);
assert.equal(timetableSource(muscat,new Date('2026-10-21T08:00:00Z')).kind,'custom');assert.equal(timetableSource(muscat,new Date('2026-11-01T08:00:00Z')).kind,'calculated');assert.equal(timetableSource({...muscat,lat:17.0194,lon:54.1108},new Date('2026-10-21T08:00:00Z')).kind,'calculated');
assert.notDeepEqual(calculateSchedule(muscat,new Date('2026-10-21T08:00:00Z')).slice(0,6).map(p=>format(p.time)),calculateSchedule(muscat,new Date('2026-10-22T08:00:00Z')).slice(0,6).map(p=>format(p.time)));
const adjusted=calculateSchedule({...muscat,adjustments:{asr:1}},new Date('2026-10-21T08:00:00Z'));assert.equal(format(adjusted[3].time),'15:16');
assert.equal(regionalProfile(23.588,58.3829).method,'Oman');assert.equal(regionalProfile(36.8065,10.1815).method,'Tunisia');assert.equal(regionalProfile(-6.2088,106.8456).method,'Kemenag');assert.equal(regionalProfile(3.139,101.6869).method,'Jakim');assert.equal(regionalProfile(40.7128,-74.006).method,'NorthAmerica');
const savedMinuteOffsets=calculateSchedule({...muscat,adjustments:{fajr:1,sunrise:1}},new Date('2026-10-21T08:00:00Z'));assert.deepEqual(savedMinuteOffsets.slice(0,6).map(p=>format(p.time)),['04:52','06:08','11:57','15:15','17:42','18:52']);
for(const [lat,lon] of [[23.4,58.14],[23.6,58.12],[23.67,58.14],[23.68,58.18]]){const western={...muscat,lat,lon};assert.deepEqual(calculateSchedule(western,new Date('2026-10-21T08:00:00Z')).slice(0,6).map(p=>format(p.time)),['04:51','06:07','11:57','15:15','17:42','18:52']);assert.equal(timetableSource(western,new Date('2026-10-21T08:00:00Z')).kind,'custom')}
assert.equal(timetableSource({...muscat,lat:23.68,lon:57.89},new Date('2026-10-21T08:00:00Z')).kind,'calculated');
// Ministry fixture values are intentionally independent of the production calendar file.
// Source: https://www.mara.gov.om/arabic/calendar_page2.asp (Muscat, Nov 2026).
for(const [date,expected] of [
 ['2026-11-01',['04:56','06:12','11:55','15:09','17:34','18:45']],
 ['2026-11-07',['04:59','06:16','11:56','15:07','17:30','18:42']],
 ['2026-11-15',['05:03','06:21','11:56','15:05','17:27','18:40']],
 ['2026-11-30',['05:12','06:31','12:00','15:04','17:24','18:39']]
]){
 const [y,m,d]=date.split('-').map(Number),now=new Date(Date.UTC(y,m-1,d,12));
 assert.deepEqual(calculateSchedule(muscat,now).slice(0,6).map(p=>format(p.time)),expected,'Official Muscat '+date);
 assert.equal(timetableSource(muscat,now).kind,'official','Official Muscat source '+date);
}
assert.equal(timetableSource(muscat,new Date('2026-12-07T12:00:00Z')).kind,'calculated','Never pretend unverified December data is official');
assert.equal(timetableSource({...muscat,lat:23.588,lon:58.9},new Date('2026-11-07T12:00:00Z')).kind,'calculated','Do not reuse Muscat calendar 50km away');
assert.equal(timetableSource({...muscat,method:'MuslimWorldLeague',madhab:'Shafi'},new Date('2026-11-07T12:00:00Z')).kind,'calculated','Explicit user method must be honored');
assert.deepEqual(calculateSchedule({...muscat,adjustments:{fajr:1,maghrib:2}},new Date('2026-11-07T12:00:00Z')).slice(0,6).map(p=>format(p.time)),['05:00','06:16','11:56','15:07','17:32','18:42'],'User offsets applied precisely once after official calendar');
for(const [city,lat,lon] of [['London',51.5074,-0.1278],['New York',40.7128,-74.006],['Sydney',-33.8688,151.2093],['Karachi',24.8607,67.0011],['Kuala Lumpur',3.139,101.6869],['Jakarta',-6.2088,106.8456],['Istanbul',41.0082,28.9784],['Makkah',21.3891,39.8579],['Kathmandu',27.7172,85.324],['Kiritimati',1.8721,-157.4278]]){
 const location={lat,lon,method:'Auto'};
 for(const iso of ['2026-03-29','2026-07-15','2026-11-07','2026-12-31']){
  const now=new Date(iso+'T12:00:00Z');
  const times=calculateSchedule(location,now).slice(0,6).map(x=>+x.time);
  assert(times.every(Number.isFinite),'Finite times '+city+' '+iso);
  assert(times.every((t,i)=>!i||t>times[i-1]),'Chronological times '+city+' '+iso);
  assert.equal(timetableSource(location,now).kind,'calculated','Do not label an unverified national calendar as official: '+city);
 }
}
let checked=0,missing=0;for(const c of cities){const state={lat:c[1],lon:c[2],method:'Auto'};for(let month=0;month<12;month++){const rows=calculateSchedule(state,new Date(Date.UTC(2026,month,15,12)));for(let i=0;i<6;i++){if(!Number.isFinite(+rows[i].time)){missing++;continue}if(i&&Number.isFinite(+rows[i-1].time))assert.ok(rows[i].time>=rows[i-1].time,c[0]+' sequence month '+month)}checked++;}}
assert.equal(missing,0);console.log(checked+' city/date schedules checked, across '+cities.length+' cities; chronological and finite.');console.log('Official Muscat sample, next-date change, expiry/geography guards, manual adjustment and regional profiles pass.');
