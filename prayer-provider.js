// Legacy offline calendar parser retained for old test fixtures and cache migration.
// Privacy: no live prayer API requests or location transmission are permitted.
const IDS={MuslimWorldLeague:3,NorthAmerica:2,Egyptian:5,UmmAlQura:4,Karachi:1,Tehran:7,Kuwait:9,Qatar:10,Singapore:11,France:12,Turkey:13,Russia:14,MoonsightingCommittee:15,Dubai:16,Jakim:17,Tunisia:18,Algeria:19,Kemenag:20,Morocco:21,Portugal:22,Jordan:23,Oman:99};
const KEYS=['fajr','sunrise','dhuhr','asr','maghrib','isha'];const API_KEYS=['Fajr','Sunrise','Dhuhr','Asr','Maghrib','Isha'];
const STORAGE='salati-prayer-calendars-v1';
// Keep offline provider calendars for a bounded period, then use local astronomical calculation.
export const MAX_OFFLINE_CACHE_AGE_MS=45*86400000;
let records={};
try{
 const saved=JSON.parse(globalThis.localStorage?.getItem(STORAGE)||'{}');
 if(saved&&typeof saved==='object'&&!Array.isArray(saved))records=Object.fromEntries(Object.entries(saved).filter(([,record])=>record&&typeof record==='object'&&Number.isFinite(record.fetchedAt)&&record.days&&typeof record.days==='object'&&!Array.isArray(record.days)));
}catch{}
let revision=0;
const identity=s=>JSON.stringify([s.lat,s.lon,s.zone,s.method,s.madhab]);
const dateKey=p=>`${p.year}-${String(p.month).padStart(2,'0')}-${String(p.day).padStart(2,'0')}`;
const key=(s,y,m)=>identity(s)+':'+y+'-'+m;
export const timetableRevision=()=>revision;
function validDay(row,p){const anchor=Date.UTC(p.year,p.month-1,p.day,12);return Array.isArray(row)&&row.length===6&&row.every((t,i)=>Number.isFinite(t)&&Math.abs(t-anchor)<=36*3600000&&(!i||t>row[i-1]));}
function validMonth(record,y,m){const count=new Date(Date.UTC(y,m,0)).getUTCDate();return record?.days&&Object.keys(record.days).length===count&&Array.from({length:count},(_,i)=>{const p={year:y,month:m,day:i+1};return validDay(record.days[dateKey(p)],p);}).every(Boolean);}
export function providerTimes(s,p){const record=records[key(s,p.year,p.month)],now=Date.now();if(!record||!Number.isFinite(record.fetchedAt)||record.fetchedAt>now||now-record.fetchedAt>MAX_OFFLINE_CACHE_AGE_MS||!validMonth(record,p.year,p.month))return null;const row=record.days?.[dateKey(p)];if(!validDay(row,p))return null;return Object.fromEntries(KEYS.map((k,i)=>[k,new Date(row[i]+Number(s.adjustments?.[k]||0)*60000)]))}
export function parseCalendar(payload,s,y,m){if(payload.code!==200||!Array.isArray(payload.data))throw Error('invalid-calendar');const days={},expected=new Date(Date.UTC(y,m,0)).getUTCDate();if(payload.data.length!==expected)throw Error('incomplete-calendar');for(const d of payload.data){if(d.meta?.timezone!==s.zone||!Number.isFinite(d.meta?.latitude)||!Number.isFinite(d.meta?.longitude)||Math.abs(d.meta.latitude-s.lat)>.001||Math.abs(d.meta.longitude-s.lon)>.001||d.meta?.method?.id!==IDS[s.method]||d.meta?.school!==(s.madhab==='Hanafi'?'HANAFI':'STANDARD'))throw Error('wrong-calendar');const [day,month,year]=String(d.date?.gregorian?.date).split('-').map(Number);if(year!==y||month!==m||day<1||day>expected)throw Error('wrong-date');const row=API_KEYS.map(k=>{const value=d.timings?.[k];if(typeof value!=='string'||!/^\d{4}-\d\d-\d\dT\d\d:\d\d(?::\d\d)?[+-]\d\d:\d\d$/.test(value))throw Error('invalid-time');const t=Date.parse(value);if(!Number.isFinite(t)||Math.abs(t-Date.UTC(y,m-1,day,12))>36*3600000)throw Error('invalid-time');return t});if(!row.every((t,i)=>!i||t>row[i-1]))throw Error('unordered');if(s.method==='Oman'){[0,1,5,5,5,0].forEach((v,i)=>row[i]+=v*60000)}days[dateKey({year,month,day})]=row}if(Object.keys(days).length!==expected)throw Error('duplicate-date');return {fetchedAt:Date.now(),days}}
// The network-based provider was retired. Existing cache files are not fetched
// or refreshed: both the web app and Android calculate prayer times locally.
// Preserve this no-network compatibility method so old callers cannot send
// latitude, longitude, timezone or calculation preferences to a third party.
export async function refreshProvider(_state,_parts,_fetcher,_options){return {changed:false,failed:false}}
