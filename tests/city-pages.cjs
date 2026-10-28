const assert=require('node:assert/strict'),fs=require('node:fs'),Module=require('node:module'),esbuild=require('esbuild');
function load(entry){const m=new Module(entry,module);m._compile(esbuild.buildSync({entryPoints:[entry],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,entry+'.cjs');return m.exports}
const {cityTimetable,cityWeek}=load('city-pages/timetable.js');const engine=load('prayer-engine.js');
const {PrayerTimes,Coordinates,CalculationMethod,Madhab,HighLatitudeRule}=require('adhan');
const cities=require('../city-pages/cities.json');
const expected={makkah:['Asia/Riyadh','UmmAlQura'],cairo:['Africa/Cairo','Egyptian'],london:['Europe/London','MuslimWorldLeague'],'new-york':['America/New_York','NorthAmerica'],jakarta:['Asia/Jakarta','Kemenag'],muscat:['Asia/Muscat','Oman'],khartoum:['Africa/Khartoum','Egyptian'],riyadh:['Asia/Riyadh','UmmAlQura'],madinah:['Asia/Riyadh','UmmAlQura'],jeddah:['Asia/Riyadh','UmmAlQura'],dubai:['Asia/Dubai','Dubai'],'abu-dhabi':['Asia/Dubai','Dubai'],doha:['Asia/Qatar','Qatar']};
let checked=0;
for(const c of cities){
 for(const instant of ['2026-01-15T12:00Z','2026-06-15T12:00Z','2026-03-08T12:00Z','2026-03-29T12:00Z','2026-10-25T12:00Z','2026-11-01T12:00Z','2026-04-24T12:00Z','2026-10-30T12:00Z']){
  const now=new Date(instant),view=cityTimetable(c,now),p=engine.calendarParts(now,view.state.zone);
  assert.deepEqual([view.state.zone,view.state.method],expected[c.slug]);
  assert.equal(view.date,`${p.year}-${String(p.month).padStart(2,'0')}-${String(p.day).padStart(2,'0')}`);
  assert.deepEqual(view.rows,engine.calculateSchedule({lat:c.lat,lon:c.lon,method:'Auto'},now).slice(0,6));
  // Compare with the underlying Adhan implementation configured independently.
  const d=new Date(p.year,p.month-1,p.day,12);
  let params;
  if(c.slug==='jakarta'){params=CalculationMethod.Other();params.fajrAngle=20;params.ishaAngle=18}
  else if(c.slug==='muscat'){params=CalculationMethod.Other();params.fajrAngle=18;params.ishaAngle=18;Object.assign(params.methodAdjustments,{sunrise:1,dhuhr:5,asr:5,maghrib:5});}
  else params=CalculationMethod[view.state.method]();
  params.madhab=Madhab.Shafi;params.highLatitudeRule=HighLatitudeRule.recommended(new Coordinates(c.lat,c.lon));
  // March 8, 2026 falls in Ramadan: the engine uses a 120-minute Isha interval.
  if(view.state.method==='UmmAlQura' && instant.startsWith('2026-03-08'))params.ishaInterval=120;
  const ref=new PrayerTimes(new Coordinates(c.lat,c.lon),d,params);
  for(let i=0;i<6;i++){assert(Number.isFinite(+view.rows[i].time));if(view.source.kind==='calculated')assert.equal(+view.rows[i].time,+ref[view.rows[i].key]);else assert.equal(c.slug,'muscat');if(i)assert(+view.rows[i].time>+view.rows[i-1].time)}
  const week=cityWeek(c,now);assert.equal(week.length,7);assert.equal(week[0].date,view.date);assert.deepEqual(week[0].rows,view.rows);
  for(let i=0;i<7;i++){const parts=week[i].date.split('-').map(Number);assert.deepEqual(week[i].rows,engine.calculateDaySchedule(view.state,{year:parts[0],month:parts[1],day:parts[2]}));if(i)assert.equal(+week[i].instant-+week[i-1].instant,86400000);}
  checked++;
 }
 // Find a city-local midnight and assert the snapshot advances that day, not UTC's day.
 const zone=expected[c.slug][0];let found=false;
 for(let h=0;h<24;h++){
  const a=new Date(Date.UTC(2026,0,15,h,59,59)),b=new Date(+a+1000);
  const va=cityTimetable(c,a),vb=cityTimetable(c,b);
  if(va.date!==vb.date){found=true;assert.notEqual(+va.rows[0].time,+vb.rows[0].time);break}
 }assert(found,zone+' midnight');
 for(const lang of ['ar','en']){
  const file=`dist/${lang}/prayer-times/${c.slug}.html`,html=fs.readFileSync(file,'utf8');
  const canonical=`https://salati-world-prayer.sprytitan65.chatgpt.site/${lang}/prayer-times/${c.slug}.html`;
  assert(html.includes(`<html lang="${lang}"`));assert(html.includes(`rel="canonical" href="${canonical}"`));
  for(const alternate of ['ar','en'])assert(html.includes(`hreflang="${alternate}" href="https://salati-world-prayer.sprytitan65.chatgpt.site/${alternate}/prayer-times/${c.slug}.html"`));
  assert(html.includes(lang==='ar'?c.arText.replace(/&/g,'&amp;'):c.enText.replace(/&/g,'&amp;').replace(/'/g,'&#39;')));
  assert(html.includes(lang==='ar'?'قد لا يوافق اليوم الحالي':"this may not be today's date"));
  assert(/id="snapshot-note">[^<]+/.test(html));
  assert.equal((html.match(/id="time-/g)||[]).length,6);assert(!/noindex/.test(html));
  const directory=fs.readFileSync(`dist/${lang}/prayer-times/index.html`,'utf8');assert(directory.includes(`/prayer-times/${c.slug}.html`));
 }
}
function offset(slug,instant){const v=cityTimetable(cities.find(c=>c.slug===slug),new Date(instant));return new Intl.DateTimeFormat('en',{timeZone:v.state.zone,timeZoneName:'longOffset'}).formatToParts(new Date(instant)).find(x=>x.type==='timeZoneName').value}
for(const [city,before,after] of [['london','2026-03-29T00:59Z','2026-03-29T01:01Z'],['london','2026-10-25T00:59Z','2026-10-25T01:01Z'],['new-york','2026-03-08T06:59Z','2026-03-08T07:01Z'],['new-york','2026-11-01T05:59Z','2026-11-01T06:01Z'],['cairo','2026-04-23T21:59Z','2026-04-23T22:01Z'],['cairo','2026-10-29T20:59Z','2026-10-29T21:01Z']])assert.notEqual(offset(city,before),offset(city,after),city+' DST');
for(const city of ['makkah','jakarta'])assert.equal(offset(city,'2026-01-15T12:00Z'),offset(city,'2026-07-15T12:00Z'));
const ramadan=cityTimetable(cities[0],new Date('2026-03-01T12:00Z'));assert.equal((+ramadan.rows[5].time-+ramadan.rows[4].time)/60000,120);
const muscat=cities.find(c=>c.slug==='muscat'),muscatDay=cityTimetable(muscat,new Date('2026-10-23T12:00Z'));
assert.deepEqual(muscatDay.rows.map(r=>new Intl.DateTimeFormat('en-GB',{timeZone:'Asia/Muscat',hour:'2-digit',minute:'2-digit'}).format(r.time)),['04:52','06:08','11:56','15:13','17:40','18:51']);
assert.equal(muscatDay.source.kind,'official');const monthEnd=cityWeek(muscat,new Date('2026-10-30T12:00Z'));assert.equal(monthEnd[1].source.kind,'official');assert.equal(monthEnd[2].source.kind,'calculated');
assert.equal(new Set(cities.map(c=>c.enText)).size,cities.length);assert.equal(new Set(cities.map(c=>c.arText)).size,cities.length);
console.log(`PASS: ${checked} city/date schedules, seven-day tables, ${cities.length} local-midnight rollovers, DST, regional sources and translated canonical/hreflang pages.`);
// Exercise the actual browser entry: timer/foreground refresh at a city-local midnight.
const vm=require('node:vm');
const runtime=esbuild.buildSync({entryPoints:['city-pages/runtime.js'],bundle:true,write:false}).outputFiles[0].text;
let instant=new Date('2026-01-15T20:59:59Z'),timer,visible;
class Clock extends Date {constructor(...args){super(...(args.length?args:[+instant]))}static now(){return +instant}}
const nodes=new Map();const doc={documentElement:{lang:'en'},hidden:false,getElementById(id){if(!nodes.has(id))nodes.set(id,{textContent:id==='city-config'?JSON.stringify(cities[0]):'',hidden:false});return nodes.get(id)},addEventListener(event,fn){visible=fn}};
vm.runInNewContext(runtime,{document:doc,Date:Clock,Intl,console,setInterval(fn){timer=fn}});
const oldDate=doc.getElementById('city-date').textContent;instant=new Date('2026-01-15T21:00:01Z');timer();assert.notEqual(doc.getElementById('city-date').textContent,oldDate);
assert(doc.getElementById('city-week').innerHTML.includes('datetime="2026-01-16"'));assert.equal((doc.getElementById('city-week').innerHTML.match(/<tr>/g)||[]).length,7);
for(const r of cityTimetable(cities[0],instant).rows)assert.equal(doc.getElementById('time-'+r.key).textContent,new Intl.DateTimeFormat('en-GB',{timeZone:'Asia/Riyadh',hour:'2-digit',minute:'2-digit',hour12:false}).format(r.time));
assert.equal(doc.getElementById('snapshot-note').hidden,true);instant=new Date('2026-01-16T21:00:01Z');visible();assert.notEqual(doc.getElementById('city-date').textContent,oldDate);
console.log('PASS: bundled browser runtime refreshes city date and all prayer rows at local midnight and foreground return.');
