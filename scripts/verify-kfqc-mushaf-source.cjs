#!/usr/bin/env node
'use strict';
/**
 * Verify that any imported Mushaf pages are the exact approved KFQC originals.
 * This is a source-asset gate, NOT approval of any green/pink #5 page frame.
 * Never rewrites Quran text, UI, audio, production assets, or release identity.
 */
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const https=require('node:https');
const MANIFEST=path.resolve(__dirname,'../reference-data/kfqc-hafs-604-plate-manifest.json');

function gitBlobSha1(buffer){
  return crypto.createHash('sha1').update('blob '+buffer.length+'\0').update(buffer).digest('hex');
}
function validateManifest(m){
  if(m?.schema!==1||m?.pageCount!==604||!Array.isArray(m.pages)||m.pages.length!==604)
    throw Error('KFQC source manifest must contain exactly 604 numbered pages');
  if(m.source?.repo!=='quran-ws/quran-svg'||!(/^[0-9a-f]{40}$/.test(m.source.revision))||
     m.source.subpath!=='mushafs/hafs/kfqc/svg')
    throw Error('Unpinned or incorrect authorized KFQC source');
  if(m.source.license!=='https://dm.qurancomplex.gov.sa/rights/')
    throw Error('Original publisher usage rights must be documented');
  for(let i=0;i<604;i++){
    const x=m.pages[i],number=String(i+1).padStart(3,'0');
    if(x?.page!==i+1||x.path!=='mushafs/hafs/kfqc/svg/'+number+'.svg')
      throw Error('Missing, unordered or renamed original plate: '+number);
    if(!Number.isSafeInteger(x.bytes)||x.bytes<1000||x.bytes>25*1024*1024||
       !/^[0-9a-f]{40}$/.test(x.gitBlobSha1))
      throw Error('Invalid plate size or content hash: '+number);
  }
  return true;
}
function verifyPlate(bytes,entry){
  const buf=Buffer.isBuffer(bytes)?bytes:Buffer.from(bytes);
  if(buf.length!==entry.bytes||gitBlobSha1(buf)!==entry.gitBlobSha1)
    throw Error('Plate bytes differ from pinned authorized source: page '+entry.page);
  const start=buf.subarray(0,1024).toString('utf8');
  if(!start.includes('<svg')||!start.includes('http://www.w3.org/2000/svg'))
    throw Error('Original plate is not a valid SVG document: page '+entry.page);
  return true;
}
function fetchOriginal(m,entry){
  const url='https://raw.githubusercontent.com/'+m.source.repo+'/'+m.source.revision+'/'+entry.path;
  return new Promise((resolve,reject)=>{
    https.get(url,{timeout:25000,headers:{'User-Agent':'salati-mushaf-source-verifier'}},response=>{
      if(response.statusCode!==200){
        response.resume();reject(Error('Source download HTTP '+response.statusCode+' page '+entry.page));return;
      }
      const chunks=[];let n=0;
      response.on('data',chunk=>{n+=chunk.length;if(n>entry.bytes){response.destroy(Error('Oversized page '+entry.page));return;}chunks.push(chunk);});
      response.on('end',()=>resolve(Buffer.concat(chunks)));
      response.on('error',reject);
    }).on('error',reject);
  });
}
async function main(){
  const m=JSON.parse(fs.readFileSync(MANIFEST,'utf8'));validateManifest(m);
  const total=m.pages.reduce((sum,p)=>sum+p.bytes,0);
  console.log('PASS KFQC manifest: exactly 604 Hafs print plates, pinned revision '+m.source.revision+', '+total+' bytes');
  const argv=process.argv.slice(2);
  if(!argv.length)return;
  if(argv[0]==='--verify-samples'){
    if(argv.length!==1)throw Error('Usage: --verify-samples');
    for(const page of [1,12,604]){
      const plate=m.pages[page-1];verifyPlate(await fetchOriginal(m,plate),plate);
      console.log('PASS original source bytes SHA-1 page '+page);
    }
  }else if(argv[0]==='--verify-directory'){
    if(argv.length!==2)throw Error('Usage: --verify-directory <full-604-page-folder>');
    const root=path.resolve(argv[1]);
    for(const entry of m.pages)verifyPlate(fs.readFileSync(path.join(root,String(entry.page).padStart(3,'0')+'.svg')),entry);
    console.log('PASS all 604 imported original plate hashes (does not verify style #5 ornament artwork)');
  }else throw Error('Unknown mode; use --verify-samples or --verify-directory <folder>');
}
if(require.main===module)main().catch(error=>{console.error('FAIL KFQC artwork verification:',error.message);process.exitCode=1});
module.exports={validateManifest,verifyPlate,gitBlobSha1,fetchOriginal};
