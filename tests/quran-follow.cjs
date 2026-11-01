const assert=require('node:assert/strict'),fs=require('node:fs'),Module=require('node:module'),esbuild=require('esbuild');
function load(file){const m=new Module(file,module);m._compile(esbuild.buildSync({entryPoints:[file],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,file);return m.exports;}
const {QuranFollow}=load('quran-follow.js'),{PageRecitation}=load('quran-page-audio.js'),{QuranReader,QURAN_RECITERS}=load('quran-controller.js');
class Player extends EventTarget{
 constructor({deferred=false}={}){super();this.src='';this.paused=true;this.deferred=deferred;this.starts=[];this.playCalls=0;}
 getAttribute(){return this.src||null;}removeAttribute(){this.src='';}load(){}pause(){this.paused=true;}
 play(){this.playCalls++;if(this.deferred)return new Promise((resolve,reject)=>this.starts.push({resolve:()=>{this.paused=false;resolve();},reject}));this.paused=false;return Promise.resolve();}
 end(){this.dispatchEvent(new Event('ended'));}
}
const element=()=>{const classes=new Set(),attributes=new Map();return {classes,attributes,classList:{add:v=>classes.add(v),remove:v=>classes.delete(v)},setAttribute:(k,v)=>attributes.set(k,v),removeAttribute:k=>attributes.delete(k)};};
const tick=()=>Promise.resolve();
(async()=>{
 // A highlight follows actual playback, including delayed starts, cancellation and errors.
 const player=new Player({deferred:true}),cues=[],errors=[],preloads=[];let stops=0,completed=0;
 const audio=new PageRecitation({player,onVerse:(v,c)=>cues.push({v,c}),onStop:()=>stops++,onComplete:()=>completed++,onError:e=>errors.push(e),createPreloader:()=>{const p=new Player();preloads.push(p);return p;}});
 const qatami=QURAN_RECITERS.find(r=>r.id==='qatami'),verses=[{s:2,a:1},{s:2,a:2}];
 await audio.play(qatami,verses);assert.equal(cues.length,0,'Buffering must not announce an unplayed verse');
 assert(player.src.endsWith('/002001.mp3'));
 player.starts.shift().resolve();await tick();assert.equal(cues.at(-1).v,verses[0]);
 assert.equal(preloads.at(-1).playCalls,0,'Prefetch must never start audible playback');assert(preloads.at(-1).src.endsWith('/002002.mp3'));
 player.dispatchEvent(new Event('playing'));assert.equal(cues.length,1,'Repeated playing events must not scroll repeatedly');
 player.pause();assert.equal(cues.at(-1).v,verses[0],'Pause retains the current verse');
 player.end();player.starts.shift().resolve();await tick();assert.equal(cues.at(-1).v,verses[1]);
 player.end();assert.equal(completed,1);assert(!audio.active);assert.equal(preloads.at(-1).src,'','Completion releases the prefetch source');
 await audio.play(qatami,[{s:1,a:1}]);assert.equal(audio.queue.length,1);
 const stale=player.starts.shift();audio.stop();const cueCount=cues.length;stale.resolve();await tick();assert.equal(cues.length,cueCount,'A stopped play promise must not restore the indicator');assert.equal(player.src,'');
 await audio.play(qatami,[{s:9,a:1}]);assert.equal(audio.queue.length,1);
 const old=player.starts.shift();await audio.play(QURAN_RECITERS[0],[{s:114,a:1}]);const newer=player.starts.shift();old.resolve();await tick();assert.equal(cues.length,cueCount,'Changing reciter cancels the old cue');newer.reject(new Error('blocked'));await tick();await tick();assert.equal(errors.at(-1),'play');assert(!audio.active);assert(stops>0);
 for(const reciter of QURAN_RECITERS.filter(r=>!r.fullSurahOnly)){const p=new Player(),seen=[];const a=new PageRecitation({player:p,onVerse:v=>seen.push(v),onComplete:()=>{},onError:e=>{throw Error(e);}});await a.play(reciter,[{s:114,a:1},{s:114,a:2}]);await tick();assert.equal(seen.at(-1).a,1);p.end();await tick();assert.equal(seen.at(-1).a,2);a.stop();}
 // Exactly one verse is current; disabling follow stops movement, not highlighting.
 const nodes=new Map([['2:1',element()],['2:2',element()]]),scrolled=[],rendered=[];let allowed=true,ensured=0;
 const follow=new QuranFollow({find:v=>nodes.get(v.s+':'+v.a),ensure:v=>{ensured++;const el=element();nodes.set(v.s+':'+v.a,el);return el;},scroll:el=>scrolled.push(el),render:(v,c)=>rendered.push({v,c}),canScroll:()=>allowed});
 follow.show(verses[0]);assert(nodes.get('2:1').classes.has('is-reciting'));assert.equal(nodes.get('2:1').attributes.get('aria-current'),'true');assert.equal(scrolled.length,1);
 follow.show(verses[0]);follow.refresh();assert.equal(scrolled.length,1);
 follow.show(verses[1]);assert(!nodes.get('2:1').classes.has('is-reciting'));assert(!nodes.get('2:1').attributes.has('aria-current'));assert.equal(scrolled.length,2);
 follow.setEnabled(false);follow.show({s:2,a:3});assert.equal(ensured,0);assert.equal(scrolled.length,2);assert.equal(rendered.at(-1).v.a,3);
 follow.setEnabled(true);assert.equal(ensured,1);assert.equal(scrolled.length,3);assert(nodes.get('2:3').classes.has('is-reciting'));
 allowed=false;follow.show({s:2,a:4});assert.equal(ensured,1);assert.equal(scrolled.length,3,'No scrolling behind a dialog or hidden tab');
 allowed=true;follow.refresh(true);assert.equal(ensured,2);assert.equal(scrolled.length,4);
 const replacement=element();nodes.set('2:4',replacement);follow.refresh();assert(replacement.classes.has('is-reciting'),'Font/layout rerenders restore the current highlight');assert.equal(scrolled.length,4);
 follow.show(null,{intro:true,surah:3});assert(!replacement.classes.has('is-reciting'));assert.equal(rendered.at(-1).c.intro,true);follow.clear();assert.equal(rendered.at(-1).c,null);
 // Tracking can render the next Mushaf page or return to an earlier page without touching audio.
 const data=JSON.parse(fs.readFileSync('dist/quran/data.json')),reader=Object.create(QuranReader.prototype),dom=new Map();
 global.document={getElementById:id=>{if(!dom.has(id))dom.set(id,{});return dom.get(id);}};
 dom.set('qVerses',{querySelector:()=>element()});reader.data=data;reader.surahVerses=QURAN_RECITERS[0].surahs.map(id=>data.pages.flat().filter(v=>v.s===id));reader.versePages=new Map();data.pages.forEach((p,i)=>p.forEach(v=>reader.versePages.set(v.s+':'+v.a,i+1)));
 let appended=0,rerenders=0;reader.getLang=()=>'ar';reader.page=1;reader.readingStart=1;reader.readingNext=1;reader.save=()=>{};reader.appendReadingPage=()=>{reader.readingNext++;appended++;};reader.renderReadingPages=()=>rerenders++;reader.stop=()=>{throw Error('Verse tracking must not stop recitation');};reader.play=()=>{throw Error('Verse tracking must not restart recitation');};
 reader.ensurePlayingVerse(data.pages[1][0]);assert.equal(appended,1);assert.equal(rerenders,0);
 reader.readingStart=100;reader.readingNext=100;reader.page=100;reader.ensurePlayingVerse(data.pages[1][0]);assert.equal(reader.page,2);assert.equal(rerenders,1);
 reader.ensurePlayingVerse(data.pages[603][0]);assert.equal(reader.page,604);assert.equal(rerenders,2);
 // Construct every page and verify all words, verse order and source dataset; omit ONLY display-only black circular zero marks.
 const {Node,makeDocument}=require('./quran-dom.cjs'),document=makeDocument();global.document=document;global.NodeFilter={SHOW_TEXT:4};
 const complete=Object.create(QuranReader.prototype);complete.data=data;complete.getLang=()=>'ar';
 const renderedKeys=[];for(let index=0;index<604;index++){
  const page=complete.makeReadingPage(index),nodes=page.querySelectorAll('[data-ayah]');
  assert.equal(Number(page.dataset.readingPage),index+1);assert.equal(nodes.length,data.pages[index].length);
  for(let offset=0;offset<nodes.length;offset++){
   const node=nodes[offset],verse=data.pages[index][offset];assert.equal(node.dataset.ayah,verse.s+':'+verse.a);
   const text=node.childNodes.filter(child=>!child.classList?.contains('ayah-number')).map(child=>child.textContent).join('').trimEnd();
   assert.equal(text,verse.t.replace(/[\u06DD\u06DE\u06DF\u06E0]/gu,''),'Only font-dependent black glyphs are hidden in rendered copy '+node.dataset.ayah);assert.equal(data.pages[index][offset].t,verse.t,'Underlying licensed verse unchanged');assert.equal(node.tabIndex,0);renderedKeys.push(node.dataset.ayah);
  }
 }
 assert.equal(renderedKeys.length,6236);assert.equal(new Set(renderedKeys).size,6236);
 // Lazy loading includes every page once and stops cleanly at the final page.
 global.IntersectionObserver=class{observe(){}unobserve(){}disconnect(){}};global.requestAnimationFrame=callback=>callback();
 complete.page=1;complete.size=26;complete.renderReadingPages();for(let page=2;page<=604;page++)complete.appendReadingPage();complete.appendReadingPage();
 assert.deepEqual(document.getElementById('qVerses').querySelectorAll('[data-reading-page]').map(page=>Number(page.dataset.readingPage)),Array.from({length:604},(_,i)=>i+1));
 assert.equal(document.getElementById('qVerses').querySelectorAll('[data-ayah]').length,6236);
 // A manual reading position must be saved without replacing pages or touching the player.
 const container=document.getElementById('qVerses'),visiblePage=container.children.find(node=>Number(node.dataset.readingPage)===300);
 visiblePage.bounds={top:-20,bottom:700};const visibleVerse=visiblePage.querySelector('[data-ayah]');visibleVerse.bounds={top:100,bottom:220};
 complete.surahVerses=reader.surahVerses;complete.versePages=reader.versePages;complete.bookmark=1;complete.activeSurah=2;complete.save=()=>{complete.savedPage=complete.page;};complete.stop=()=>{throw Error('Manual scrolling must not stop recitation');};complete.play=()=>{throw Error('Manual scrolling must not play recitation');};
 global.window={innerHeight:800};complete.captureReadingPosition();assert.equal(complete.page,300);assert.equal(complete.savedPage,300);assert.equal(complete.activeSurah,2,'Reading position does not change the selected audio queue');assert.equal(container.querySelectorAll('[data-reading-page]').length,604);
 assert.equal(document.getElementById('qPageNumber').value,300);assert.equal(document.getElementById('qJuz').value,String(data.pages[299][0].j));assert(!document.getElementById('qBookmark').textContent.includes('✓'),'Bookmark state follows the visible page');
 document.getElementById('mushaf').hidden=true;visiblePage.bounds={top:900,bottom:1500};complete.captureReadingPosition();assert.equal(complete.page,300,'A hidden Mushaf does not change the saved reading position');document.getElementById('mushaf').hidden=false;
 // A layout/language refresh while browsing must retain the surah actually playing.
 global.Option=class extends Node{constructor(label,value){super(1,'option');this.textContent=label;this.value=String(value);}};
 for(const id of ['qRepeat','qAutoNext']){const label=new Node(1,'label');label.append(document.getElementById(id),new Node(1,'span'));}
 complete.reciters=QURAN_RECITERS;complete.reciter=QURAN_RECITERS[0];complete.pageAudio={active:true};
 const firstRendered=container.children[0],currentRendered=visiblePage;
 complete.refresh();assert(container.children[0]===firstRendered,'Calendar/theme refresh must retain the existing Quran page stack');assert(container.children.includes(currentRendered));
 complete.resize(2);assert(container.children[0]===firstRendered,'Font sizing must resize existing verse nodes without replacing the reading stack');
 assert.equal(complete.activeSurah,2);assert.equal(document.getElementById('qSurah').value,'2');
 complete.pageAudio.active=false;complete.refresh();assert.equal(complete.activeSurah,data.pages[299][0].s,'After playback ends, controls can follow the visible surah');
 const jumped=Object.create(QuranReader.prototype);jumped.data=data;jumped.page=1;jumped.size=26;jumped.renderReadingPages();const staleAppend=jumped.appendReadingPage;
 jumped.page=42;jumped.renderReadingPages();assert.equal(Number(container.children[0].dataset.readingPage),42);
 assert.doesNotThrow(staleAppend,'A queued callback from the old page stack must be ignored');assert.equal(container.querySelectorAll('[data-reading-page]').length,1);
 // Exact verse links share the pending data request, handle failures, and never autoplay.
 const linked=Object.create(QuranReader.prototype);let releaseLoad,loads=0,stopped=0;linked.follow={refresh:()=>{}};linked.getLang=()=>'ar';linked.page=1;linked.reciter=QURAN_RECITERS[0];linked.refresh=()=>{};
 const originalFetch=global.fetch;global.fetch=()=>{loads++;return new Promise(resolve=>{releaseLoad=()=>resolve({ok:true,json:async()=>data});});};
 linked.stop=()=>{stopped++;};linked.go=(page,surah)=>{linked.page=page;linked.activeSurah=surah;container.replaceChildren(linked.makeReadingPage(page-1));};linked.play=()=>{throw Error('Opening a verse must not play audio');};
 global.matchMedia=()=>({matches:true});const pending=linked.open(),exact=linked.openVerse(2,255);assert.equal(loads,1);releaseLoad();assert.equal(await pending,true);assert.equal(await exact,true);assert.equal(linked.page,42);assert.equal(linked.activeSurah,2);assert.equal(stopped,1);
 const target=container.querySelector('[data-ayah="2:255"]');assert.equal(target.scrolled,1);assert(target.focused);assert.equal(target.closest('.quran-reading-page').style.contentVisibility,'visible');
 for(const pair of [[0,1],[115,1],[2,0],[2,287],[2.5,1],[2,'255']])assert.equal(await linked.openVerse(...pair),false);assert.equal(stopped,1,'Invalid references do not disturb recitation');
 const failed=Object.create(QuranReader.prototype);failed.getLang=()=>'ar';global.fetch=async()=>{throw Error('network');};assert.equal(await failed.openVerse(2,255),false);assert.equal(failed.opening,null,'A failed load can be retried');assert.equal(failed.loading,false);assert.equal(document.getElementById('qRetry').hidden,false);
 failed.page=1;failed.reciter=QURAN_RECITERS[0];failed.refresh=()=>{};global.fetch=async()=>({ok:true,json:async()=>data});assert.equal(await failed.open(),true);assert.equal(failed.versePages.get('114:6'),604);global.fetch=originalFetch;
 delete global.window;delete global.matchMedia;delete global.NodeFilter;delete global.IntersectionObserver;delete global.requestAnimationFrame;delete global.Option;
 delete global.document;
 const html=fs.readFileSync('dist/index.html','utf8');assert(html.includes('id="qFollowBar"'));assert(!html.includes('id="qDownloadSurah"'));assert(!html.includes('id="qDownloadConfirm"'));
 console.log('Quran following: audio-start cues, cancellation, follow/dialog safety, all 604 rendered pages without changed text, lazy loading, saved scroll position and concurrent exact-verse navigation pass.');
})().catch(error=>{console.error(error);process.exitCode=1;});
