// All prayer-time computations use the bundled Adhan library locally.
import tzLookup from './timezone-lookup.js';
import {getTimezone} from 'countries-and-timezones';
import {PrayerTimes,Coordinates,CalculationMethod,Madhab,HighLatitudeRule} from 'adhan';
import {cities} from './cities.js';
import {nearestCity} from './location.js';
import {MUSCAT_OCTOBER_2026,MUSCAT_NOVEMBER_2026,MUSCAT_SOURCE} from './official-muscat.js';
import {SINGAPORE_MUIS_2026,SINGAPORE_MUIS_SOURCE} from './official-singapore.js';
import {WLY01_NOVEMBER_2026,WLY01_SOURCE} from './official-malaysia-wly01.js';
import {CAIRO_NOVEMBER_2026,CAIRO_SOURCE} from './official-cairo.js';
export const PRAYER_KEYS=['fajr','sunrise','dhuhr','asr','maghrib','isha'];
// Regional conventions, not a claim of official timetable coverage everywhere.
// Method angles: https://api.aladhan.com/v1/methods
const COUNTRY_METHODS={OM:'Oman',AE:'Dubai',SA:'UmmAlQura',EG:'Egyptian',KW:'Kuwait',QA:'Qatar',TR:'Turkey',IR:'Tehran',MA:'Morocco',TN:'Tunisia',DZ:'Algeria',JO:'Jordan',MY:'Jakim',ID:'Kemenag',SG:'Singapore',RU:'Russia',PT:'Portugal',US:'NorthAmerica',CA:'NorthAmerica',PK:'Karachi',IN:'Karachi',BD:'Karachi',AF:'Karachi',AU:'MoonsightingCommittee',NZ:'MoonsightingCommittee',ZA:'MoonsightingCommittee'};
const HANAFI=new Set(['PK','IN','BD','AF','UZ','TJ','KG','TM','KZ','RU']);
const CUSTOM={Tunisia:{fajr:18,isha:18},Algeria:{fajr:18,isha:17},Jordan:{fajr:18,isha:18,offsets:{maghrib:5}},Jakim:{fajr:18,isha:18},Kemenag:{fajr:20,isha:18},Russia:{fajr:16,isha:15},France:{fajr:12,isha:12},Portugal:{fajr:18,interval:77,offsets:{maghrib:3}},Oman:{fajr:18,isha:18,offsets:{sunrise:1,dhuhr:5,asr:5,maghrib:5}}};
export function regionalProfile(lat,lon){const zone=tzLookup(lat,lon);const candidates=cities.filter(c=>c[3]===zone);const nearest=candidates.sort((a,b)=>((a[1]-lat)**2+(a[2]-lon)**2)-((b[1]-lat)**2+(b[2]-lon)**2))[0];const countries=getTimezone(zone)?.countries||[];const country=countries[0]||'';const method=COUNTRY_METHODS[country]||nearest?.[4]||'MuslimWorldLeague';return {zone,method,country,madhab:HANAFI.has(country)?'Hanafi':'Shafi'}}
export function calendarParts(now,zone){const parts=new Intl.DateTimeFormat('en',{timeZone:zone,year:'numeric',month:'numeric',day:'numeric'}).formatToParts(now);return Object.fromEntries(parts.filter(p=>p.type!=='literal').map(p=>[p.type,+p.value]))}
// A detected named city uses the same calendar coordinates as selecting that city manually.
// Actual GPS stays in state for the compass; remote/custom locations retain point calculations.
export function resolveCalculationState(state){
 const resolved=state.method==='Auto'?{...state,...regionalProfile(state.lat,state.lon),...(state.zoneMode==='manual'?{zone:state.zone}:{})}:state;
 if(state.locationMode!=='auto')return resolved;
 const city=nearestCity({latitude:state.lat,longitude:state.lon},cities,state.zoneMode==='manual'?tzLookup(state.lat,state.lon):resolved.zone);
 return city?{...resolved,lat:city[1],lon:city[2],zone:state.zoneMode==='manual'?state.zone:city[3],locationMode:'city-calendar',authorityLat:state.lat,authorityLon:state.lon}:resolved;
}
export function prayerParameters(state,day){state=resolveCalculationState(state);let p;if(state.method==='Morocco'){p=CalculationMethod.Other();p.fajrAngle=19;p.ishaAngle=17;p.methodAdjustments.dhuhr=5;p.methodAdjustments.maghrib=3}else if(CUSTOM[state.method]){const c=CUSTOM[state.method];p=CalculationMethod.Other();p.fajrAngle=c.fajr;p.ishaAngle=c.isha||0;p.ishaInterval=c.interval||0;Object.assign(p.methodAdjustments,c.offsets||{})}else {const factory=CalculationMethod[state.method];if(!factory)throw Error('Unknown calculation method');p=factory()}p.madhab=Madhab[state.madhab];p.highLatitudeRule=HighLatitudeRule.recommended(new Coordinates(state.lat,state.lon));if(state.method==='UmmAlQura'){const month=new Intl.DateTimeFormat('en-u-ca-islamic-umalqura',{month:'numeric',timeZone:'UTC'}).format(new Date(Date.UTC(day.getFullYear(),day.getMonth(),day.getDate(),12)));if(Number(month)===9)p.ishaInterval=120}for(const k of PRAYER_KEYS)p.adjustments[k]=Number(state.adjustments?.[k]||0);return p}
function muscatCoverage(state,day){if(state.method!=='Oman'||state.madhab!=='Shafi'||day.getFullYear()!==2026||day.getMonth()!==9)return false;const dy=(state.lat-23.588)*111,dx=(state.lon-58.3829)*111*Math.cos(state.lat*Math.PI/180);return Math.hypot(dx,dy)<=20&&!!MUSCAT_OCTOBER_2026[day.getDate()]}
// Requested display correction for Muscat on 2026-10-21; not an official-table edit.
function requestedMuscatDay(day){return day.getFullYear()===2026&&day.getMonth()===9&&day.getDate()===21}
function requestedMuscatCoverage(state,day){if(state.method!=='Oman'||state.madhab!=='Shafi'||!requestedMuscatDay(day))return false;const dy=(state.lat-23.588)*111,dx=(state.lon-58.3829)*111*Math.cos(state.lat*Math.PI/180);return Math.hypot(dx,dy)<=45}
// Some circumpolar days cause the astronomical library's shadow-based Asr
// to be before solar noon or after sunset. This is not a valid prayer time.
// Never invent a clock time or schedule an Adhan for that event; the UI
// renders an unavailable marker until a locally approved high-latitude method
// is selected. Dates at ordinary latitudes remain untouched.
export function validateDayTimes(times){
 const result={...times};
 const t=key=>+result[key];
 const absent=key=>{result[key]=new Date(NaN)};
 const finite=(...keys)=>keys.every(key=>Number.isFinite(t(key)));
 if(finite('fajr','sunrise')&&t('fajr')>=t('sunrise'))absent('fajr');
 if(finite('sunrise','dhuhr')&&t('sunrise')>=t('dhuhr'))absent('sunrise');
 if(finite('dhuhr','maghrib')&&t('dhuhr')>=t('maghrib')){absent('dhuhr');absent('asr')}
 if(finite('asr','maghrib')&&t('asr')>=t('maghrib'))absent('asr');
 if(finite('dhuhr','asr')&&t('asr')<=t('dhuhr'))absent('asr');
 if(finite('maghrib','isha')&&t('isha')<=t('maghrib'))absent('isha');
 return result;
}
function calendarAlignedSolarTimes(state,day){
 const coordinates=new Coordinates(state.lat,state.lon),parameters=prayerParameters(state,day);
 const zone=state.zone||tzLookup(state.lat,state.lon);
 const target=Date.UTC(day.getFullYear(),day.getMonth(),day.getDate());
 // Adhan anchors its solar calculation to a Gregorian UTC day. West-longitude
 // locations using an eastern civil date (e.g. Kiritimati/Apia) need the
 // previous solar day. Recalculate it: moving tomorrow's timestamps24h would
 // keep tomorrow's solar angles and can introduce a one-minute error.
 const difference=times=>{
  if(!Number.isFinite(+times.dhuhr))return 0;
  const corrections=Number(parameters.adjustments.dhuhr||0)+Number(parameters.methodAdjustments.dhuhr||0);
  const local=calendarParts(new Date(+times.dhuhr-corrections*60000),zone);
  return (target-Date.UTC(local.year,local.month-1,local.day))/86400000;
 };
 let times=new PrayerTimes(coordinates,day,parameters),shift=difference(times);
 if(shift){const solarDay=new Date(day);solarDay.setDate(solarDay.getDate()+shift);times=new PrayerTimes(coordinates,solarDay,parameters);}
 // A historically skipped civil date has no corresponding solar day. Never
 // invent six alarm timestamps for it. Normal dates retain the original data.
 if(difference(times))return Object.fromEntries(PRAYER_KEYS.map(k=>[k,new Date(NaN)]));
 return times;
}
// Authority tables are immutable per-city/date references, NOT a universal calculation rule.
// The already-published GPS-to-nearest-city behavior is intentionally unchanged.
function verifiedMuscatNovember(state,day){
 if(state.method!=='Oman'||state.zone!=='Asia/Muscat'
   ||day.getFullYear()!==2026||day.getMonth()!==10)return null;
 const lat=state.authorityLat??state.lat,lon=state.authorityLon??state.lon;
 const dy=(lat-23.588)*111,dx=(lon-58.3829)*111*Math.cos(lat*Math.PI/180);
 // Never pass the Muscat table off as the official calendar for distant Seeb/Al Maabela.
 if(Math.hypot(dx,dy)>2)return null;
 return MUSCAT_NOVEMBER_2026[day.getDate()]||null;
}
function verifiedSingapore2026(state,day){
 const lat=state.authorityLat??state.lat,lon=state.authorityLon??state.lon;
 if(state.method!=='Singapore'||state.zone!=='Asia/Singapore'
   ||day.getFullYear()!==2026||lat<1.14||lat>1.48||lon<103.58||lon>104.15)return null;
 const key=day.getFullYear()+'-'+String(day.getMonth()+1).padStart(2,'0')+'-'+String(day.getDate()).padStart(2,'0');
 return SINGAPORE_MUIS_2026[key]||null;
}
// Kuala Lumpur and Putrajaya are JAKIM official prayer zone WLY01.
// This is a conservative subset (2km around Kuala Lumpur center or Putrajaya center),
// not a false claim to know all Malaysian prayer-zone boundaries.
function verifiedMalaysiaWLY01November(state,day){
 if(state.method!=='Jakim'||state.zone!=='Asia/Kuala_Lumpur'
   ||day.getFullYear()!==2026||day.getMonth()!==10)return null;
 const lat=state.authorityLat??state.lat,lon=state.authorityLon??state.lon;
 const near=(a,b)=>{
  const dy=(lat-a)*111,dx=(lon-b)*111*Math.cos(lat*Math.PI/180);
  return Math.hypot(dx,dy)<=2;
 };
 return (near(3.139,101.6869)||near(2.9264,101.6964))?
   (WLY01_NOVEMBER_2026[day.getDate()]||null):null;
}

