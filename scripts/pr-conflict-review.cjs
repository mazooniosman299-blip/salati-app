#!/usr/bin/env node
'use strict';
/** GitHub PR source collision guard: identifies exact shared EXECUTABLE paths. */
const fs=require('node:fs'),https=require('node:https'),path=require('node:path'),assert=require('node:assert/strict');
const ROOT=path.resolve(__dirname,'..');
const repo='mazooniosman299-blip/salati-app';
function isRuntime(p){return /^(?:dist\/|android\/|[^/]+\.(?:js|css)$|scripts\/(?:build-|release-|sign-|prepare-android)|\.github\/workflows\/(?:publish-|salati-permanent-regression))/i.test(p)}
function intersections(ours,others){
 const a=new Set(ours.filter(isRuntime));
 return others.filter(isRuntime).filter(p=>a.has(p)).sort();
}
function request(endpoint){
 const token=process.env.GITHUB_TOKEN||process.env.GH_TOKEN;
 if(!token)throw Error('No GitHub token; cannot prove live PR compatibility, fail closed');
 return new Promise((resolve,reject)=>{
  const req=https.get('https://api.github.com/repos/'+repo+endpoint,{headers:{
   Accept:'application/vnd.github+json','User-Agent':'Salati-PR-Conflict-Guard',
   Authorization:'Bearer '+token,'X-GitHub-Api-Version':'2022-11-28'
  },timeout:15000},res=>{
   let body='';res.setEncoding('utf8');
   res.on('data',s=>{body+=s;if(body.length>5000000)req.destroy(Error('Too much GitHub API data'))});
   res.on('end',()=>{if(res.statusCode!==200)return reject(Error('GitHub REST returned '+res.statusCode+' '+body.slice(0,250)));
    try{resolve(JSON.parse(body))}catch(e){reject(e)}
   });
  });req.on('error',reject);req.on('timeout',()=>req.destroy(Error('GitHub API timeout')));
 });
}
async function filesFor(pr){
 let all=[];
 for(let page=1;page<=10;page++){
  const data=await request('/pulls/'+pr+'/files?per_page=100&page='+page);
  all.push(...data.map(x=>x.filename));if(data.length<100)break;
 }
 return all;
}
function thisPR(){
 if(!process.env.GITHUB_EVENT_PATH)throw Error('Missing PR event; live PR guard runs only on pull_request');
 const data=JSON.parse(fs.readFileSync(process.env.GITHUB_EVENT_PATH,'utf8'));
 const pr=data.pull_request?.number;
 if(!pr)throw Error('No pull_request.number in GitHub event');
 return pr;
}
function selfTest(){
 assert.deepEqual(intersections(['dist/index.html','AGENTS.md'],['dist/index.html','docs/a.md']),['dist/index.html']);
 assert.deepEqual(intersections(['AGENTS.md'],['dist/index.html']),[]);
 assert.deepEqual(intersections(['dist/index.html'],['tests/legacy.py']),[]);
 assert.deepEqual(intersections(['android/app/src/main/AndroidManifest.xml'],['android/app/src/main/AndroidManifest.xml']),['android/app/src/main/AndroidManifest.xml']);
 assert.deepEqual(intersections(['glass-navigation.js','docs/a.md'],['glass-navigation.js','docs/b.md']),['glass-navigation.js'],'Unlisted frontend modules must be treated as runtime, not documentation');
 console.log('PASS PR collision rejection/allowance self-test');
}
(async()=>{
 if(process.argv.includes('--self-test'))return selfTest();
 const num=thisPR();
 const mine=await filesFor(num);
 const open=await request('/pulls?state=open&base=production&per_page=100');
 const report={own_pr:num,checked:[],fatal_collisions:[],limitations:[
  'Exact shared file path detection; independent files can still cause semantic conflicts',
  'Pixel-level final user acceptance and original signing remain separate gates']};
 for(const other of open){
  if(other.number===num)continue;
  const their=await filesFor(other.number);
  const collisions=intersections(mine,their);
  if(collisions.length){
   const row={pr:other.number,title:other.title,draft:other.draft,head:other.head?.ref,paths:collisions};
   report.fatal_collisions.push(row);
  }
  report.checked.push({pr:other.number,overlap:collisions.length});
 }
 const filename=path.join(ROOT,'reports/pr-overlap-latest.json');
 fs.mkdirSync(path.dirname(filename),{recursive:true});
 fs.writeFileSync(filename,JSON.stringify(report,null,2)+'\n');
 if(report.fatal_collisions.length)throw Error('Conflicting open PR(s) modify the same live Salati files: '+JSON.stringify(report.fatal_collisions));
 console.log('PASS live PR collision guard: PR #'+num+', '+report.checked.length+' other open PRs, zero runtime collisions');
})().catch(e=>{console.error('BLOCK conflicting PR:',e.message);process.exitCode=1});
