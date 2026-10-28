// Always ask for a fresh GPS fix; never silently accept cached coordinates.
export function freshPosition(geo){return new Promise((resolve,reject)=>{if(!geo){reject(Error('unavailable'));return}geo.getCurrentPosition(p=>{const {latitude,longitude,accuracy}=p.coords;if(!Number.isFinite(latitude)||!Number.isFinite(longitude)||Math.abs(latitude)>90||Math.abs(longitude)>180||!Number.isFinite(accuracy)||accuracy<0||accuracy>5000||!Number.isFinite(p.timestamp)||Math.abs(Date.now()-p.timestamp)>120000){reject(Error('invalid-location'));return}resolve(p)},reject,{enableHighAccuracy:true,maximumAge:0,timeout:25000})})}
export function samePrayerLocation(state,coords){if(!state.locationSet)return false;const rad=Math.PI/180,dLat=(coords.latitude-state.lat)*rad,dLon=(coords.longitude-state.lon)*rad;const a=Math.sin(dLat/2)**2+Math.cos(state.lat*rad)*Math.cos(coords.latitude*rad)*Math.sin(dLon/2)**2;return 6371000*2*Math.atan2(Math.sqrt(a),Math.sqrt(Math.max(0,1-a)))<5000}
// Identify a nearby city without mutating stored GPS; the calendar engine selects its reference separately.
export function nearestCity(coords,candidates,zone,maxDistance=50000){
 if(!Number.isFinite(coords.latitude)||!Number.isFinite(coords.longitude))return null;
 const rad=Math.PI/180;let best=null,limit=maxDistance;
 for(const city of candidates){if(zone&&city[3]!==zone)continue;const a=Math.sin((city[1]-coords.latitude)*rad/2)**2+Math.cos(coords.latitude*rad)*Math.cos(city[1]*rad)*Math.sin((city[2]-coords.longitude)*rad/2)**2;const distance=6371000*2*Math.atan2(Math.sqrt(a),Math.sqrt(Math.max(0,1-a)));if(distance<=limit){best=city;limit=distance}}
 return best;
}

// Retain intentional minute adjustments when GPS moves within the same detected city.
export function samePrayerCity(state,coords,candidates,zone){
 if(!state.locationSet)return false;
 const before=nearestCity({latitude:state.lat,longitude:state.lon},candidates,state.zone);
 const after=nearestCity(coords,candidates,zone);
 return !!before&&before===after;
}
