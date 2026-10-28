import {fullSurahUrl} from './quran-audio-source.js';
// Stable across app releases; shell cache updates must not delete these downloads.
export const QURAN_AUDIO_CACHE='salati-quran-downloads-v1';
const valid=(reciter,surah)=>/^(shatri|yasser|qatami|sudais|afasy)$/.test(reciter.id)&&reciter.surahs.includes(Number(surah));
const source=fullSurahUrl;
const key=(reciter,surah)=>reciter.id+':'+surah;

export class QuranOffline{
 constructor({bridge=globalThis.window?.SalatiNative,storage=globalThis.caches,fetcher=(...args)=>fetch(...args),onChange=()=>{},online=()=>globalThis.navigator?.onLine!==false}={}){
  this.bridge=typeof bridge?.quranDownloadStatus==='function'?bridge:null;
  this.storage=storage;this.fetcher=fetcher;this.onChange=onChange;this.online=online;
  this.jobs=new Map();this.queue=[];this.running=false;
 }
 get available(){return !!(this.bridge||this.storage);}
 native(method,...args){const value=JSON.parse(this.bridge[method](...args));if(value.error)throw Error(value.error);return value;}
 async list(reciter){
  if(reciter.fullSurahOnly)return [];
  if(this.bridge)return this.native('quranDownloadStatus',reciter.id).entries||[];
  if(!this.storage)return [];
  const cache=await this.storage.open(QURAN_AUDIO_CACHE),rows=[];
  for(const request of await cache.keys()){
   if(!request.url.startsWith(reciter.server))continue;
   const surah=Number(request.url.slice(reciter.server.length).replace(/\.mp3$/,''));
   if(!valid(reciter,surah))continue;
   const response=await cache.match(request);
   if(response)rows.push({surah,state:'saved',bytes:Number(response.headers.get('content-length'))||0});
  }
  for(const job of this.jobs.values())if(job.reciter.id===reciter.id&&!rows.some(row=>row.surah===job.surah))rows.push({surah:job.surah,state:job.state,bytes:job.bytes||0,total:job.total||0,error:job.error});
  return rows;
 }
 async download(reciter,surah=0){
  if(reciter.fullSurahOnly)throw Error('streaming-only');
  if(!this.available)throw Error('storage');
  if(surah!==0&&!valid(reciter,surah))throw Error('invalid');
  if(this.bridge){this.native('downloadQuran',reciter.id,surah);this.onChange();return;}
  const saved=new Set((await this.list(reciter)).filter(row=>row.state==='saved').map(row=>row.surah));
  for(const id of surah?[surah]:reciter.surahs){
   const idKey=key(reciter,id),prior=this.jobs.get(idKey);
   if(saved.has(id)||prior&&['queued','downloading'].includes(prior.state))continue;
   const job={reciter,surah:id,state:'queued',controller:new AbortController()};
   this.jobs.set(idKey,job);this.queue.push(job);
  }
  globalThis.navigator?.storage?.persist?.().catch(()=>{});
  this.onChange();this.run();
 }
 async run(){
  if(this.running)return;
  this.running=true;
  try{while(this.queue.length){
   const job=this.queue.shift();if(job.controller.signal.aborted)continue;
   job.state='downloading';this.onChange();
   try{await this.save(job);if(this.jobs.get(key(job.reciter,job.surah))===job)this.jobs.delete(key(job.reciter,job.surah));}
   catch(error){if(job.controller.signal.aborted){if(this.jobs.get(key(job.reciter,job.surah))===job)this.jobs.delete(key(job.reciter,job.surah));}else{job.state='failed';job.error=error.name==='QuotaExceededError'?'space':error.message;}}
   this.onChange();
  }}finally{this.running=false;}
 }
 async save(job){
  const url=source(job.reciter,job.surah),response=await this.fetcher(url,{mode:'cors',credentials:'omit',referrerPolicy:'no-referrer',signal:job.controller.signal});
  if(response.status!==200||!response.body||response.type==='opaque')throw Error('network');
  const type=response.headers.get('content-type')||'';
  if(/text\/|json|html/i.test(type))throw Error('audio');
  const reader=response.body.getReader(),expected=Number(response.headers.get('content-length'))||0;
  job.total=expected;job.bytes=0;const prefix=[];let lastUpdate=0;
  const body=new ReadableStream({
   pull:async controller=>{
    try{
     if(job.controller.signal.aborted)throw new DOMException('Cancelled','AbortError');
     const {done,value}=await reader.read();
     if(done){if(job.bytes<128||expected&&expected!==job.bytes)throw Error('incomplete');controller.close();return;}
     for(const byte of value){if(prefix.length>=3)break;prefix.push(byte);}
     if(prefix.length>=3&&!(prefix[0]===73&&prefix[1]===68&&prefix[2]===51)&&!(prefix[0]===255&&(prefix[1]&224)===224))throw Error('audio');
     job.bytes+=value.byteLength;
     if(Date.now()-lastUpdate>250){lastUpdate=Date.now();this.onChange();}
     controller.enqueue(value);
    }catch(error){reader.cancel().catch(()=>{});controller.error(error);}
   },cancel:()=>reader.cancel()
  });
  const headers={'Content-Type':'audio/mpeg'};if(expected)headers['Content-Length']=String(expected);
  const cache=await this.storage.open(QURAN_AUDIO_CACHE);
  await cache.put(url,new Response(body,{status:200,headers}));
  if(job.controller.signal.aborted){await cache.delete(url);throw new DOMException('Cancelled','AbortError');}
 }
 async cancel(reciter){
  if(this.bridge)this.native('cancelQuranDownloads',reciter.id);
  else for(const [id,job]of this.jobs)if(job.reciter.id===reciter.id){job.controller.abort();this.jobs.delete(id);}
  this.onChange();
 }
 async remove(reciter,surah=0){
  if(this.bridge)this.native('deleteQuranDownload',reciter.id,surah);
  else{
   if(!surah)await this.cancel(reciter);
   const cache=await this.storage.open(QURAN_AUDIO_CACHE);
   for(const id of surah?[surah]:reciter.surahs)await cache.delete(source(reciter,id));
  }
  this.onChange();
 }
 async resolve(reciter,surah,url=source(reciter,surah)){
  if(reciter.fullSurahOnly){if(!this.online())throw Error('offline');return {url};}
  if(this.bridge){const local=this.bridge.quranOfflineUrl(reciter.id,surah);if(local)return {url:local};}
  else if(this.storage){
   try{
    const cached=await(await this.storage.open(QURAN_AUDIO_CACHE)).match(url);
    if(cached){const local=URL.createObjectURL(await cached.blob());return {url:local,release:()=>URL.revokeObjectURL(local)};}
   }catch{}
  }
  if(!this.online())throw Error('offline');
  return {url};
 }
}
