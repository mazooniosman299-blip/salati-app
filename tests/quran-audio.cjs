const assert=require('node:assert/strict');
const Module=require('node:module');
const esbuild=require('esbuild');
function load(file){const m=new Module(file,module);m._compile(esbuild.buildSync({entryPoints:[file],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,file);return m.exports;}
const {QURAN_RECITERS,recitationUrl}=load('quran-controller.js');
const {PageRecitation}=load('quran-page-audio.js');
class Player extends EventTarget{
 constructor(){super();this.src='';this.paused=true;this.loop=false;this.currentTime=0;}
 getAttribute(name){return name==='src'?(this.src||null):null;}
 removeAttribute(name){if(name==='src')this.src='';}
 load(){}
 play(){this.paused=false;return Promise.resolve();}
 pause(){this.paused=true;}
 end(){this.dispatchEvent(new Event('ended'));}
}
(async()=>{
 const qatami=QURAN_RECITERS.find(r=>r.id==='qatami');
 assert(qatami,'Nasser Al-Qatami must be selectable in both reciter pickers');
 assert.equal(qatami.ar,'ناصر القطامي');
 assert.equal(new Set(qatami.surahs).size,114);
 for(const [id,name,server]of [['afasy','مشاري العفاسي','https://server8.mp3quran.net/afs/']]){const reader=QURAN_RECITERS.find(r=>r.id===id);assert(reader);assert(reader.ar.startsWith(name));assert.equal(reader.server,server);assert.deepEqual(reader.surahs,Array.from({length:114},(_,i)=>i+1));for(let surah=1;surah<=114;surah++)assert.equal(recitationUrl(reader,surah),server+String(surah).padStart(3,'0')+'.mp3');}
 const player=new Player(),errors=[],verses=[];let completed=0;
 const audio=new PageRecitation({player,onError:error=>errors.push(error),onVerse:v=>verses.push(v),onComplete:()=>completed++});
 for(const surah of [1,2,18,36,55,114]){
  audio.playSurah(qatami,surah);
  assert.equal(player.src,'https://server6.mp3quran.net/qtm/'+String(surah).padStart(3,'0')+'.mp3');
  assert.equal(player.src,recitationUrl(qatami,surah));
  assert(audio.active);player.end();assert(!audio.active);
 }
 assert.equal(completed,6);
 const oldFetch=global.fetch;
 global.fetch=()=>{throw Error('Qatami verse playback must use verified EveryAyah files without timing lookup');};
 try{
  const page=[{s:1,a:7},{s:2,a:1}];
  await audio.play(qatami,page);
  assert.equal(player.src,'https://everyayah.com/data/Nasser_Alqatami_128kbps/001007.mp3');
  assert.equal(verses.at(-1),page[0]);player.end();await Promise.resolve();
  assert.equal(player.src,'https://everyayah.com/data/Nasser_Alqatami_128kbps/002001.mp3');
  assert.equal(verses.at(-1),page[1]);player.end();assert.equal(completed,7);
  await audio.play(qatami,[{s:114,a:6}]);
  assert.equal(player.src,'https://everyayah.com/data/Nasser_Alqatami_128kbps/114006.mp3');
  audio.stop();player.end();assert.equal(player.src,'');assert.equal(completed,7);
 }finally{global.fetch=oldFetch;}
 audio.playSurah(qatami,2);
 audio.playSurah(QURAN_RECITERS.find(r=>r.id==='shatri'),2);
 assert.equal(player.src,'https://server11.mp3quran.net/shatri/002.mp3');
 audio.playSurah(QURAN_RECITERS.find(r=>r.id==='yasser'),2);
 assert.equal(player.src,'https://server11.mp3quran.net/yasser/002.mp3');
 assert.equal(errors.length,0);
 assert.equal(recitationUrl(qatami,115),null);
 audio.playSurah(qatami,115);assert.deepEqual(errors,['unsupported']);assert(!audio.active);
 // Main playback uses one exact recording per surah; individual ayahs retain verified EveryAyah routes.
 const data=require('../dist/quran/data.json'),all=data.pages.flat();
 global.fetch=async url=>({ok:true,json:async()=>require('../dist/'+url)});
 try{for(const reciter of QURAN_RECITERS.filter(r=>!r.fullSurahOnly)){
  const p=new Player(),heard=[];let done=0;
  const full=new PageRecitation({player:p,onError:error=>{throw Error(error);},onVerse:verse=>{if(verse)heard.push(verse.s+':'+verse.a);},onComplete:()=>done++,createPreloader:()=>null});
  const individual=await full.segments(reciter,all);assert.equal(individual.length,6236);
  for(let i=0;i<individual.length;i++)assert(individual[i].url.endsWith(String(all[i].s).padStart(3,'0')+String(all[i].a).padStart(3,'0')+'.mp3'));
  for(const surah of data.surahs){
   const rows=all.filter(v=>v.s===surah.id);await full.play(reciter,rows,{surah:surah.id});
   assert.equal(full.queue.length,1);const track=full.queue[0];assert(track.continuous);assert(!track.start&&!track.end);assert(!track.url.includes('everyayah.com'));assert.equal(p.src,track.url);
   assert.equal(new Set(track.cues.map(c=>c[0])).size,surah.total_verses-(surah.id===1&&['qatami','yasser'].includes(reciter.id)?1:0));
   for(const [ayah,start,end] of track.cues){p.currentTime=(start+Math.min(end-start,10))/1000;p.dispatchEvent(new Event('timeupdate'));assert.equal(heard.at(-1),surah.id+':'+ayah);assert.equal(p.src,track.url,'A verse transition must not reload audio');assert.equal(full.index,0);}
   p.end();await Promise.resolve();assert(!full.active);
  }
  assert.equal(new Set(heard).size,['qatami','yasser'].includes(reciter.id)?6235:6236);assert.equal(done,114);
 }}finally{global.fetch=oldFetch;}
 const studio=QURAN_RECITERS.find(r=>r.id==='sudais');assert(studio&&studio.fullSurahOnly);assert.equal(studio.ar,'عبدالرحمن السديس');assert.equal(QURAN_RECITERS.filter(r=>r.id.includes('sudais')).length,1);assert(!require('node:fs').readFileSync('quran-page-audio.js','utf8').includes('Abdurrahmaan_As-Sudais'));assert.equal(studio.surahs.length,114);const studioPlayer=new Player(),studioAudio=new PageRecitation({player:studioPlayer,onError:error=>{throw Error(error);},onVerse:verse=>assert.equal(verse,null),onComplete:()=>{}});for(let surah=1;surah<=114;surah++){const url=recitationUrl(studio,surah);assert(url.startsWith('https://archive.org/download/a0s0261002ddddddddddd/'));assert(decodeURIComponent(new URL(url).pathname.split('/').pop()).startsWith(String(surah).padStart(3,'0')+' - '));studioAudio.playSurah(studio,surah);assert.equal(studioPlayer.src,url);assert.equal(studioAudio.queue.length,1);assert.equal(studioAudio.queue[0].verse,null);studioAudio.stop();}
 console.log('Quran audio: 456 continuous surah recordings with matching cues (including repeats), no per-verse reload; all 24944 individual-ayah routes, stop and reciter switching pass.');
})().catch(error=>{console.error(error);process.exitCode=1;});
