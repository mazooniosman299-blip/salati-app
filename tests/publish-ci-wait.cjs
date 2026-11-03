#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');
const {verify,latestCorrectRun,requiredJobsSuccess}=require('../scripts/verify-publish-ci.cjs');
const sha='a'.repeat(40),wrong='b'.repeat(40);
const correct={head_sha:sha,head_branch:'production',event:'push',name:'Salati permanent regression protection (NO DEPLOY)',created_at:'2026-11-03T02:00:00Z',id:123,status:'completed',conclusion:'success'};
const older={...correct,id:122,created_at:'2026-11-02T02:00:00Z',conclusion:'failure'};
const jobNames=['behavior-and-release','actual-browser-ui','real-android-webview','negative-publication-tests'];
const ready={jobs:jobNames.map(name=>({name,conclusion:'success'}))};
assert.equal(latestCorrectRun({workflow_runs:[older,correct,{...correct,id:555,head_sha:wrong}]},sha).id,123,'Wrong CI run selected');
assert.equal(latestCorrectRun({workflow_runs:[{...correct,head_branch:'main'}]},sha),null,'Old/default branch must not satisfy exact production CI');
assert(requiredJobsSuccess(ready));
assert.throws(()=>requiredJobsSuccess({jobs:ready.jobs.slice(0,3)}),/required job absent/);
assert.throws(()=>requiredJobsSuccess({jobs:ready.jobs.map(x=>x.name===jobNames[3]?{...x,conclusion:'failure'}:x)}),/required job failed/);
let polls=0,minutes=0;
const responses=[
 {workflow_runs:[]},
 {workflow_runs:[{...correct,status:'in_progress',conclusion:null}]},
 {workflow_runs:[correct]},
 ready
];
const okFetch=async path=>{
 polls++;
 if(path.includes('/jobs?'))return responses[3];
 return responses[Math.min(polls-1,2)];
};
(async()=>{
 const result=await verify(sha,{fetch:okFetch,wait:async()=>{minutes+=1},clock:()=>minutes*1000,maxWaitMs:10000,pollMs:1000,report:()=>{}});
 assert.equal(result,123,'Correct in-progress SHA should finally succeed');
 assert.equal(polls,4,'Expected 3 run polls + 1 jobs proof');
 assert.equal(minutes,2,'Expected bounded wait only while unfinished');
 await assert.rejects(verify(sha,{fetch:async()=>({workflow_runs:[{...correct,conclusion:'failure'}]}),wait:async()=>{},clock:()=>0,maxWaitMs:1000,report:()=>{}}),/CI failed/,'Fail closed if CI failed');
 await assert.rejects(verify(sha,{fetch:async()=>({workflow_runs:[{...correct,status:'queued'}]}),wait:async()=>{},clock:(()=>{let n=0;return ()=>n++*1000})(),maxWaitMs:1000,pollMs:100,report:()=>{}}),/still running/,'Never accept running CI');
 await assert.rejects(verify(sha,{fetch:async()=>{throw Error('GitHub API down')},wait:async()=>{},clock:()=>0,maxWaitMs:1000,report:()=>{}}),/GitHub API down/,'API failure cannot bypass release');
 await assert.rejects(verify(wrong.slice(1),{fetch:async()=>({}),clock:()=>0}),/invalid SHA/);
 console.log('PASS production CI staging: bounded await of exact production SHA, four required green jobs, fail-closed on failed/missing/running/API errors');
})().catch(e=>{console.error(e);process.exitCode=1});
