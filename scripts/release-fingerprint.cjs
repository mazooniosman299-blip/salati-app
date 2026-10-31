#!/usr/bin/env node
'use strict';
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const ROOT=path.resolve(__dirname,'..');
const DIST=path.join(ROOT,'dist');
function allowed(rel){
  if(rel==='index.html'||rel==='manifest.json')return true;
  if(!rel.includes('/')&&/\.(?:css|js)$/.test(rel))return true;
  return /^(?:images|icons|fonts|quran|audio\/reminders)\//.test(rel);
}
function fingerprint(directory=DIST){
  const selected=[];
  function visit(dir){
    for(const item of fs.readdirSync(dir,{withFileTypes:true})){
      const file=path.join(dir,item.name);
      if(item.isDirectory()){if(!['downloads','.git'].includes(item.name))visit(file);}
      else if(item.isFile()){
        const rel=path.relative(directory,file).split(path.sep).join('/');
        if(allowed(rel))selected.push({rel,file});
      }
    }
  }
  visit(directory);
  selected.sort((a,b)=>a.rel.localeCompare(b.rel,'en'));
  if(selected.length<25)throw Error('Too few web assets for signed-release fingerprint');
  const hash=crypto.createHash('sha256');
  for(const {rel,file} of selected){
    hash.update(rel+'\0','utf8');
    // Cloudflare replaces the verified legacy canonical host with the deployment host.
    // Normalize ONLY that hosting substitution; all other application bytes remain hashed.
    const original=fs.readFileSync(file);
    const data=(rel==='index.html'||rel==='manifest.json')
      ?Buffer.from(original.toString('utf8').replace(
        /https:\/\/(?:salati-world-prayer\.(?:sprytitan65|mazenosman968)\.chatgpt\.site|[a-z0-9.-]+\.pages\.dev)/gi,
        'https://salati-release-origin.invalid'), 'utf8')
      :original;
    const len=Buffer.alloc(8);
    len.writeBigUInt64LE(BigInt(data.length));
    hash.update(len);
    hash.update(data);
  }
  return {sha256:hash.digest('hex'),assets:selected.length};
}
module.exports={fingerprint};
if(require.main===module)console.log(JSON.stringify(fingerprint(),null,2));
