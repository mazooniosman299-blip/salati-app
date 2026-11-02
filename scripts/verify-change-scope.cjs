#!/usr/bin/env node
'use strict';
/* Per-request PR diff contract. No release/deployment commands. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const {execFileSync} = require('node:child_process');
const path = require('node:path');
const root = path.resolve(__dirname,'..');
const activePath = path.join(root,'docs/requests/ACTIVE_CHANGE.json');
const readManifest = () => JSON.parse(fs.readFileSync(activePath,'utf8'));
const runtimePath = path => /^(?:dist\/|android\/|apk-release-parts\/|app-source\.js$|quran-controller\.js$|quran-page-audio\.js$|.*\.css$)/.test(path);
const releaseCriticalPath = path => /^(?:dist\/|android\/|apk-release-parts\/)/.test(path);
function validateScope(changed, manifest) {
  assert(manifest && typeof manifest.request_id === 'string' && manifest.request_id.startsWith('SALATI-'), 'Missing request ID');
  assert.equal(manifest.base_branch,'production','Every Salati production PR starts from production');
  assert(['governance','preview','production'].includes(manifest.release_mode),'Declare release_mode: governance/preview/production');
  assert(Array.isArray(manifest.allowed_paths) && manifest.allowed_paths.length>0,'Empty scope allowlist');
  assert.equal(new Set(manifest.allowed_paths).size,manifest.allowed_paths.length,'Duplicate allowlist paths');
  assert(manifest.allowed_paths.every(p=>typeof p==='string' && !!p && !p.startsWith('/') && !p.includes('..') && !p.includes('*')),'Only exact repository-relative paths allowed');
  assert(changed.length>0,'No changes in PR');
  const unexpected = changed.filter(p=>!manifest.allowed_paths.includes(p));
  assert.deepEqual(unexpected,[], 'OUT-OF-SCOPE FILES: '+unexpected.join(', '));
  if (manifest.release_mode==='governance') {
    const runtime=changed.filter(runtimePath);
    assert.deepEqual(runtime,[], 'Governance request must not modify runtime/style/native files: '+runtime.join(', '));
  }
  if(manifest.release_mode==='preview') {
    assert.equal(manifest.android_release,false,'No Android official release from preview');
    const protectedFiles=changed.filter(p=>p.startsWith('apk-release-parts/') || /^(?:scripts\/release-guard\.cjs|scripts\/sign-android\.py|scripts\/build-cloudflare-pages\.cjs)$/.test(p));
    assert.deepEqual(protectedFiles,[], 'Preview must not change signed APK or release safeguards');
  }
  if (manifest.release_mode==='production' && changed.some(releaseCriticalPath)) {
    assert.equal(manifest.original_key_signing_verified,true,'Production runtime/APK change requires original-key signing proof in request record');
    assert.equal(manifest.website_apk_fingerprint_verified,true,'Production runtime/APK change requires exact signed site fingerprint verification');
  }
  return changed.length;
}
function changedPaths(base){
  const diff=execFileSync('git',['diff','--name-only','--diff-filter=ACDMRT',base+'...HEAD'],{cwd:root,encoding:'utf8'});
  return diff.split(/\r?\n/).filter(Boolean);
}
if(require.main===module){
  try {
    const base=process.argv[2]||'origin/production';
    const manifest=readManifest();
    const changes=changedPaths(base);
    const n=validateScope(changes,manifest);
    console.log('PASS Salati request scope:',manifest.request_id,'mode',manifest.release_mode,'changed paths',n);
    for(const item of changes)console.log(' - '+item);
  } catch(err) {
    console.error('FAIL Salati request scope:',err.message);
    process.exitCode=1;
  }
}
module.exports={validateScope,changedPaths,runtimePath};
