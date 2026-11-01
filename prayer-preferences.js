const KEYS=['fajr','sunrise','dhuhr','asr','maghrib','isha'];
export const zeroPrayerAdjustments=()=>Object.fromEntries(KEYS.map(k=>[k,0]));
const validAdjustments=saved=>Object.fromEntries(KEYS.map(k=>{
  const raw=saved.adjustments?.[k];
  const value=typeof raw==='number'?raw:Number(raw??0);
  return [k,Number.isFinite(value)&&Math.abs(value)<=30?value:0];
}));

// A migration must NEVER decide that an existing user's correction is disposable.
// Keep valid offsets verbatim, including legacy Auto/near-Muscat settings.
// Only an explicit user press on "Restore automatic times" may zero adjustments.
export function restorePrayerPreferences(saved){
 const adjustments=validAdjustments(saved);
 const hasCorrections=Object.values(adjustments).some(v=>v!==0);
 return {
  prayerPreferenceVersion:2,
  adjustmentMode:hasCorrections?'manual':saved.adjustmentMode==='manual'?'manual':'automatic',
  adjustments,
  cleared:false
 };
}

// Older versions reset offsets for users within 45 km of Muscat. Mark the
// migration as consumed without changing the user's stored prayer corrections.
// Copy rather than mutate, so opening the app cannot silently discard a change.
export function applyRequestedMuscatTimes(saved){
 if(saved.muscatCalibrationVersion===4)return saved;
 return {...saved,muscatCalibrationVersion:4};
}
