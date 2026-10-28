const assert=require('node:assert/strict'),Module=require('node:module'),esbuild=require('esbuild');
function load(file){const m=new Module(file,module);m._compile(esbuild.buildSync({entryPoints:[file],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,file);return m.exports;}
const {QuranOffline}=load('quran-offline.js'),{PageRecitation}=load('quran-page-audio.js');
const {QURAN_RECITERS}=load('quran-controller.js');
const qatami=QURAN_RECITERS.find(r=>r.id==='qatami'),shatri=QURAN_RECITERS.find(r=>r.id==='shatri');
const mp3=new Uint8Array(2048);mp3.set([73,68,51]);for(let i=3;i<mp3.length;i++)mp3[i]=i%251;
class Cache{
 constructor(){this.rows=new Map();}
 async keys(){return [...this.rows.keys()].map(url=>new Request(url));}
 async match(request){return this.rows.get(request.url||request)?.clone();}
 async put(url,response){const bytes=await response.arrayBuffer();this.rows.set(url,new Response(bytes,{status:200,headers:response.headers}));}
 async delete(url){return this.rows.delete(url.url||url);}
}
const response=()=>new Response(mp3,{status:200,headers:{'Content-Type':'audio/mpeg','Content-Length':String(mp3.length)}});
const settle=async offline=>{for(let i=0;i<300&&offline.running;i++)await new Promise(resolve=>setTimeout(resolve,1));assert(!offline.running,'Downloads did not finish');};
class Player extends EventTarget{
 constructor(){super();this.src='';this.loop=false;this.paused=true;}
 getAttribute(){return this.src||null;}removeAttribute(){this.src='';}load(){}pause(){this.paused=true;}play(){this.paused=false;return Promise.resolve();}
}
(async()=>{
 const cache=new Cache(),storage={open:async()=>cache};let networkCalls=0;
 const online=new QuranOffline({bridge:null,storage,fetcher:async()=>{networkCalls++;return response();},online:()=>true});
 await online.download(qatami,1);await settle(online);
 assert.equal(networkCalls,1);assert.equal((await online.list(qatami))[0].state,'saved');
 await online.download(qatami,1);await settle(online);assert.equal(networkCalls,1,'Saved audio must not be downloaded twice');
 const disconnected=new QuranOffline({bridge:null,storage,fetcher:()=>{throw Error('Network disabled');},online:()=>false});
 assert.equal((await disconnected.list(qatami))[0].surah,1,'Saved downloads must survive a new store instance');
 assert.equal((await disconnected.list(shatri)).length,0,'Reciters must have separate downloads');
 const local=await disconnected.resolve(qatami,1);assert(local.url.startsWith('blob:'));
 assert.deepEqual(new Uint8Array(await(await fetch(local.url)).arrayBuffer()),mp3,'Offline bytes must match the downloaded audio');local.release();
 await assert.rejects(disconnected.resolve(shatri,1),/offline/);
 await disconnected.cancel(qatami);assert.equal((await disconnected.list(qatami))[0].state,'saved','Cancel must retain completed files');
 const player=new Player(),errors=[];
 const playback=new PageRecitation({player,onError:e=>errors.push(e),onVerse:()=>{},onComplete:()=>{},resolveSource:(...args)=>disconnected.resolve(...args)});
 await playback.playSurah(qatami,1);assert(player.src.startsWith('blob:'));assert.equal(playback.surahKey,'qatami:1');playback.stop();
 await playback.playSurah(shatri,1);assert.deepEqual(errors,['offline']);assert.equal(player.src,'');
 let complete,releaseCount=0;
 const waiting=new PageRecitation({player,onError:()=>{},onVerse:()=>{},onComplete:()=>{},resolveSource:()=>new Promise(resolve=>complete=resolve)});
 const pending=waiting.playSurah(qatami,1);await Promise.resolve();waiting.stop();complete({url:'blob:stale',release:()=>releaseCount++});await pending;
 assert.equal(player.src,'');assert.equal(releaseCount,1,'Stopping while loading must release a stale source without starting playback');
 await disconnected.remove(qatami,1);await assert.rejects(disconnected.resolve(qatami,1),/offline/);
 const broken=new QuranOffline({bridge:null,storage,fetcher:async()=>new Response('<html>error</html>',{headers:{'Content-Type':'text/html'}})});
 await broken.download(qatami,2);await settle(broken);assert.equal((await broken.list(qatami))[0].state,'failed');assert.equal(cache.rows.size,0);
 broken.fetcher=async()=>new Response(mp3.slice(0,500),{headers:{'Content-Type':'audio/mpeg','Content-Length':'2048'}});
 await broken.download(qatami,2);await settle(broken);assert.equal(cache.rows.size,0,'A truncated download must not be marked saved');
 const quotaCache=new Cache();quotaCache.put=async(url,response)=>{await response.body.cancel();throw new DOMException('Full','QuotaExceededError');};
 const full=new QuranOffline({bridge:null,storage:{open:async()=>quotaCache},fetcher:async()=>response()});
 await full.download(qatami,3);await settle(full);assert.equal((await full.list(qatami))[0].error,'space');
 let started;
 const cancelled=new QuranOffline({bridge:null,storage,fetcher:(url,{signal})=>new Promise((resolve,reject)=>{started=true;signal.addEventListener('abort',()=>reject(new DOMException('Cancelled','AbortError')));})});
 await cancelled.download(qatami,4);await Promise.resolve();assert(started);await cancelled.cancel(qatami);await settle(cancelled);assert.equal((await cancelled.list(qatami)).length,0);
 let rejectOld,finishRetry,retryStarted=false,attempt=0;
 const retry=new QuranOffline({bridge:null,storage,fetcher:()=>++attempt===1?new Promise((resolve,reject)=>rejectOld=reject):new Promise(resolve=>{retryStarted=true;finishRetry=resolve;})});
 await retry.download(qatami,4);await Promise.resolve();await retry.cancel(qatami);await retry.download(qatami,4);
 rejectOld(new DOMException('Cancelled','AbortError'));await new Promise(resolve=>setImmediate(resolve));assert(retryStarted);
 assert.equal((await retry.list(qatami))[0].state,'downloading','A late cancellation must not erase the immediately restarted download');
 finishRetry(response());await settle(retry);assert.equal((await retry.list(qatami))[0].state,'saved');await retry.remove(qatami,4);
 const small={...qatami,surahs:[1,2,3]};const all=new QuranOffline({bridge:null,storage,fetcher:async()=>response()});
 await all.download(small);await settle(all);assert.equal((await all.list(small)).length,3);await all.remove(small);assert.equal(cache.rows.size,0);
 const calls=[],bridge={quranDownloadStatus:()=>JSON.stringify({entries:[{surah:1,state:'saved'}]}),downloadQuran:(...args)=>{calls.push(args);return '{"ok":true}';},quranOfflineUrl:()=> 'https://appassets.androidplatform.net/quran-offline/qatami/001.mp3',cancelQuranDownloads:()=>'{"ok":true}',deleteQuranDownload:()=>'{"ok":true}'};
 const native=new QuranOffline({bridge,storage:null,online:()=>false});await native.download(qatami,1);assert.deepEqual(calls,[['qatami',1]]);assert((await native.resolve(qatami,1)).url.includes('/quran-offline/qatami/001.mp3'));
 for(const id of ['afasy']){const reciter=QURAN_RECITERS.find(r=>r.id===id);const added=new QuranOffline({bridge:null,storage,fetcher:async()=>response()});await added.download(reciter,114);await settle(added);assert.equal((await added.list(reciter))[0].surah,114);const offline=new QuranOffline({bridge:null,storage,online:()=>false});const result=await offline.resolve(reciter,114);assert(result.url.startsWith('blob:'));result.release();await offline.remove(reciter,114);}
 const studio=QURAN_RECITERS.find(r=>r.id==='sudais');let oldCacheCalled=false;const studioStream=new QuranOffline({bridge:{quranOfflineUrl:()=>{oldCacheCalled=true;throw Error('Legacy cache must not serve studio recording');}},online:()=>true});assert.equal((await studioStream.resolve(studio,1)).url,studio.surahUrls[1]);assert(!oldCacheCalled);assert.deepEqual(await studioStream.list(studio),[]);await assert.rejects(studioStream.download(studio,1),/streaming-only/);const studioOffline=new QuranOffline({bridge:null,storage,online:()=>false});await assert.rejects(studioOffline.resolve(studio,1),/offline/);
 console.log('Offline Quran: persisted byte-identical playback with network disabled, reciter isolation, bulk download, cancellation, deletion, quota/truncation failure and native routing pass.');
})().catch(error=>{console.error(error);process.exitCode=1;});
