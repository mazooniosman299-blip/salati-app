// Fail-closed INDEPENDENT authority test for public source rows not already bundled
// in Salati. Mathematical/Adhan agreement is not accepted as external proof.
const fs=require('node:fs'),Module=require('node:module'),esbuild=require('esbuild');
const m=new Module('authority-independent',module);
m._compile(esbuild.buildSync({entryPoints:['prayer-engine.js'],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,'audit.cjs');
const {calculateDaySchedule,timetableSource,PRAYER_KEYS}=m.exports;
const fixtures=[
 {name:'Istanbul, Türkiye',date:'2026-11-07',lat:41.0082,lon:28.9784,zone:'Europe/Istanbul',method:'Turkey',madhab:'Shafi',
  expected:['06:08','07:35','12:53','15:35','18:01','19:22'],
  authority:'Türkiye Diyanet İşleri Başkanlığı',url:'https://namazvakitleri.diyanet.gov.tr/tr-TR/9541/istanbul-icin-namaz-vakti'},
 {name:'Kuala Lumpur, Malaysia',date:'2026-11-07',lat:3.139,lon:101.6869,zone:'Asia/Kuala_Lumpur',method:'Jakim',madhab:'Shafi',
  expected:['05:48','06:56','13:00','16:21','18:58','20:10'],
  authority:'Pejabat Mufti Wilayah Persekutuan / JAKIM Almanak Falak Syarie',
  url:'https://www.muftiwp.gov.my/images/falak/takwim/jadual-waktu-solat/KL-dan-Putrajaya/JADUAL_WAKTU_SOLAT_2026_WP_KL_PUTRAJAYA.pdf'},
 {name:'Cairo, Egypt',date:'2026-11-07',lat:30.0444,lon:31.2357,zone:'Africa/Cairo',method:'Egyptian',madhab:'Shafi',
  expected:['04:45','06:13','11:39','14:41','17:03','18:23'],
  authority:'Egyptian General Authority for Survey and Dar al-Ifta',
  url:'https://www.esa.gov.eg/praytimes.aspx'},
];
const toMinute=s=>{const [h,m]=s.split(':').map(Number);return h*60+m};
const clock=(d,zone)=>new Intl.DateTimeFormat('en-GB',{timeZone:zone,hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).format(d);
const results=fixtures.map(f=>{
 const state={lat:f.lat,lon:f.lon,zone:f.zone,locationMode:'manual',method:f.method,madhab:f.madhab,adjustments:{}};
 const [year,month,day]=f.date.split('-').map(Number);
 const computed=calculateDaySchedule(state,{year,month,day}).map(p=>clock(p.time,f.zone));
 const differences=computed.map((value,i)=>toMinute(value)-toMinute(f.expected[i]));
 return {name:f.name,date:f.date,zone:f.zone,method:f.method,authority:f.authority,url:f.url,expected:f.expected,actual:computed,
  difference_minutes:differences,source_kind:timetableSource(state,new Date(f.date+'T12:00:00Z')).kind,
  exact_match:differences.every(x=>x===0),within_1_minute:differences.every(x=>Math.abs(x)<=1)};
});
fs.mkdirSync('reports/world-authority',{recursive:true});
fs.writeFileSync('reports/world-authority/independent-reference-2026-11-07.json',JSON.stringify({purpose:'Compare independent official country-level prayer times against actual candidate app engine. No publication authorization.',fixtures:results,unverified_countries:'all other regions without independent authority fixtures'},null,2)+'\n');
console.log(JSON.stringify(results,null,2));
if(!results.every(x=>x.exact_match)){console.error('FAIL: independent official authority disagrees with app candidate. NO worldwide exactness proof; NO RELEASE.');process.exitCode=1}
else console.log('PASS: independent benchmark matches for listed cities and dates ONLY; NOT all countries.');
