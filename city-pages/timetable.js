import {calculateSchedule,calculateDaySchedule,regionalProfile,calendarParts,timetableSource} from '../prayer-engine.js';
const dateKey=p=>`${p.year}-${String(p.month).padStart(2,'0')}-${String(p.day).padStart(2,'0')}`;
export function cityTimetable(city,now=new Date()) {
 const state={lat:city.lat,lon:city.lon,...regionalProfile(city.lat,city.lon),locationMode:'manual'};
 const date=dateKey(calendarParts(now,state.zone));
 return {state,date,rows:calculateSchedule(state,now).slice(0,6),source:timetableSource(state,now)};
}
// Advance civil dates rather than 24-hour instants: daylight-saving days can be shorter or longer.
export function cityWeek(city,now=new Date()) {
 const view=cityTimetable(city,now),start=calendarParts(now,view.state.zone);
 return Array.from({length:7},(_,i)=>{
  const instant=new Date(Date.UTC(start.year,start.month-1,start.day+i,12));
  const parts={year:instant.getUTCFullYear(),month:instant.getUTCMonth()+1,day:instant.getUTCDate()};
  const rows=calculateDaySchedule(view.state,parts);
  return {date:dateKey(parts),instant,rows,source:timetableSource(view.state,rows[2].time)};
 });
}
