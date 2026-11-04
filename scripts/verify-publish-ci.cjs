#!/usr/bin/env node
'use strict';
/** Do not publish while required CI is running; await the EXACT production SHA.
 * Cloudflare may begin its build before GitHub Actions reaches completion.
 * Wait within a finite bound, require all four real jobs, and fail closed
 * on failure/API error/timeout. This does not bypass original-key APK checks.
 */
const assert=require('node:assert/strict'),https=require('node:https');
const base='https://api.github.com/repos/mazooniosman299-blip/salati-app';
const mandatory=['behavior-and-release','actual-browser-ui','real-android-webview','negative-publication-tests'];
const MAX_WAIT_MS=13*60*1000;
const POLL_MS=30000;
function requestHeaders(env=process.env){
 const headers={
  Accept:'application/vnd.github+json',
  'User-Agent':'Salati-Required-Production-Checks',
  'X-GitHub-Api-Version':'2022-11-28'
 };
 // Explicit build-only secret. Never implicitly copy a general workspace token,
 // and never include this value in logs, frontend bundles or error messages.
 const token=String(env.SALATI_GITHUB_CHECKS_TOKEN||'').trim();
 assert(!/[\x00-\x20\x7f]/.test(token),'Invalid SALATI_GITHUB_CHECKS_TOKEN characters');
 if(token)headers.Authorization='Bearer '+token;
 return headers;
}
function githubAPIError(status,headers={}){
 const digits=value=>/^\d{1,12}$/.test(String(value||''))?String(value):'unknown';
 const remaining=digits(headers['x-ratelimit-remaining']);
 const reset=digits(headers['x-ratelimit-reset']);
 const when=reset==='unknown'?'unknown':new Date(Number(reset)*1000).toISOString();
 // Response bodies and unvalidated header values may contain secrets; never log them.
 return Error('GitHub checks API returned '+status+'; rate-limit remaining='+remaining+' reset='+when+
  (status===401||status===403?'; configure SALATI_GITHUB_CHECKS_TOKEN as an encrypted Cloudflare Production secret with repository Actions read-only access':''));
}
function request(uri){
 return new Promise((resolve,reject)=>{
  // Fixed HTTPS GitHub host/repository; redirects are rejected, not followed.
  const req=https.get(base+uri,{headers:requestHeaders(),timeout:12000},res=>{
   let body='';res.setEncoding('utf8');
   res.on('data',part=>{body+=part;if(body.length>2000000)req.destroy(Error('GitHub response too large'))});
   res.on('end',()=>{
    if(res.statusCode!==200)return reject(githubAPIError(res.statusCode,res.headers));
    try{resolve(JSON.parse(body))}catch{reject(Error('GitHub checks API returned invalid JSON'))}
   });
  });
  req.on('timeout',()=>req.destroy(Error('GitHub checks API timeout')));
  req.on('error',error=>reject(Error(error?.message==='GitHub checks API timeout'?'GitHub checks API timeout':'GitHub checks API network failure')));
 });
}
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
function latestCorrectRun(data,sha){
 const matching=(data.workflow_runs||[]).filter(x=>x.head_sha===sha
  &&x.head_branch==='production'&&x.event==='push'
  &&x.name==='Salati permanent regression protection (NO DEPLOY)');
 return matching.sort((a,b)=>Date.parse(b.created_at)-Date.parse(a.created_at))[0]||null;
}
function requiredJobsSuccess(jobs){
 for(const name of mandatory){
  const match=(jobs.jobs||[]).filter(x=>x.name===name);
  assert.equal(match.length,1,'BLOCK PRODUCTION: required job absent: '+name);
  assert.equal(match[0].conclusion,'success','BLOCK PRODUCTION: required job failed: '+name);
 }
 return true;
}
async function verify(sha,{fetch=request,wait=sleep,clock=Date.now,maxWaitMs=MAX_WAIT_MS,pollMs=POLL_MS,report=console.log}={}){
 assert.match(sha,/^[a-f0-9]{40}$/i,'BLOCK PRODUCTION: invalid SHA');
 const started=clock();let attempts=0;
 while(true){
  attempts++;
  const result=await fetch('/actions/runs?head_sha='+encodeURIComponent(sha)+'&per_page=100');
  const run=latestCorrectRun(result,sha);
  if(run&&run.status==='completed'){
   assert.equal(run.conclusion,'success','BLOCK PRODUCTION: CI failed');
   const jobs=await fetch('/actions/runs/'+run.id+'/jobs?per_page=100');
   requiredJobsSuccess(jobs);
   report('PASS validated production GitHub Actions required checks: '+sha+' run: '+run.id+' polls: '+attempts);
   return run.id;
  }
  const elapsed=clock()-started;
  assert(elapsed<maxWaitMs,'BLOCK PRODUCTION: required CI still running/unregistered after '+Math.round(elapsed/1000)+'s; deployment timed out safely');
  // This finite wait prevents normal push-vs-CI webhook races; never
  // interpret 'queued' or 'in_progress' as proof of successful checks.
  report('WAIT PRODUCTION CI: '+sha.slice(0,8)+' state='+(run?.status||'not registered')+' elapsed='+Math.round(elapsed/1000)+'s');
  await wait(Math.min(pollMs,maxWaitMs-elapsed));
 }
}
if(require.main===module){
 verify(process.argv[2]||'').catch(e=>{console.error('BLOCK PRODUCTION:',e.stack||String(e));process.exitCode=1});
}
module.exports={verify,latestCorrectRun,requiredJobsSuccess,MAX_WAIT_MS,POLL_MS,requestHeaders,githubAPIError};
