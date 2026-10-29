const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),Module=require('node:module'),esbuild=require('esbuild');
function load(file){const m=new Module(file,module);m._compile(esbuild.buildSync({entryPoints:[file],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,file);return m.exports;}
async function compass(){
 const old=global.window,grants=[],listeners=new Set();global.window={isSecureContext:true,DeviceOrientationEvent:{requestPermission:()=>new Promise((resolve,reject)=>grants.push({resolve,reject}))},addEventListener:n=>listeners.add(n),removeEventListener:n=>listeners.delete(n)};
 const {QiblaCompass}=load('compass.js'),c=new QiblaCompass(()=>({lat:30,lon:31}),()=>{});
 try{
  const pending=c.enable();c.disable();grants[0].resolve('granted');await pending;assert.equal(c.enabled,false,'Disabled compass must not revive after delayed permission');assert.equal(listeners.size,0);
  const first=c.enable(),second=c.enable();grants[2].resolve('granted');await second;assert(c.enabled);assert.equal(listeners.size,2);grants[1].resolve('denied');await first;assert.equal(c.status,'waiting','Stale denied request must not overwrite new active request');assert(c.enabled);
  c.disable();const last=c.enable();c.disable();grants[3].reject(Error('permission dismissed'));await last;assert.equal(c.status,'manual','Stale rejection must not overwrite disabled state');assert.equal(listeners.size,0);
 }finally{c.disable();global.window=old;}
}
async function sessions(){
 const old={window:global.window,document:global.document};global.window=new EventTarget();global.document=new EventTarget();document.visibilityState='visible';const players=[];
 let state={},queue=[],pending,controls=[];
 const bridge={quranState:()=>JSON.stringify({...state,requestedSession:pending?.session||state.session}),quranQueue:()=>JSON.stringify(queue),quranPlay:text=>{pending=JSON.parse(text);return 'ok'},quranPause:s=>controls.push(s),quranStop:()=>{}};
 const acknowledge=()=>{queue=pending.queue;state={session:pending.session,index:0,active:true,paused:false,position:12,duration:60,status:'playing'};};
 const {NativeQuranPlayer}=load('native-quran-player.js');
 try{
  const a=new NativeQuranPlayer(bridge);players.push(a);await a.playQueue([{url:'A'}]);acknowledge();a.sync();const first={...state};
  const b=new NativeQuranPlayer(bridge);players.push(b);await b.playQueue([{url:'B'}]);const waiting=b.session;b.sync();assert.equal(b.session,waiting,'Pending start must not adopt the previous native snapshot');
  acknowledge();b.sync();window.dispatchEvent(new Event('salati-native-resume'));assert.equal(a.session,state.session,'Older Activity must adopt current service session after acknowledgement');assert.equal(a.src,'B');a.pause();assert.equal(controls.at(-1),state.session);
  const late=new Event('salati-native-quran');late.detail=first;window.dispatchEvent(late);assert.equal(a.session,state.session,'Delayed pushed old session must not replace authoritative current session');
  a.stopQueue();a.sync();assert.equal(a.active,false,'Stopped session cannot restart from polling');
  await a.playQueue([{url:'C'}]);const neverAcknowledged=a.session;await b.playQueue([{url:'D'}]);a.sync();assert.equal(a.session,neverAcknowledged,'Latest request metadata must not adopt an old snapshot before replacement starts');acknowledge();a.sync();assert.equal(a.session,state.session,'A start superseded before its first acknowledgement must recover to the started replacement');assert.equal(a.src,'D');
 }finally{for(const p of players)clearInterval(p.timer);Object.assign(global,old);}
}
async function offline(){
 let fetchHandler;const root=new Response(fs.readFileSync('dist/index.html','utf8'),{headers:{'content-type':'text/html'}}),scope='https://salati.test/';
 const context={self:{location:new URL(scope+'sw.js'),registration:{scope},addEventListener:(type,f)=>{if(type==='fetch')fetchHandler=f}},URL,Response,location:{origin:new URL(scope).origin},fetch:async()=>{throw Error('offline')},caches:{match:async key=>key==='./index.html'?root.clone():undefined}};
 vm.runInNewContext(fs.readFileSync('dist/sw.js','utf8'),context);
 for(const path of ['en/prayer-times/unvisited.html','ar/prayer-times/unvisited.html']){
  let promise;const url=scope+path;fetchHandler({request:{url,method:'GET',mode:'navigate'},respondWith:p=>promise=p});const response=await promise;
  if(response.status>=300&&response.status<400){assert.equal(response.headers.get('location'),scope);continue;}
  const html=await response.text(),app=html.match(/src="(app[^\"]+\.js)"/)[1],base=html.match(/<base[^>]+href="([^"]+)"/i)?.[1];assert.equal(new URL(app,base?new URL(base,url):url).pathname,'/'+app,'Offline nested root-shell fallback must resolve assets at root');
 }
}
(async()=>{let failures=0;for(const [name,run] of [['compass cancellation',compass],['native session takeover',sessions],['offline deep link fallback',offline]])try{await run();console.log('PASS: '+name)}catch(e){failures++;console.error('FAIL: '+name+'\n'+e.stack)}process.exitCode=failures?1:0;})();
