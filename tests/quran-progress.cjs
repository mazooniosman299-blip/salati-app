const assert=require('node:assert/strict'),fs=require('node:fs'),Module=require('node:module'),esbuild=require('esbuild');
function load(file){const m=new Module(file,module);m._compile(esbuild.buildSync({entryPoints:[file],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,file);return m.exports;}
const {PageRecitation}=load('quran-page-audio.js'),{QuranReader,QURAN_RECITERS}=load('quran-controller.js');
class Player extends EventTarget{
 constructor(){super();this.src='';this.paused=true;this.currentTime=0;this.duration=NaN;this.loads=0;}
 getAttribute(){return this.src||null;}removeAttribute(){this.src='';}load(){this.loads++;this.currentTime=0;this.duration=NaN;}
 pause(){this.paused=true;}play(){this.paused=false;return Promise.resolve();}
 at(seconds){this.currentTime=seconds;this.dispatchEvent(new Event('timeupdate'));}
}
const previous={fetch:global.fetch,document:global.document};
(async()=>{try{
 global.fetch=async url=>({ok:true,json:async()=>JSON.parse(fs.readFileSync('dist/'+url))});
 const player=new Player(),seen=[],errors=[];let completed=0;
 const engine=new PageRecitation({player,onVerse:v=>seen.push(v),onError:e=>errors.push(e),onComplete:()=>completed++});
 const nodes=new Map(),node=()=>({value:0,style:{setProperty(){}},setAttribute(k,v){this[k]=v;}});
 global.document={getElementById:id=>{if(!nodes.has(id))nodes.set(id,node());return nodes.get(id);}};
 const reader=Object.create(QuranReader.prototype);Object.assign(reader,{player,pageAudio:engine,getLang:()=> 'ar'});reader.setupPlayer();
 const verses=require('../dist/quran/data.json').pages.flat().filter(v=>v.s===2);
 await engine.play(QURAN_RECITERS[0],verses,{surah:2});assert.equal(nodes.get('qDuration').textContent,'—:—');assert(nodes.get('qSeek').disabled);
 const track=engine.queue[0],duration=track.cues.at(-1)[2]/1000+1;player.duration=duration;player.dispatchEvent(new Event('loadedmetadata'));const label=nodes.get('qDuration').textContent,loads=player.loads,src=player.src;
 assert(duration>3600,'Al-Baqarah must use its complete recording');assert(label.split(':').length===3);assert(!nodes.get('qSeek').disabled);
 const first=track.cues[0],second=track.cues[1];player.at((first[1]+10)/1000);assert.equal(seen.at(-1).a,1);const before=Number(nodes.get('qSeek').value);
 player.at((second[1]+10)/1000);assert.equal(seen.at(-1).a,2);assert(Number(nodes.get('qSeek').value)>before);assert.equal(nodes.get('qDuration').textContent,label);assert.equal(player.loads,loads);assert.equal(player.src,src);
 const target=track.cues.find(c=>c[0]===255),time=(target[1]+10)/1000;nodes.get('qSeek').value=time/duration*100;nodes.get('qSeek').oninput();player.dispatchEvent(new Event('seeked'));assert.equal(seen.at(-1).a,255);assert(Math.abs(player.currentTime-time)<.001);assert.equal(nodes.get('qDuration').textContent,label);
 nodes.get('qSeek').value=second[1]/1000/duration*100;nodes.get('qSeek').oninput();player.at((second[1]+10)/1000);assert.equal(seen.at(-1).a,2,'Backward seek must follow the actual new verse');
 const gap=track.cues.findIndex((r,i)=>i&&r[1]>track.cues[i-1][2]);player.at((track.cues[gap-1][2]+1)/1000);assert.equal(seen.at(-1),null,'Do not invent a verse during an unaligned gap');
 player.pause();const count=seen.length;player.at(time);assert.equal(seen.length,count);await player.play();player.dispatchEvent(new Event('playing'));assert.equal(seen.at(-1).a,255);assert.equal(completed,0,'Verse boundaries must never end a full-surah recording');
 engine.stop();player.at(time);assert.equal(seen.at(-1).a,255);assert(!engine.active);
 // A slow timing fetch cannot start audio after Stop or replace a newer reader.
 let deliver;global.fetch=()=>new Promise(resolve=>deliver=resolve);const delayed=new PageRecitation({player:new Player(),onVerse:()=>{},onError:e=>errors.push(e),onComplete:()=>{}});
 const pending=delayed.play(QURAN_RECITERS[0],verses,{surah:2});delayed.stop();deliver({ok:true,json:async()=>JSON.parse(fs.readFileSync('dist/quran/timings/shatri.json'))});await pending;assert.equal(delayed.player.src,'');assert(!delayed.active);
 global.fetch=async()=>({ok:false});await delayed.play(QURAN_RECITERS[4],verses,{surah:2});assert.equal(errors.at(-1),'network');assert.equal(delayed.player.src,'','Missing timings must not silently restore fragmented surah playback');
 console.log('PASS: full-surah duration, cumulative elapsed/seek across ayahs, forward/backward seek, exact cues/repeats, gap/pause/stop safety, no per-verse reload or completion, metadata races and failures.');
}finally{Object.assign(global,previous);}})().catch(e=>{console.error(e);process.exitCode=1;});
