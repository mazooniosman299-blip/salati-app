import {cityTimetable,cityWeek} from './timetable.js';
const config=JSON.parse(document.getElementById('city-config').textContent),lang=document.documentElement.lang,locale=lang==='ar'?'ar-EG':'en-GB';
let weekDate;
function refresh(){
 const now=new Date(),{state,rows,date,source}=cityTimetable(config,now);
 const format=value=>Number.isFinite(+value)?new Intl.DateTimeFormat(locale,{timeZone:state.zone,hour:'2-digit',minute:'2-digit',hour12:false}).format(value):'—';
 document.getElementById('city-date').textContent=new Intl.DateTimeFormat(locale,{timeZone:state.zone,dateStyle:'full'}).format(now);
 document.getElementById('city-clock').textContent=new Intl.DateTimeFormat(locale,{timeZone:state.zone,timeStyle:'short'}).format(now);
 document.getElementById('city-offset').textContent=new Intl.DateTimeFormat('en',{timeZone:state.zone,timeZoneName:'longOffset'}).formatToParts(now).find(p=>p.type==='timeZoneName').value;
 for(const row of rows)document.getElementById('time-'+row.key).textContent=format(row.time);
 const link=document.getElementById('city-source');link.textContent=source[lang];link.href=source.url;
 if(weekDate!==date){document.getElementById('city-week').innerHTML=cityWeek(config,now).map(day=>`<tr><th scope="row"><time datetime="${day.date}">${new Intl.DateTimeFormat(locale,{timeZone:'UTC',weekday:'short',day:'numeric',month:'short'}).format(day.instant)}</time></th>${day.rows.map(row=>`<td><bdi>${format(row.time)}</bdi></td>`).join('')}</tr>`).join('');weekDate=date;}
 document.getElementById('snapshot-note').hidden=true;
}
refresh();setInterval(refresh,30000);document.addEventListener('visibilitychange',()=>{if(!document.hidden)refresh()});
