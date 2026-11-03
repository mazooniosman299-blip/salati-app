const assert=require('node:assert/strict'),fs=require('node:fs'),Module=require('node:module'),esbuild=require('esbuild');
function load(file){const m=new Module(file,module);m._compile(esbuild.buildSync({entryPoints:[file],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,file);return m.exports;}
const {PageRecitation}=load('quran-page-audio.js'),{QURAN_RECITERS}=load('quran-controller.js');
class Player extends EventTarget{constructor(){super();this.src='';this.paused=true;this.currentTime=0;this.duration=900;this.readyState=1;}getAttribute(){return this.src||null}removeAttribute(){this.src=''}load(){this.dispatchEvent(new Event('loadedmetadata'))}pause(){this.paused=true}play(){this.paused=false;return Promise.resolve()}}
(async()=>{const previous=global.fetch;global.fetch=async url=>({ok:true,json:async()=>JSON.parse(fs.readFileSync('dist/'+url))});try{
 const data=JSON.parse(fs.readFileSync('dist/quran/data.json')),rows=data.pages.flat().filter(v=>v.s===67),reciter=QURAN_RECITERS.find(r=>r.id==='afasy');
 const p=new Player(),heard=[],errors=[],engine=new PageRecitation({player:p,onComplete:()=>{},onVerse:v=>heard.push(v),onError:e=>errors.push(e),createPreloader:()=>null});
 await engine.play(reciter,rows,{surah:67,startAyah:27});
 assert.equal(engine.queue.length,1);assert(engine.queue[0].continuous);assert.equal(engine.queue[0].start,undefined,'Initial cue is not a clipping boundary');
 assert.equal(p.currentTime,384.234,'Selection must start at the exact full-surah cue');assert.equal(p.duration,900);const source=p.src;
 p.currentTime=402;p.dispatchEvent(new Event('timeupdate'));assert.equal(heard.at(-1).a,28);assert.equal(p.src,source);assert(!p.paused);
 p.currentTime=0;p.dispatchEvent(new Event('timeupdate'));assert.equal(p.currentTime,0,'Full-surah seek must still reach its beginning');
 await engine.play(reciter,rows,{surah:67,startAyah:999});assert.equal(errors.at(-1),'unsupported');assert.equal(p.src,'');
 const native=new Player();native.nativeQuran=true;native.state={};native.stopQueue=()=>{native.queue=[]};native.playQueue=(queue,options)=>{native.queue=queue;native.options=options};
 const n=new PageRecitation({player:native,onComplete:()=>{},onVerse:()=>{},onError:e=>{throw Error(e)}});await n.play(reciter,rows,{surah:67,startAyah:27,surahNames:data.surahs.map(s=>s.name)});
 assert.equal(native.queue[0].initialPosition,384.234);assert.equal(native.queue[0].start,undefined);assert(native.queue[0].continuous);assert.equal(native.queue[0].verse,null);
 const sourceController=fs.readFileSync('quran-controller.js','utf8');assert(!sourceController.includes("id:'verseReciterMenu'"),'Direct selection must not open the old popup');
 console.log('PASS direct ayah: full-source exact cue, full duration/unclipped seek, continuous next ayah, invalid cue rejected, native initial position and no popup');
}finally{global.fetch=previous}})().catch(e=>{console.error(e);process.exitCode=1});
