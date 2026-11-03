#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const manifest=JSON.parse(fs.readFileSync(path.join(root,'design-references/APPROVED_REFERENCE_REGISTRY.json'),'utf8'));
const refs=manifest.references;
assert(refs.length>=7);
assert.equal(new Set(refs.map(r=>r.id)).size,refs.length,'Duplicate visual reference identifiers');
let verified=0,unresolved=0;
for(const ref of refs){
 assert(ref.status&&ref.source&&ref.element&&ref.rights,'Missing provenance metadata: '+ref.id);
 if(ref.status.startsWith('verified-')){
  assert(ref.file&&/^[a-f0-9]{64}$/.test(ref.sha256||''),'Approved references require exact bytes and SHA256: '+ref.id);
  const file=path.resolve(root,ref.file);
  assert(file.startsWith(root+path.sep),'Reference escaped repository');
  assert(fs.existsSync(file),'Missing approved original asset: '+ref.file);
  const hash=crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
  assert.equal(hash,ref.sha256,'Reference image was changed or substituted: '+ref.file);
  verified++;
 }else {
  assert(!ref.sha256||ref.file,'Unknown image digest is not a verified reference');
  unresolved++;
 }
}
const original=refs.find(x=>x.id==='mosque-original');
assert.equal(original.sha256,JSON.parse(fs.readFileSync(path.join(root,'design-references/mosque-crop.json'),'utf8')).source_sha256);
const web=refs.find(x=>x.id==='mosque-web-cropped'),native=refs.find(x=>x.id==='mosque-native-cropped');
assert.equal(web.sha256,native.sha256,'Widget and browser original mosque must match exactly');
console.log('PASS reference provenance',verified,'verified image bytes;',unresolved,'historical/unresolved (NOT certified). No generated image substituted.');
