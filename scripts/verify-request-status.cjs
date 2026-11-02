#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const ledger=JSON.parse(fs.readFileSync(path.join(root,'docs/requests/ACCEPTANCE_STATUS.json'),'utf8'));
const valid=new Set(['pass','fail','blocked','not_run','not_applicable']);
const required=['user_request_captured','source_map_and_contract','source_build','functional_regressions','real_browser','screenshot_user_reference','android_emulator','physical_android','signed_release','production_publication','latest_user_acceptance'];
function validate(state){
 assert(/^SALATI-/.test(state.request_id||''),'Invalid request id');
 assert(['in_progress','blocked','complete'].includes(state.overall),'Invalid overall state');
 assert.equal(state.complete,state.overall==='complete','Completion flag does not match state');
 for(const key of required){
  const value=state.stages?.[key];
  assert(value && valid.has(value.status),'Missing/invalid stage '+key);
  if(value.status==='pass')assert(typeof value.evidence==='string'&&value.evidence.length>5,'Pass has no real evidence: '+key);
  else assert(typeof value.reason==='string'&&value.reason.length>5,'Unverified stage lacks reason: '+key);
 }
 if(state.complete){
  for(const key of ['screenshot_user_reference','latest_user_acceptance','real_browser','functional_regressions'])
   assert.equal(state.stages[key].status,'pass','Cannot mark all 20 complete without '+key);
  for(const [key,record] of Object.entries(state.stages))assert(['pass','not_applicable'].includes(record.status),'Complete request has blocked/failed stage '+key);
  if(state.code_runtime_changed){
   assert.equal(state.stages.signed_release.status,'pass','Runtime production needs original-key signing proof');
   assert.equal(state.stages.production_publication.status,'pass','Runtime release needs actual deploy verification');
  }
 }
 return true;
}
validate(ledger);
const falseSuccess=JSON.parse(JSON.stringify(ledger));falseSuccess.complete=true;falseSuccess.overall='complete';
assert.throws(()=>validate(falseSuccess),/Cannot mark|Complete request|original-key/,'False completion must be rejected');
const unsupported=JSON.parse(JSON.stringify(ledger));unsupported.stages.real_browser={status:'pass'};
assert.throws(()=>validate(unsupported),/no real evidence/);
console.log('PASS acceptance status: full source/build/functional/browser/reference/Android/device/release/user acceptance separated; false claims rejected');
module.exports={validate};
