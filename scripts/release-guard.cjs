#!/usr/bin/env node
'use strict';
const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const {fingerprint}=require('./release-fingerprint.cjs');
function verifiedManifest(){
  const pointer=JSON.parse(fs.readFileSync(path.join(root,'apk-release-parts/current.json'),'utf8'));
  if(!/^1\.0\.\d+$/.test(pointer.version))throw Error('Invalid current signed APK version');
  const file=path.join(root,'apk-release-parts','v'+pointer.version,'manifest.json');
  const manifest=JSON.parse(fs.readFileSync(file,'utf8'));
  if(manifest.version!==pointer.version||manifest.filename!=='salati-'+pointer.version+'.apk')
    throw Error('Signed release version or filename mismatch');
  if(manifest.applicationId!=='com.salati.prayer' ||
     manifest.certificateSha256!=='559dec66ab13e86be17c661732f1d2b1751a63261ed7d7d353b857f693cf056e')
    throw Error('Untrusted APK signing identity');
  if(!/^[0-9a-f]{64}$/.test(manifest.sha256)||!Number.isSafeInteger(manifest.size))
    throw Error('Missing immutable signed APK checksum or byte count');
  if(!Number.isInteger(manifest.partCount)||manifest.partCount<1)
    throw Error('Missing signed APK blob inventory');
  const gradle=fs.readFileSync(path.join(root,'android/app/build.gradle'),'utf8');
  if(!gradle.includes("getOrElse('"+manifest.versionCode+"')")||
     !gradle.includes("getOrElse('"+manifest.version+"')"))
    throw Error('Android versionCode/versionName mismatch with website release');
  const html=fs.readFileSync(path.join(root,'dist/index.html'),'utf8');
  if(!html.includes('href="/downloads/'+manifest.filename+'"')||
     !html.includes('class="app-version">v'+manifest.version+'</small>'))
    throw Error('Website footer or download link points to stale APK');
  const fp=fingerprint();
  if(fp.sha256!==manifest.webFingerprint)
    throw Error('Website assets do NOT match APK release ('+fp.sha256+' vs '+manifest.webFingerprint+'). Refusing publication.');
  return manifest;
}
module.exports={verifiedManifest};
if(require.main===module){
  const release=verifiedManifest();
  console.log('Website and signed APK release synchronized:',release.version,release.sha256);
}
