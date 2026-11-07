const assert=require('node:assert/strict');const fs=require('node:fs');const Module=require('node:module');const built=require('esbuild').buildSync({entryPoints:['prayer-engine.js'],bundle:true,platform:'node',format:'cjs',write:false});const engine=new Module('prayer-engine-test',module);engine._compile(built.outputFiles[0].text,'prayer-engine-test.cjs');const{calculateSchedule,calculateDaySchedule,resolveCalculationState,regionalProfile,timetableSource}=engine.exports;const cities=JSON.parse(fs.readFileSync('cities.js','utf8').replace('export const cities=','').replace(/;\s*$/,''));
const muscat={lat:23.588,lon:58.3829,method:'Auto'};const format=t=>new Intl.DateTimeFormat('en-GB',{timeZone:'Asia/Muscat',hour:'2-digit',minute:'2-digit'}).format(t);
assert.deepEqual(calculateSchedule(muscat,new Date('2026-10-21T08:00:00Z')).slice(0,6).map(p=>format(p.time)),['04:51','06:07','11:57','15:15','17:42','18:52']);
assert.equal(timetableSource(muscat,new Date('2026-10-21T08:00:00Z')).kind,'custom');assert.equal(timetableSource(muscat,new Date('2026-11-01T08:00:00Z')).kind,'official');assert.equal(timetableSource(muscat,new Date('2026-12-01T08:00:00Z')).kind,'calculated');assert.equal(timetableSource({...muscat,lat:17.0194,lon:54.1108},new Date('2026-10-21T08:00:00Z')).kind,'calculated');
assert.notDeepEqual(calculateSchedule(muscat,new Date('2026-10-21T08:00:00Z')).slice(0,6).map(p=>format(p.time)),calculateSchedule(muscat,new Date('2026-10-22T08:00:00Z')).slice(0,6).map(p=>format(p.time)));
const adjusted=calculateSchedule({...muscat,adjustments:{asr:1}},new Date('2026-10-21T08:00:00Z'));assert.equal(format(adjusted[3].time),'15:16');
assert.equal(regionalProfile(23.588,58.3829).method,'Oman');assert.equal(regionalProfile(36.8065,10.1815).method,'Tunisia');assert.equal(regionalProfile(-6.2088,106.8456).method,'Kemenag');assert.equal(regionalProfile(3.139,101.6869).method,'Jakim');assert.equal(regionalProfile(40.7128,-74.006).method,'NorthAmerica');
const savedMinuteOffsets=calculateSchedule({...muscat,adjustments:{fajr:1,sunrise:1}},new Date('2026-10-21T08:00:00Z'));assert.deepEqual(savedMinuteOffsets.slice(0,6).map(p=>format(p.time)),['04:52','06:08','11:57','15:15','17:42','18:52']);
for(const [lat,lon] of [[23.4,58.14],[23.6,58.12],[23.67,58.14],[23.68,58.18]]){const western={...muscat,lat,lon};const kind=timetableSource(western,new Date('2026-10-21T08:00:00Z')).kind;assert.equal(kind,'calculated','GPS coordinates outside 20km must not borrow the official city-centre calendar')}
assert.equal(timetableSource({...muscat,lat:23.68,lon:57.89},new Date('2026-10-21T08:00:00Z')).kind,'calculated');

// All 30 rows are from the actual Ministry timetable, not a fitted day-7 offset.
const officialNov=require('node:fs').readFileSync('official-muscat.js','utf8');
const officialRows=JSON.parse(officialNov.split('export const MUSCAT_NOVEMBER_2026=')[1].split(';')[0]);
assert.equal(Object.keys(officialRows).length,30,'Must ship all November ministry dates');
for(let day=1;day<=30;day++){
 const actual=calculateDaySchedule(muscat,{year:2026,month:11,day}).map(p=>format(p.time));
 const expected=officialRows[day].map(min=>String(Math.floor(min/60)).padStart(2,'0')+':'+String(min%60).padStart(2,'0'));
 assert.deepEqual(actual,expected,'Ministry timetable mismatch on 2026-11-'+day);
}
assert.deepEqual(calculateDaySchedule(muscat,{year:2026,month:11,day:7}).map(p=>format(p.time)),['04:59','06:16','11:56','15:07','17:30','18:42']);
const geolocated={lat:23.68,lon:58.18,method:'Auto',locationMode:'auto',zone:'Asia/Muscat',zoneMode:'auto'};
const actualGPS=resolveCalculationState(geolocated);
assert.equal(actualGPS.lat,geolocated.lat,'GPS latitude must not be replaced with Muscat centre');
assert.equal(actualGPS.lon,geolocated.lon,'GPS longitude must not be replaced with Muscat centre');
assert.equal(actualGPS.method,'Oman');
assert.equal(timetableSource(geolocated,new Date('2026-11-07T08:00:00Z')).kind,'calculated','Outside verified city scope must not claim official timetable');

let checked=0,missing=0;for(const c of cities){const state={lat:c[1],lon:c[2],method:'Auto'};for(let month=0;month<12;month++){const rows=calculateSchedule(state,new Date(Date.UTC(2026,month,15,12)));for(let i=0;i<6;i++){if(!Number.isFinite(+rows[i].time)){missing++;continue}if(i&&Number.isFinite(+rows[i-1].time))assert.ok(rows[i].time>=rows[i-1].time,c[0]+' sequence month '+month)}checked++;}}
assert.equal(missing,0);console.log(checked+' city/date schedules checked, across '+cities.length+' cities; chronological and finite.');console.log('Official Muscat sample, next-date change, expiry/geography guards, manual adjustment and regional profiles pass.');
