const KEYS=['fajr','sunrise','dhuhr','asr','maghrib','isha'];
export const zeroPrayerAdjustments=()=>Object.fromEntries(KEYS.map(k=>[k,0]));
// Legacy Auto mixed calculated times and untracked saved offsets. Start it clean
// once; explicit corrections made with the new UI remain intentional and saved.
export function restorePrayerPreferences(saved){const legacy=saved.prayerPreferenceVersion!==2;const automatic=saved.method==='Auto'||!saved.methodPreferenceVersion;const adjustments=Object.fromEntries(KEYS.map(k=>{const value=Number(saved.adjustments?.[k]||0);return [k,Number.isFinite(value)&&Math.abs(value)<=30?value:0]}));const cleared=legacy&&automatic&&Object.values(adjustments).some(Boolean);return {prayerPreferenceVersion:2,adjustmentMode:legacy&&automatic?'automatic':saved.adjustmentMode||'manual',adjustments:legacy&&automatic?zeroPrayerAdjustments():adjustments,cleared}}

// Clear offsets from the earlier settings-based correction. The requested
// dated correction now lives in the shared schedule engine.
export function applyRequestedMuscatTimes(saved){
 const version=4;
 if(saved.muscatCalibrationVersion===version)return saved;
 const next={...saved,muscatCalibrationVersion:version};
 const dy=(saved.lat-23.588)*111,dx=(saved.lon-58.3829)*111*Math.cos(saved.lat*Math.PI/180);
 if(Math.hypot(dx,dy)<=45&&['Auto','Oman'].includes(saved.method)&&saved.madhab!=='Hanafi'){
  next.adjustments=zeroPrayerAdjustments();
  next.adjustmentMode='manual';
 }
 return next;
}