// Cairo 2026-11 timetable from Dar al-Ifta / Egyptian Survey; never use for other Egyptian cities.
function verifiedCairoNovember(state,day){
 if(state.method!=='Egyptian'||state.zone!=='Africa/Cairo'
   ||day.getFullYear()!==2026||day.getMonth()!==10)return null;
 const lat=state.authorityLat??state.lat,lon=state.authorityLon??state.lon;
 const dy=(lat-30.0444)*111,dx=(lon-31.2357)*111*Math.cos(lat*Math.PI/180);
 return Math.hypot(dx,dy)<=2?(CAIRO_NOVEMBER_2026[day.getDate()]||null):null;
}

function sourceRowTimes(state,day,rows,utcOffsetMinutes){
 const times={};
 for(let i=0;i<PRAYER_KEYS.length;i++){
  const key=PRAYER_KEYS[i],mins=rows[i]+Number(state.adjustments?.[key]||0);
  times[key]=new Date(Date.UTC(day.getFullYear(),day.getMonth(),day.getDate(),0,mins-utcOffsetMinutes));
 }
 // Changing the Asr school must never change source-verified sunrise or Isha.
 if(state.madhab==='Hanafi')times.asr=calendarAlignedSolarTimes(state,day).asr;
 return validateDayTimes(times);
}

