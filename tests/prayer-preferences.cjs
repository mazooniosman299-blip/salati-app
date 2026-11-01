const assert=require('node:assert/strict'),Module=require('node:module'),esbuild=require('esbuild');
const out=esbuild.buildSync({entryPoints:['prayer-preferences.js'],bundle:true,platform:'node',format:'cjs',write:false});
const m=new Module('preferences',module);m._compile(out.outputFiles[0].text,'preferences.cjs');
const {restorePrayerPreferences,applyRequestedMuscatTimes}=m.exports;
const original={method:'Auto',methodPreferenceVersion:1,adjustments:{fajr:1,sunrise:-2,asr:3,maghrib:0},lat:23.588,lon:58.3829,madhab:'Shafi',locationSet:true};
for(const method of ['Auto','Oman','Egyptian']){
 for(const madhab of ['Shafi','Hanafi']){
  for(const version of [undefined,1,2,3,4]){
   const saved={...original,method,madhab,muscatCalibrationVersion:version};
   const first=restorePrayerPreferences(saved);
   assert.deepEqual(first.adjustments,{fajr:1,sunrise:-2,dhuhr:0,asr:3,maghrib:0,isha:0});
   assert.equal(first.adjustmentMode,'manual');assert.equal(first.cleared,false);
   const upgraded=applyRequestedMuscatTimes({...saved,...first});
   assert.deepEqual(upgraded.adjustments,first.adjustments,'migration must be lossless');
   assert.equal(upgraded.muscatCalibrationVersion,4);
   assert.deepEqual(applyRequestedMuscatTimes(upgraded).adjustments,first.adjustments,'idempotent');
  }
 }
}
for(const position of [[23.588,58.3829],[23.6,58.12],[17.02,54.11],[30,31]]){
 const saved={...original,lat:position[0],lon:position[1],muscatCalibrationVersion:1};
 assert.deepEqual(applyRequestedMuscatTimes(saved).adjustments,original.adjustments);
}
assert.equal(restorePrayerPreferences({...original,adjustments:{fajr:Infinity}}).adjustments.fajr,0);
assert.equal(restorePrayerPreferences({...original,adjustments:{fajr:-31}}).adjustments.fajr,0);
assert.equal(restorePrayerPreferences({method:'Auto',adjustments:{}}).adjustmentMode,'automatic');
assert.equal(restorePrayerPreferences({...original,method:'Auto',prayerPreferenceVersion:2,adjustments:{isha:-5}}).adjustments.isha,-5);
console.log('PASS: no stored prayer offsets are deleted across all tested migration versions, methods, madhabs and locations.');
