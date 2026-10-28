const assert=require('node:assert/strict'),Module=require('node:module'),esbuild=require('esbuild');const m=new Module(__filename,module);m._compile(esbuild.buildSync({entryPoints:['audio-controller.js'],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,__filename);const {PrayerAudio}=m.exports;
(async()=>{try{
 for(const mode of ['corrupt-cache','corrupt-network','quota','blocked-cache']){
  let requests=0,decodes=0;const data=new Map();if(mode==='corrupt-cache')data.set('audio/test',new Response('bad'));
  global.caches={keys:async()=>['salati-audio-v4'],open:async()=>{if(mode==='blocked-cache')throw Error('SecurityError');return {match:async key=>data.get(key)?.clone(),delete:async key=>data.delete(key),put:async(key,r)=>{if(mode==='quota')throw Error('quota');data.set(key,r);}};}};
  global.fetch=async()=>new Response(mode==='corrupt-network'&&++requests===1?'bad':(mode==='corrupt-network'?'good':(requests++,'good')),{status:200});
  const audio=new PrayerAudio({Context:class {},storage:null,getSettings:()=>({}),onState(){}});audio.ctx={decodeAudioData:async bytes=>{decodes++;const value=new TextDecoder().decode(bytes);if(value==='bad')throw Error('EncodingError');return {value};}};
  if(mode==='corrupt-network'){await assert.rejects(audio.load('audio/test'));assert.equal(data.size,0,'Do not cache invalid network audio');}
  assert.deepEqual(await audio.load('audio/test'),{value:'good'},mode);const previous=requests;await audio.load('audio/test');assert.equal(requests,previous,'Decoded buffers must remain reusable');
  if(mode==='corrupt-cache')assert.equal(await data.get('audio/test').text(),'good');
 }
 console.log('PASS: corrupt cache evicted/replaced; invalid network audio not cached; quota/privacy failure cannot block decoded playback.');
}finally{delete global.fetch;delete global.caches;}})().catch(e=>{console.error(e);process.exitCode=1});