function dayTimes(state,day){const muscat=verifiedMuscatNovember(state,day),singapore=verifiedSingapore2026(state,day),wly01=verifiedMalaysiaWLY01November(state,day),cairo=verifiedCairoNovember(state,day);if(muscat)return sourceRowTimes(state,day,muscat,240);if(singapore)return sourceRowTimes(state,day,singapore,480);if(wly01)return sourceRowTimes(state,day,wly01,480);if(cairo)return sourceRowTimes(state,day,cairo,120);if(muscatCoverage(state,day)||requestedMuscatCoverage(state,day)){const times={};PRAYER_KEYS.forEach((key,i)=>{const minutes=MUSCAT_OCTOBER_2026[day.getDate()][i]+(requestedMuscatDay(day)?({asr:1}[key]||0):0)+Number(state.adjustments?.[key]||0);times[key]=new Date(Date.UTC(day.getFullYear(),day.getMonth(),day.getDate(),0,minutes-240))});return validateDayTimes(times)}return validateDayTimes(calendarAlignedSolarTimes(state,day))}
export function timetableSource(state,now=new Date()){state=resolveCalculationState(state);const d=calendarParts(now,state.zone),day=new Date(d.year,d.month-1,d.day,12);return verifiedCairoNovember(state,day)?(state.madhab==='Hanafi'?{kind:'custom',ar:'تقويم القاهرة الرسمي والعصر حنفي محسوب',en:'Cairo official calendar with calculated Hanafi Asr',url:CAIRO_SOURCE}:{kind:'official',ar:'تقويم القاهرة الرسمي · دار الإفتاء وهيئة المساحة المصرية',en:'Official Cairo calendar · Egyptian Dar al-Ifta/Survey Authority',url:CAIRO_SOURCE}):verifiedMalaysiaWLY01November(state,day)?(state.madhab==='Hanafi'?{kind:'custom',ar:'تقويم كوالالمبور وبوتراجايا الرسمي والعصر حنفي محسوب',en:'Official WLY01 JAKIM times with calculated Hanafi Asr',url:WLY01_SOURCE}:{kind:'official',ar:'تقويم منطقة WLY01 الرسمي · مكتب المفتي الماليزي',en:'Official Kuala Lumpur and Putrajaya WLY01 timetable · Federal Territory Mufti',url:WLY01_SOURCE}):verifiedSingapore2026(state,day)?(state.madhab==='Hanafi'?{kind:'custom',ar:'تقويم سنغافورة MUIS الرسمي والعصر حنفي محسوب',en:'Singapore MUIS official times with calculated Hanafi Asr',url:SINGAPORE_MUIS_SOURCE}:{kind:'official',ar:'تقويم سنغافورة الرسمي · MUIS',en:'Official Singapore timetable · MUIS',url:SINGAPORE_MUIS_SOURCE}):verifiedMuscatNovember(state,day)?(state.madhab==='Hanafi'?{kind:'custom',ar:'تقويم مسقط الرسمي والعصر حنفي محسوب',en:'Muscat official times with calculated Hanafi Asr',url:MUSCAT_SOURCE}:{kind:'official',ar:'تقويم مسقط الرسمي · وزارة الأوقاف العُمانية',en:'Official Muscat calendar · Oman Ministry of Endowments',url:MUSCAT_SOURCE}):requestedMuscatCoverage(state,day)?{kind:'custom',ar:'تقويم مسقط مع تعديلات المواقيت المطلوبة',en:'Muscat calendar with requested prayer-time corrections',url:MUSCAT_SOURCE}:muscatCoverage(state,day)?{kind:'official',ar:'تقويم مسقط الرسمي · وزارة الأوقاف العُمانية',en:'Official Muscat calendar · Oman Ministry of Endowments',url:MUSCAT_SOURCE}:{kind:'calculated',ar:'حساب فلكي بحسب طريقة المنطقة',en:'Astronomical calculation using the regional convention',url:'https://aladhan.com/calculation-methods'}}
export function calculateSchedule(state,now=new Date()){state=resolveCalculationState(state);const d=calendarParts(now,state.zone);const day=new Date(d.year,d.month-1,d.day,12),today=dayTimes(state,day);day.setDate(day.getDate()+1);const tomorrow=dayTimes(state,day);return [...PRAYER_KEYS.map(key=>({key,time:today[key]})),{key:'fajr',time:tomorrow.fajr,tomorrow:true}]}

export function calculateDaySchedule(state,parts){state=resolveCalculationState(state);const day=new Date(parts.year,parts.month-1,parts.day,12),times=dayTimes(state,day);return PRAYER_KEYS.map(key=>({key,time:times[key]}))}

// No external prayer-calendar update. Legacy callers keep their Promise result,
// and even an injected fetcher cannot transmit exact coordinates.
export function refreshTimetables(_state,_now=new Date(),_fetcher,_options){return Promise.resolve({changed:false,failed:false})}
