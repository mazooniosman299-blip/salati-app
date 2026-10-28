const assert=require('node:assert/strict'),Module=require('node:module'),esbuild=require('esbuild');
const m=new Module('auto-city',module);m._compile(esbuild.buildSync({entryPoints:['prayer-engine.js'],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,'auto-city.cjs');
const {calculateSchedule,resolveCalculationState,timetableSource}=m.exports;
const date=new Date('2026-10-22T08:00:00Z');
const manual={lat:23.588,lon:58.3829,zone:'Asia/Muscat',method:'Auto',locationMode:'manual',adjustments:{fajr:2,asr:1}};
const gps={...manual,lat:23.62,lon:58.15,locationMode:'auto'};
assert.equal(timetableSource({...gps,locationMode:'manual'},date).kind,'calculated');
assert.equal(timetableSource(manual,date).kind,'official');
assert.equal(timetableSource(gps,date).kind,'official');
assert.deepEqual(calculateSchedule(gps,date),calculateSchedule(manual,date));
assert.equal(gps.lat,23.62);assert.equal(gps.lon,58.15); // compass must keep actual location
for(const [lat,lon,zone] of [[30.0444,31.2357,'Africa/Cairo'],[25.2048,55.2708,'Asia/Dubai'],[51.5074,-.1278,'Europe/London']]){
 const city={lat,lon,zone,method:'Auto',locationMode:'manual'},point={...city,lat:lat+.01,lon:lon+.01,locationMode:'auto'};
 assert.deepEqual(calculateSchedule(point,date),calculateSchedule(city,date));
}
const remote={lat:0,lon:0,zone:'Etc/GMT',method:'MuslimWorldLeague',madhab:'Shafi',locationMode:'auto'};
assert.equal(resolveCalculationState(remote).lat,0);assert.equal(resolveCalculationState(remote).lon,0);
assert.equal(resolveCalculationState({...gps,locationMode:'manual'}).lon,58.15);
for(const day of ['2026-10-21T08:00:00Z','2026-10-22T08:00:00Z','2026-10-23T08:00:00Z','2026-11-01T08:00:00Z'])assert.deepEqual(calculateSchedule(gps,new Date(day)),calculateSchedule(manual,new Date(day)));
const cityModule=new Module('cities',module);cityModule._compile(esbuild.buildSync({entryPoints:['cities.js'],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,'cities.cjs');let count=0;for(const c of cityModule.exports.cities){for(const day of ['2026-10-22T08:00:00Z','2027-03-29T08:00:00Z','2027-07-15T08:00:00Z']){const chosen={lat:c[1],lon:c[2],zone:c[3],method:'Auto',locationMode:'manual'},detected={...chosen,lat:c[1]+.01,lon:c[2]+.01,locationMode:'auto'};assert.deepEqual(calculateSchedule(detected,new Date(day)),calculateSchedule(chosen,new Date(day)),c[0]+' '+day);count++}}console.log('PASS: '+count+' auto/manual schedule comparisons across all '+cityModule.exports.cities.length+' cities, including seasonal and DST dates.');console.log('PASS: reproduced Muscat GPS/calendar mismatch; auto/manual city calendars now match across dates and regions; actual GPS, remote locations, explicit coordinates and minute adjustments preserved.');
