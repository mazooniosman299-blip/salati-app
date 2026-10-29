const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const listeners={},cached=new Map();let networkCalls=0;
const context={URL,Response,location:{origin:'https://salati.test'},self:{addEventListener:(name,fn)=>listeners[name]=fn},caches:{match:async request=>cached.get(typeof request==='string'?request:request.url),open:async()=>({put:async()=>{}})},fetch:async()=>{networkCalls++;throw Error('offline')}};
vm.runInNewContext(fs.readFileSync('dist/sw.js','utf8'),context);
(async()=>{
 for(const file of ['fajr-user-approved-1.0.103']){
  const url='https://salati.test/audio/reminders/'+file+'.mp3',recording=new Response('valid cached recording',{headers:{'Content-Type':'audio/mpeg'}});cached.set(url,recording);
  let response;listeners.fetch({request:{method:'GET',url},respondWith:value=>response=Promise.resolve(value),waitUntil(){}});
  assert(response,'service worker must intercept bundled reminder audio offline');assert.equal(await response,recording);
 }
 assert.equal(networkCalls,0,'cached reminder previews start immediately without waiting for network');
 let intercepted=false;listeners.fetch({request:{method:'GET',url:'https://salati.test/audio/nufais-clean-v3.mp3'},respondWith(){intercepted=true}});assert.equal(intercepted,false,'legacy adhan retains its dedicated audio cache');
 console.log('PASS: approved Fajr recording request served from shell cache; legacy adhan bypass preserved.');
})().catch(error=>{console.error(error);process.exitCode=1});
