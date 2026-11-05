'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),os=require('node:os'),Module=require('node:module'),{execFileSync}=require('node:child_process');
const built=require('esbuild').buildSync({entryPoints:['prayer-engine.js'],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text;
const m=new Module('global-calendar-audit',module);m._compile(built,'global-calendar-audit.cjs');const engine=m.exports;
const canonical=z=>new Intl.DateTimeFormat('en',{timeZone:z}).resolvedOptions().timeZone;
for(const c of JSON.parse(fs.readFileSync('tests/fixtures/world-timezone-boundary-cases.json')).mismatches){
 const actual=engine.regionalProfile(c.lat,c.lon).zone;
 assert(c.exact.map(canonical).includes(canonical(actual)),c.name+': exact geographic timezone mismatch '+actual);
}
function civil(time,zone){const p=new Intl.DateTimeFormat('en',{timeZone:zone,year:'numeric',month:'numeric',day:'numeric'}).formatToParts(time);return Object.fromEntries(p.filter(x=>['year','month','day'].includes(x.type)).map(x=>[x.type,+x.value]));}
const boundary=[
 {name:'Kiritimati',lat:1.8721,lon:-157.4278,zone:'Pacific/Kiritimati'},
 {name:'Apia',lat:-13.8333,lon:-171.75,zone:'Pacific/Apia'},
 {name:'Chatham',lat:-43.95,lon:-176.55,zone:'Pacific/Chatham'},
 {name:'Fakaofo',lat:-9.38,lon:-171.25,zone:'Pacific/Fakaofo'},
 {name:'Pago Pago',lat:-14.2756,lon:-170.702,zone:'Pacific/Pago_Pago'},
 {name:'Muscat',lat:23.588,lon:58.3829,zone:'Asia/Muscat'}
].map(c=>({...c,method:'Auto'}));
const dates=[{year:2026,month:1,day:1},{year:2026,month:1,day:15},{year:2026,month:12,day:31},{year:2027,month:1,day:1}];
for(const c of boundary)for(const day of dates){
 const rows=engine.calculateDaySchedule(c,day),noon=rows.find(x=>x.key==='dhuhr');
 assert.deepEqual(civil(noon.time,c.zone),day,c.name+': solar noon belongs to a different local calendar day');
 for(const p of rows)assert.equal(+p.time%60000,0,'Minute rounding drift: '+c.name+'/'+p.key);
 const next=engine.calculateDaySchedule({...c,adjustments:{fajr:1,asr:-2}},day);
 assert.equal(+next[0].time-rows[0].time,60000);assert.equal(+next[3].time-rows[3].time,-120000,'Manual offsets must survive date-line correction');
}
// Verify actual daily solar recomputation, not shifting next-day results24h.
const raw=require('adhan');const k=boundary[0],params=engine.prayerParameters(k,new Date(2026,0,15,12));
const physical=new raw.PrayerTimes(new raw.Coordinates(k.lat,k.lon),new Date(2026,0,14,12),params);
assert.equal(+engine.calculateDaySchedule(k,{year:2026,month:1,day:15})[2].time,+physical.dhuhr,'Recompute the real UTC solar day; daily minute changes must not be copied from tomorrow');

const manifest=JSON.parse(fs.readFileSync('world-data/countries.json')),countries=[],empty=[];
for(const country of manifest.countries){const rows=JSON.parse(fs.readFileSync('dist/world-cities/'+country.code+'.json'));if(!rows.length){empty.push(country.code);continue;}const r=rows[0],profile=engine.regionalProfile(r[1],r[2]);countries.push({name:country.en,code:country.code,lat:r[1],lon:r[2],zone:profile.zone,method:'Auto'});}
const cases=[];for(const c of countries)for(let month=1;month<=12;month++)cases.push({state:c,day:{year:2026,month,day:15}});
for(const c of boundary)for(const day of dates)cases.push({state:c,day});
let finite=0,unavailable=0;
const expected=cases.map(({state,day})=>{
 const rows=engine.calculateDaySchedule(state,day);
 const noon=rows[2];assert.deepEqual(civil(noon.time,state.zone),day,state.name+' wrong civil date');
 for(let i=0;i<rows.length;i++){
  // Adhan's seasonal interpolation may preserve a subsecond remainder;
  // the whole-second clock must still be exactly on its rounded minute.
  if(Number.isFinite(+rows[i].time)){finite++;assert.equal(Math.floor(+rows[i].time/1000)%60,0,state.name+'/'+rows[i].key+' minute rounding');if(i&&Number.isFinite(+rows[i-1].time))assert(+rows[i].time>+rows[i-1].time,state.name+' prayer order');}
  else unavailable++; // Physical polar unavailability is reported, never fabricated.
 }
 return rows.map(p=>Number.isFinite(+p.time)?+p.time:null);
});
const temp=fs.mkdtempSync(path.join(os.tmpdir(),'salati-world-calendar-'));
try{
 const bundle=path.join(temp,'engine.cjs'),input=path.join(temp,'cases.json');fs.writeFileSync(bundle,built);fs.writeFileSync(input,JSON.stringify(cases));
 const worker='const e=require(process.argv[1]),cs=JSON.parse(require("fs").readFileSync(process.argv[2]));process.stdout.write(JSON.stringify(cs.map(({state,day})=>e.calculateDaySchedule(state,day).map(p=>Number.isFinite(+p.time)?+p.time:null))));';
 for(const zone of ['UTC','Pacific/Kiritimati','America/New_York','Asia/Kathmandu','Australia/Adelaide']){
  const actual=JSON.parse(execFileSync(process.execPath,['-e',worker,bundle,input],{env:{...process.env,TZ:zone},maxBuffer:8*1024*1024}));
  assert.deepEqual(actual,expected,'Device timezone changes selected-city prayer instants: '+zone);
 }
}finally{fs.rmSync(temp,{recursive:true,force:true});}
function wall(t,zone){const p=new Intl.DateTimeFormat('en-GB',{timeZone:zone,hour:'numeric',minute:'numeric',hourCycle:'h23'}).formatToParts(t);return +p.find(x=>x.type==='hour').value*60+(+p.find(x=>x.type==='minute').value);}
for(const [c,a,b,jump] of [
 [{lat:40.7128,lon:-74.006,zone:'America/New_York'},[2026,3,7],[2026,3,8],60],
 [{lat:51.5074,lon:-.1278,zone:'Europe/London'},[2026,3,28],[2026,3,29],60],
 [{lat:-33.8688,lon:151.2093,zone:'Australia/Sydney'},[2026,4,4],[2026,4,5],-60]
]){
 const get=d=>engine.calculateDaySchedule({...c,method:'Auto'},{year:d[0],month:d[1],day:d[2]})[1].time;
 const t1=get(a),t2=get(b);assert(Math.abs((+t2-t1)-86400000)<5*60000,'Solar sunrise jumps with DST');assert(Math.abs(wall(t2,c.zone)-wall(t1,c.zone)-jump)<=5,'DST wall clock not applied correctly');
}
const report={countriesWithCities:countries.length,countryFiles:manifest.countries.length,emptyCountryFiles:empty,calendarCases:cases.length,hostTimezones:5,finitePrayerTimes:finite,polarUnavailable:unavailable,dateLineAndYearBoundaries:'PASS',dailySolarRecalculation:'PASS',manualOffsets:'PASS',dst:'PASS',scope:'Mathematical calendar/zone/rounding checks, not minute-perfect official-calendar coverage for every locality.'};
fs.mkdirSync('reports/global-prayer-calendar',{recursive:true});fs.writeFileSync('reports/global-prayer-calendar/results.json',JSON.stringify(report,null,2)+'\n');console.log('PASS global prayer calendar audit',JSON.stringify(report));
