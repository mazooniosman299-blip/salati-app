#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict'),https=require('node:https');
const sha=process.argv[2]||'';
assert.match(sha,/^[a-f0-9]{40}$/i,'BLOCK PRODUCTION: invalid SHA');
const base='https://api.github.com/repos/mazooniosman299-blip/salati-app';
function request(path){
 return new Promise((resolve,reject)=>{
  const req=https.get(base+path,{headers:{
   Accept:'application/vnd.github+json',
   'User-Agent':'Salati-Required-Production-Checks',
   'X-GitHub-Api-Version':'2022-11-28'
  },timeout:12000},res=>{
   let body='';res.setEncoding('utf8');
   res.on('data',part=>{body+=part;if(body.length>2000000)req.destroy(new Error('GitHub response too large'))});
   res.on('end',()=>{
    if(res.statusCode!==200)return reject(Error('GitHub checks API returned '+res.statusCode));
    try{resolve(JSON.parse(body))}catch(e){reject(e)}
   });
  });
  req.on('timeout',()=>req.destroy(Error('GitHub checks API timeout')));
  req.on('error',reject);
 });
}
(async()=>{
 const data=await request('/actions/runs?head_sha='+encodeURIComponent(sha)+'&per_page=100');
 const matching=(data.workflow_runs||[]).filter(x=>
  x.head_sha===sha&&x.head_branch==='production'&&x.event==='push'&&
  x.name==='Salati permanent regression protection (NO DEPLOY)');
 assert(matching.length>0,'BLOCK PRODUCTION: no mandatory CI run for the exact SHA');
 const run=matching.sort((a,b)=>Date.parse(b.created_at)-Date.parse(a.created_at))[0];
 assert.equal(run.status,'completed','BLOCK PRODUCTION: CI still running');
 assert.equal(run.conclusion,'success','BLOCK PRODUCTION: CI failed');
 const jobs=await request('/actions/runs/'+run.id+'/jobs?per_page=100');
 for(const name of ['behavior-and-release','actual-browser-ui','real-android-webview','negative-publication-tests']){
  const list=(jobs.jobs||[]).filter(x=>x.name===name);
  assert.equal(list.length,1,'BLOCK PRODUCTION: required job absent: '+name);
  assert.equal(list[0].conclusion,'success','BLOCK PRODUCTION: required job failed: '+name);
 }
 console.log('PASS validated production GitHub Actions required checks:',sha,'run:',run.id);
})().catch(e=>{console.error('BLOCK PRODUCTION:',e.stack||String(e));process.exitCode=1});
