const assert=require('node:assert/strict'),Module=require('node:module'),esbuild=require('esbuild');
const m=new Module('auto-city',module);m._compile(esbuild.buildSync({entryPoints:['prayer-engine.js'],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,'auto-city.cjs');
const {calculateSchedule,resolveCalculationState,timetableSource}=m.exports;
const date=new Date('2026-10-22T08:00:00Z');
const manual={lat:23.588,lon:58.3829,zone:'Asia/Muscat',method:'Auto',locationMode:'manual',adjustments:{fajr:2,asr:1}};
const gps={...manual,lat:23.62,lon:58.15,locationMode:'auto'};
assert.equal(timetableSource(manual,date).kind,'official');
assert.equal(timetableSource(gps,date).kind,'calculated','Do not apply Muscat centre table to remote GPS');
const resolved=resolveCalculationState(gps);
assert.equal(resolved.lat,gps.lat);assert.equal(resolved.lon,gps.lon);
assert.equal(resolved.method,'Oman');
assert.notDeepEqual(calculateSchedule(gps,date).map(x=>+x.time),calculateSchedule(manual,date).map(x=>+x.time),'Different geographical locations must not be silently snapped to the same city');
for(const day of ['2026-10-22T08:00:00Z','2026-10-23T08:00:00Z','2026-11-01T08:00:00Z']){
 const actual=resolveCalculationState({...gps,locationMode:'auto'});assert.equal(actual.lat,gps.lat);assert.equal(actual.lon,gps.lon);
 assert.equal(timetableSource(gps,new Date(day)).kind,'calculated');
}
const remote={lat:0,lon:0,zone:'Etc/GMT',method:'MuslimWorldLeague',madhab:'Shafi',locationMode:'auto'};
assert.equal(resolveCalculationState(remote).lat,0);assert.equal(resolveCalculationState(remote).lon,0);
const cityModule=new Module('cities',module);cityModule._compile(esbuild.buildSync({entryPoints:['cities.js'],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,'cities.cjs');
let count=0,distinct=0;
for(const c of cityModule.exports.cities){
 const anchor={lat:c[1],lon:c[2],zone:c[3],method:'Auto',locationMode:'manual'};
 const detected={...anchor,lat:c[1]+.02,lon:c[2]+.02,locationMode:'auto'};
 const location=resolveCalculationState(detected);
 assert.equal(location.lat,detected.lat,c[0]+' GPS latitude');
 assert.equal(location.lon,detected.lon,c[0]+' GPS longitude');
 const a=calculateSchedule(anchor,date),b=calculateSchedule(detected,date);
 if(a.some((x,i)=>+x.time!==+b[i].time))distinct++;
 count++;
}
assert(distinct>10,'Global regression: precise GPS must produce independent local schedule, not universal city-centre schedules');
console.log('PASS: GPS preserved in '+count+' world cities, '+distinct+' distinct prayer schedules, local Ministry timetable only inside verified Muscat scope.');
