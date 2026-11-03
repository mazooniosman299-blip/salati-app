#!/usr/bin/env node
'use strict';
/** Fail-closed declared scope and independent signed release proof. */
const assert=require('node:assert/strict');
const fs=require('node:fs'),crypto=require('node:crypto'),os=require('node:os'),path=require('node:path');
const {execFileSync}=require('node:child_process');
const root=path.resolve(__dirname,'..');
const runtimePath=p=>/^(?:dist\/|android\/|apk-release-parts\/|[^/]+\.js$|[^/]+\.css$|scripts\/(?:build-web|build-cloudflare-pages|release-guard|release-fingerprint|verify-publish-ci|prepare-android|sign-android|reconstruct-verified-apk)\.(?:cjs|py|sh)$)/.test(p);
const requiresWebVisualDiff=files=>files.some(p=>/^(?:dist\/(?:index\.html|.*\.(?:css|js|svg|png|webp|ttf|json))|[^/]+\.(?:js|css))$/.test(p));
const releaseCriticalPath=p=>runtimePath(p)||/^scripts\/(?:build-|release-|sign-|prepare-android)/.test(p);
function independentReleaseVerification() {
 const {verifiedManifest}=require('./release-guard.cjs');
 const release=verifiedManifest(); // exact current site fingerprint + release version
 const dir=path.join(root,'apk-release-parts','v'+release.version);
 const tool=process.env.ANDROID_HOME && path.join(process.env.ANDROID_HOME,'build-tools','36.0.0','apksigner');
 assert(tool && fs.existsSync(tool),'Original-key APK verification requires Android SDK build-tools/36.0.0/apksigner, not a claimed boolean');
 const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'salati-original-cert-'));
 const apk=path.join(tmp,release.filename);
 try {
  const fd=fs.openSync(apk,'w');
  const hash=crypto.createHash('sha256');
  let count=0;
  try {for(let i=0;i<release.partCount;i++){
   const p=path.join(dir,'part'+String(i).padStart(2,'0')+'.bin');
   const bytes=fs.readFileSync(p);
   fs.writeSync(fd,bytes);hash.update(bytes);count+=bytes.length;
  }}finally{fs.closeSync(fd);}
  assert.equal(count,release.size,'Signed APK byte size mismatch');
  assert.equal(hash.digest('hex'),release.sha256,'Signed APK actual SHA-256 mismatch');
  const output=execFileSync(tool,['verify','--print-certs',apk],{encoding:'utf8',timeout:120000});
  const match=output.match(/Signer #1 certificate SHA-256 digest:\s*([0-9a-f:]+)/i);
  assert(match,'apksigner did not independently report a signer certificate');
  assert.equal(match[1].replace(/:/g,'').toLowerCase(),release.certificateSha256,'Original signing certificate NOT present in reconstructed APK');
  console.log('PASS independently inspected signed APK SHA, cert and exact linked website fingerprint:',release.version);
 }finally{fs.rmSync(tmp,{recursive:true,force:true});}
}
function validateScope(changed,manifest,options={}) {
 assert(manifest && /^SALATI-\d{8}-[A-Z0-9-]+$/.test(manifest.request_id||''),'Missing valid per-request ID');
 assert.equal(manifest.base_branch,'production','Salati work must start from production');
 assert(['governance','preview','production','infrastructure'].includes(manifest.release_mode),'Declare release_mode');
 assert(Array.isArray(manifest.allowed_paths)&&manifest.allowed_paths.length>0,'Empty scope allowlist');
 assert.equal(new Set(manifest.allowed_paths).size,manifest.allowed_paths.length,'Duplicate paths');
 assert(manifest.allowed_paths.every(p=>typeof p==='string'&&p.length>0&&!p.startsWith('/')&&!p.includes('..')&&!p.includes('*')),'Only exact repository-relative paths allowed');
 if(manifest.visual_change===true){
  assert(Array.isArray(manifest.visual_allowed_regions)&&manifest.visual_allowed_regions.length>0,'Visual request must explicitly list allowed DOM selector/tab/language regions');
  assert(manifest.visual_allowed_regions.every(x=>typeof x.selector==='string'&&x.selector.trim()&&['times','mushaf','qibla','dhikr','tasbih','settings'].includes(x.tab)&&['ar','en','both'].includes(x.language)),'Invalid approved visual regions');
  // A color/position request is not implementable from a CSS selector alone.
  // Record the exact current vs requested result and every property to preserve.
  assert(manifest.visual_allowed_regions.every(x=>typeof x.before==='string'&&x.before.trim()&&typeof x.after==='string'&&x.after.trim()&&Array.isArray(x.preserve)&&x.preserve.length>0),'Visual request missing before/after/preserve contract');
  assert(manifest.visual_allowed_regions.every(x=>x.preserve.every(y=>typeof y==='string'&&y.trim())),'Preserved component properties must be explicit');
  assert(manifest.visual_allowed_regions.every(x=>x.selector.startsWith('#')||x.selector.startsWith('.')),'Visual targets must identify a real DOM id/class, not a vague page description');
 }
 assert(changed.length>0,'No PR file changes');
 const unexpected=changed.filter(p=>!manifest.allowed_paths.includes(p));
 assert.deepEqual(unexpected,[],'OUT-OF-SCOPE FILES: '+unexpected.join(', '));
 if(manifest.release_mode==='governance') {
  const execution=changed.filter(runtimePath);
  assert.deepEqual(execution,[],'Governance changes cannot mutate web/native/build/signing: '+execution.join(', '));
 }
 if(manifest.release_mode==='infrastructure') {
  assert.equal(manifest.visual_change,false,'Infrastructure cannot claim a visual change');
  assert.equal(manifest.android_release,false,'Infrastructure cannot publish an Android update');
  const allowedInfra=new Set(['package.json','scripts/verify-publish-ci.cjs','tests/publish-ci-wait.cjs','scripts/verify-change-scope.cjs','tests/agent-governance-contract.cjs','tests/android-emulator-screen-preflight.py','scripts/android-webview-smoke.sh','docs/requests/ACTIVE_CHANGE.json','docs/requests/ACCEPTANCE_STATUS.json']);
  const forbidden=changed.filter(p=>!allowedInfra.has(p));
  assert.deepEqual(forbidden,[],'Infrastructure request cannot edit app, signed release or other unapproved code: '+forbidden.join(', '));
 }
 if(manifest.release_mode==='preview') {
  assert.equal(manifest.android_release,false,'Preview must not publish Android release');
  const protectedPaths=changed.filter(p=>p.startsWith('apk-release-parts/')||/^(?:scripts\/release-guard\.cjs|scripts\/sign-android\.py|scripts\/build-cloudflare-pages\.cjs)$/.test(p));
  assert.deepEqual(protectedPaths,[],'Preview cannot modify signed release or production guards');
 }
 if(manifest.release_mode==='production' && changed.some(releaseCriticalPath)) {
  // NEVER treat boolean flags in user- or agent-edited JSON as signing evidence.
  (options.releaseVerifier||independentReleaseVerification)();
 }
 return changed.length;
}
function changedPaths(base) {
 const diff=execFileSync('git',['diff','--name-only','--diff-filter=ACDMRT',base+'...HEAD'],{cwd:root,encoding:'utf8'});
 return diff.split(/\r?\n/).filter(Boolean);
}
if(require.main===module) {
 try{
  const current=JSON.parse(fs.readFileSync(path.join(root,'docs/requests/ACTIVE_CHANGE.json'),'utf8'));
  const files=changedPaths(process.argv[2]||'origin/production');
  const n=validateScope(files,current);
  console.log('PASS scoped Salati change request',current.request_id,current.release_mode,n,'files');
  files.forEach(p=>console.log(' - '+p));
 }catch(e){console.error('FAIL scoped Salati change:',e.stack||e);process.exitCode=1;}
}
module.exports={validateScope,changedPaths,runtimePath,requiresWebVisualDiff,independentReleaseVerification};
