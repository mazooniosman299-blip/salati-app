export function hasPrayerLocation(state){return state.locationSet===true&&Number.isFinite(state.lat)&&Math.abs(state.lat)<=90&&Number.isFinite(state.lon)&&Math.abs(state.lon)<=180;}
export function restoreLocation(saved={},zone='UTC'){
 const valid=hasPrayerLocation(saved);let safeZone=zone;try{new Intl.DateTimeFormat('en',{timeZone:zone}).format();}catch{safeZone='UTC';}
 if(!valid)return {lat:null,lon:null,zone:safeZone,name:'',locationSet:false,locationMode:'auto'};
 let restoredZone=saved.zone||safeZone;try{new Intl.DateTimeFormat('en',{timeZone:restoredZone}).format();}catch{restoredZone=safeZone;}
 return {lat:saved.lat,lon:saved.lon,zone:restoredZone,name:saved.name||'',locationSet:true,locationMode:saved.locationMode||'auto'};
}
// A manual choice made while GPS is pending wins over that old request.
export class LocationIntent{
 constructor(){this.generation=0;}
 request(){return ++this.generation;}
 cancel(){this.generation++;}
 current(generation){return generation===this.generation;}
}
