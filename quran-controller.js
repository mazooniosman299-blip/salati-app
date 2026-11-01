import {quranPlayer} from './native-quran-player.js';
import {fullSurahUrl} from './quran-audio-source.js';
import studioUrls from './sudais-studio-urls.json';
import {createPopover} from './popover-menu.js';
import {QuranOffline} from './quran-offline.js';
import {QuranFollow} from './quran-follow.js';
import {PageRecitation} from './quran-page-audio.js';
const allSurahs=Array.from({length:114},(_,i)=>i+1);
export const QURAN_RECITERS=[
 {id:'shatri',ar:'أبو بكر الشاطري',en:'Abu Bakr Al-Shatri',catalogId:4,server:'https://server11.mp3quran.net/shatri/',surahs:allSurahs},
 {id:'yasser',ar:'ياسر الدوسري',en:'Yasser Al-Dosari',catalogId:92,server:'https://server11.mp3quran.net/yasser/',surahs:allSurahs},
 {id:'qatami',ar:'ناصر القطامي',en:'Nasser Al-Qatami',server:'https://server6.mp3quran.net/qtm/',surahs:allSurahs},
 {id:'sudais',ar:'عبدالرحمن السديس',en:'Abdul Rahman Al-Sudais',surahUrls:studioUrls,fullSurahOnly:true,surahs:allSurahs},
 {id:'afasy',ar:'مشاري العفاسي',en:'Mishary Al-Afasy',server:'https://server8.mp3quran.net/afs/',surahs:allSurahs},
];
export function recitationUrl(reciter,surah){return fullSurahUrl(reciter,surah)}
const $=id=>document.getElementById(id);
export class QuranReader{
 constructor({getLang,beforePlay}){this.getLang=getLang;this.beforePlay=beforePlay;this.reciters=QURAN_RECITERS.map(r=>({...r,surahs:[...r.surahs]}));let saved={};try{saved=JSON.parse(localStorage.getItem('salati-quran')||'{}')||{}}catch{}
 this.page=this.validPage(saved.page)?saved.page:1;this.activeSurah=Number.isInteger(saved.activeSurah)?saved.activeSurah:null;this.bookmark=this.validPage(saved.bookmark)?saved.bookmark:null;this.size=saved.layoutVersion===2&&Number.isFinite(saved.size)?Math.max(22,Math.min(36,saved.size)):26;this.reciter=this.reciters.find(r=>r.id===saved.reciter)||this.reciters[0];this.audioSurah=this.reciter.surahs.includes(saved.audioSurah)?saved.audioSurah:this.reciter.surahs[0];this.player=quranPlayer($('qAudio'));this.player.loop=false;$('qRepeat').checked=!!saved.repeat;$('qAutoNext').checked=!!saved.autoNext;
 if(this.player.nativeQuran&&this.player.active){this.reciter=this.reciters.find(r=>r.id===this.player.state.reciter)||this.reciter;this.activeSurah=this.audioSurah=this.player.queue[this.player.queueIndex]?.surah||this.audioSurah;$('qRepeat').checked=!!this.player.state.repeat;$('qAutoNext').checked=!!this.player.state.autoNext;}this.offline=new QuranOffline();this.followEnabled=saved.follow!==false;
 this.pageAudio=new PageRecitation({player:this.player,resolveSource:(reciter,surah,url)=>this.offline.resolve(reciter,surah,url),onComplete:()=>{if(this.versePlayback){this.versePlayback=false;this.audioMessage('انتهت تلاوة الآية.','Verse recitation finished.');return}if(this.player.nativeQuran){this.audioMessage('انتهت التلاوة.','Recitation finished.');return;}if($('qRepeat').checked)this.play();else if($('qAutoNext').checked){if(this.surahMode()){const i=this.reciter.surahs.indexOf(this.activeSurah);const id=this.reciter.surahs[i+1];if(id){this.go(this.data.surahs[id-1].page,id,true);return}}else if(this.page<604){this.go(this.page+1,undefined,true);return}this.audioMessage('انتهت التلاوة.','Recitation finished.')}else this.audioMessage(this.surahMode()?'انتهت تلاوة السورة.':'انتهت تلاوة الصفحة.',this.surahMode()?'Surah recitation finished.':'Page recitation finished.')},onStop:()=>this.follow?.clear(),onError:code=>this.audioMessage(code==='offline'?'التلاوة تحتاج اتصالًا بالإنترنت.':code==='unsupported'?'متابعة الآيات غير متاحة لهذا القارئ. اختر قارئًا آخر.':'تعذر تشغيل التلاوة. تحقق من الاتصال واضغط تشغيل.',code==='offline'?'Recitation needs an internet connection.':code==='unsupported'?'Verse tracking is unavailable for this reciter. Choose another reciter.':'Could not play recitation. Check your connection and press Play.'),onVerse:(v,cue)=>{if(!this.data)return;const id=v?.s||cue?.surah;if(id)this.audioSurah=id;if(this.player.nativeQuran&&id){this.activeSurah=id;$('qSurah').value=String(id);}if(id)this.renderTrack(id,v,this.player.nativeQuran?(this.reciters.find(r=>r.id===this.player.state.reciter)||this.reciter):(this.versePlayback?this.playingReciter:this.reciter));this.follow.show(v,cue)}});$('qPageForm').onsubmit=e=>{e.preventDefault();this.go(Number($('qPageNumber').value))};$('qSurah').onchange=()=>this.go(this.data.surahs[Number($('qSurah').value)-1].page,Number($('qSurah').value));$('qJuz').onchange=()=>this.go(this.data.pages.findIndex(p=>p.some(v=>v.j===Number($('qJuz').value)))+1);$('qSmaller').onclick=()=>this.resize(-2);$('qLarger').onclick=()=>this.resize(2);$('qBookmark').onclick=()=>{this.captureReadingPosition();this.bookmark=this.page;this.save();this.refreshBookmarkControls()};$('qResume').onclick=()=>this.go(this.bookmark);$('qRetry').onclick=()=>this.open();
 $('qReciter').onchange=()=>{this.stop();this.reciter=this.reciters.find(r=>r.id===$('qReciter').value);if(this.data&&!this.reciter.surahs.includes(this.activeSurah)){const id=this.reciter.surahs[0];this.go(this.data.surahs[id-1].page,id);this.audioMessage('السورة السابقة غير متاحة لهذا القارئ؛ فُتحت أول سورة متاحة بصوته.','The previous surah is unavailable for this reciter; the first available surah has been opened.')}this.save();this.refresh()};$('qPlay').onclick=()=>this.play();$('qStop').onclick=()=>this.stop();

 this.setupFollow();this.setupPlayer();this.setupVerseActions();this.setupReadingPosition();
 $('qRepeat').onchange=$('qAutoNext').onchange=()=>{if(!this.versePlayback)this.player.setOptions?.($('qRepeat').checked,$('qAutoNext').checked);this.save();};
 this.player.addEventListener('play',()=>{this.beforePlay();this.audioMessage('جارٍ تشغيل التلاوة…','Playing recitation…')});this.player.addEventListener('pause',()=>{if(this.player.src&&!this.player.ended&&this.pageAudio.active)this.audioMessage('التلاوة متوقفة مؤقتًا.','Recitation paused.')});this.player.addEventListener('waiting',()=>this.audioMessage('جارٍ تحميل التلاوة…','Buffering recitation…'));this.player.addEventListener('playing',()=>this.audioMessage('جارٍ تشغيل التلاوة…','Playing recitation…'));this.player.addEventListener('error',()=>this.audioMessage('تعذر تحميل التلاوة. تحقق من الإنترنت أو جرّب سورة أخرى، ثم اضغط تشغيل لإعادة المحاولة.','Could not load recitation. Check your connection or choose another surah, then press Play to retry.'));if(this.player.nativeQuran){const resume=()=>{this.player.sync();this.pageAudio.syncNative();this.follow.refresh(true);};window.addEventListener('salati-native-resume',resume);document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')resume();});}this.refresh();if(saved.reciter&&saved.reciter!==this.reciter.id)this.save();
 }
 setupFollow(){
 const canScroll=()=>document.visibilityState!=='hidden'&&!$('mushaf').hidden&&!this.verseMenuOpen&&!document.querySelector('dialog[open]');
 this.follow=new QuranFollow({enabled:this.followEnabled,canScroll,
  find:v=>$('qVerses').querySelector('[data-ayah="'+v.s+':'+v.a+'"]'),
  ensure:v=>this.ensurePlayingVerse(v),
  scroll:element=>{const [s,a]=element.dataset.ayah.split(':').map(Number);this.updateReadingPosition({s,a});element.closest('.quran-reading-page').style.contentVisibility='visible';element.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'center'});},
  render:(v,cue)=>{const bar=$('qFollowBar');bar.hidden=!v&&!cue?.intro;if(bar.hidden)return;const surah=this.data.surahs[(v?.s||cue.surah)-1];const name=this.getLang()==='ar'?surah.name:surah.transliteration;const number=n=>new Intl.NumberFormat(this.getLang()).format(n);$('qCurrentVerse').textContent=name+' · '+(v?this.tr('الآية ','Verse ')+number(v.a)+' / '+number(this.surahVerses[v.s-1].length):this.tr('البسملة','Basmala'));}
 });
 $('qFollowToggle').checked=this.followEnabled;$('qFollowToggle').onchange=()=>{this.followEnabled=$('qFollowToggle').checked;this.follow.setEnabled(this.followEnabled);this.save();};
 }
 setupReadingPosition(){
  const record=()=>{if(this.readingPositionScheduled)return;this.readingPositionScheduled=true;requestAnimationFrame(()=>{this.readingPositionScheduled=false;this.captureReadingPosition()})};
  window.addEventListener('scroll',record,{passive:true});
  document.querySelector('main')?.addEventListener('scroll',record,{passive:true});
  // The reading area now scrolls independently of the application shell.
  $('qVerses').addEventListener('scroll',record,{passive:true});
  document.addEventListener('visibilitychange',()=>{
   if(document.visibilityState==='visible'&&!$('mushaf').hidden)this.enterAtSurahStart();
  });
 }
 captureReadingPosition(){
  if(!this.data||$('mushaf').hidden||document.querySelector('dialog[open]'))return;
  const container=$('qVerses');const region=container.getBoundingClientRect();
  // For a real bounded scroller, ignore verses clipped outside its viewport.
  // The fallback preserves reading on the legacy unbounded DOM (also tests).
  const bounded=Number(container.clientHeight)>0&&region.bottom>region.top+20;
  const anchor=bounded?Math.max(region.top+12,Math.min(window.innerHeight*.3,160)):Math.min(window.innerHeight*.3,160);
  const ceiling=bounded?Math.min(region.bottom,window.innerHeight):window.innerHeight;
  const visible=element=>{const bounds=element.getBoundingClientRect();return bounds.bottom>anchor&&bounds.top<ceiling;};
  const page=[...$('qVerses').children].find(element=>element.dataset.readingPage&&visible(element));
  const verse=page&&[...page.querySelectorAll('[data-ayah]')].find(visible);if(!verse)return;
  const [s,a]=verse.dataset.ayah.split(':').map(Number);this.updateReadingPosition({s,a});
 }
 refreshBookmarkControls(){$('qResume').disabled=!this.bookmark;$('qResume').textContent=this.bookmark?this.tr('العودة للعلامة · '+this.bookmark,'Bookmark · '+this.bookmark):this.tr('العودة للعلامة','Go to bookmark');$('qBookmark').textContent=this.page===this.bookmark?this.tr('✓ العلامة محفوظة هنا','✓ Bookmarked here'):this.tr('حفظ علامة القراءة','Bookmark page');}
 updateReadingPosition(v){const page=this.versePages.get(v.s+':'+v.a);if(!page||page===this.page)return;this.page=page;$('qPageNumber').value=page;$('qPageLabel').textContent=new Intl.NumberFormat('ar').format(page);if(!this.surahMode())$('qProgress').textContent=page+' / 604';const verse=this.surahVerses[v.s-1].find(row=>row.a===v.a);$('qJuz').value=String(verse.j);$('qPageJuz').textContent='الجزء '+new Intl.NumberFormat('ar').format(verse.j);this.refreshBookmarkControls();this.save();}
 ensurePlayingVerse(v){
 const page=this.versePages.get(v.s+':'+v.a);if(!page)return null;
 if(page>=this.readingStart&&page<=this.readingNext+3){while(this.readingNext<page)this.appendReadingPage();}
 else{this.updateReadingPosition(v);this.renderReadingPages();}
 return $('qVerses').querySelector('[data-ayah="'+v.s+':'+v.a+'"]');
 }
 setupVerseActions(){
 const popup=createPopover({id:'verseReciterMenu',className:'verse-reciter-menu',label:this.tr('اختر القارئ','Choose reciter'),width:230,height:240,onClose:()=>{this.verseMenuOpen=false;}}),menu=popup.element;
 menu.setAttribute('role','menu');
 const play=async(verse,reciter)=>{popup.close(true);if(navigator.onLine===false){this.audioMessage('تشغيل الآية ومتابعتها يحتاج اتصالًا بالإنترنت.','Verse playback and tracking need an internet connection.');return;}this.stop();this.beforePlay();this.versePlayback=true;this.playingReciter=reciter;this.audioSurah=verse.s;$('qStop').disabled=false;this.renderTrack(verse.s,verse,reciter);this.audioMessage('جارٍ تحميل الآية…','Loading verse…');await this.pageAudio.play(reciter,[verse]);};
 const open=(element,event)=>{const [surah,ayah]=element.dataset.ayah.split(':').map(Number),verse=this.data?.pages.flat().find(v=>v.s===surah&&v.a===ayah);if(!verse)return;
  menu.dir=document.documentElement.dir;menu.setAttribute('aria-label',this.data.surahs[surah-1].name+' · '+ayah+' · '+this.tr('اختر القارئ','Choose reciter'));
  menu.replaceChildren(...this.reciters.filter(reciter=>!reciter.fullSurahOnly).map(reciter=>{const button=document.createElement('button');button.type='button';button.dataset.reciter=reciter.id;button.setAttribute('role','menuitemradio');button.setAttribute('aria-checked',String(reciter.id===(this.playingReciter||this.reciter).id));button.textContent=reciter[this.getLang()];button.onclick=()=>play(verse,reciter);return button;}));
  this.verseMenuOpen=true;popup.open(element,{point:event?.type==='click'&&event.detail!==0?{x:event.clientX,y:event.clientY}:undefined});
  const selected=[...menu.children].find(button=>button.dataset.reciter===(this.playingReciter||this.reciter).id)||menu.children[0];selected?.focus({preventScroll:true});selected?.scrollIntoView({block:'nearest'});
 };
 menu.onkeydown=event=>{const buttons=[...menu.children].filter(button=>!button.hidden&&!button.disabled);if(!buttons.length)return;const index=buttons.indexOf(document.activeElement);let next;if(event.key==='ArrowDown')next=(index+1)%buttons.length;else if(event.key==='ArrowUp')next=(index-1+buttons.length)%buttons.length;else if(event.key==='Home')next=0;else if(event.key==='End')next=buttons.length-1;if(next!==undefined){event.preventDefault();buttons[next].focus();}};
 $('qVerses').addEventListener('click',event=>{const selection=window.getSelection();if(selection&&!selection.isCollapsed)return;const verse=event.target.closest('[data-ayah]');if(verse)open(verse,event);});
 $('qVerses').addEventListener('keydown',event=>{if((event.key==='Enter'||event.key===' ')&&event.target.matches('[data-ayah]')){event.preventDefault();open(event.target,event);}});
 }
 setupPlayer(){
 const player=this.player;player.muted=false;player.volume=1;const seek=$('qSeek');const clock=value=>{const seconds=Math.max(0,Math.floor(value||0));return (seconds>=3600?Math.floor(seconds/3600)+':'+String(Math.floor(seconds/60)%60).padStart(2,'0'):Math.floor(seconds/60))+':'+String(seconds%60).padStart(2,'0')};
 const bounds=()=>{const segment=this.pageAudio.queue[this.pageAudio.index];return {start:segment?.start||0,end:segment?.end??player.duration}};
 const update=()=>{const {start,end}=bounds(),duration=Number.isFinite(end)?Math.max(0,end-start):0,elapsed=Math.max(0,Math.min(duration,player.currentTime-start));seek.disabled=!duration;seek.value=duration?elapsed/duration*100:0;seek.style.setProperty('--seek',seek.value+'%');$('qElapsed').textContent=clock(elapsed);$('qDuration').textContent=duration?clock(duration):'—:—';$('qTransportIcon').setAttribute('d',player.paused?'M8 5v14l11-7z':'M6 5h4v14H6zM14 5h4v14h-4z');$('qTransport').setAttribute('aria-label',player.paused?this.tr('تشغيل','Play'):this.tr('إيقاف مؤقت','Pause'));$('qFollowTransport').textContent=player.paused?this.tr('▶ تشغيل','▶ Play'):this.tr('Ⅱ إيقاف مؤقت','Ⅱ Pause');seek.setAttribute('aria-label',this.pageAudio.queue[this.pageAudio.index]?.verse?this.tr('موضع التشغيل داخل الآية','Playback position within verse'):this.tr('موضع التشغيل داخل السورة','Playback position within surah'));};
 $('qTransport').onclick=()=>{if(!player.paused){player.pause();return}if(this.pageAudio.active&&player.getAttribute('src'))player.play().catch(()=>this.audioMessage('تعذر تشغيل التلاوة. حاول مجددًا.','Could not play. Try again.'));else this.play()};
 $('qFollowTransport').onclick=()=>$('qTransport').click();
 seek.oninput=()=>{const {start,end}=bounds();if(Number.isFinite(end)&&end>start)player.currentTime=start+(end-start)*Number(seek.value)/100;update()};
 for(const event of ['timeupdate','loadedmetadata','durationchange','play','pause','emptied','ended','volumechange'])player.addEventListener(event,update);update();
 }
 continuousReading(){return true}
 goSurah(step){const id=this.activeSurah+step;if(this.data&&id>=1&&id<=114)this.go(this.data.surahs[id-1].page,id,true)}
 renderTrack(surah,verse,reader=this.reciter){const info=this.data?.surahs[surah-1];if(!info)return;const row=this.surahVerses?.[surah-1]?.[(verse?.a||1)-1];const part=row?.j||1;const arabic=this.getLang()==='ar';const partName=part===1&&arabic?'الأول':new Intl.NumberFormat(this.getLang()).format(part);$('qTrack').textContent=this.tr('سورة ','Surah ')+(arabic?info.name:info.transliteration)+' · '+this.tr('الجزء ','Juz ')+partName;$('qTrack').title=reader[this.getLang()]+(verse?' · '+this.tr('الآية ','Verse ')+verse.a:'');}
 surahMode(){return true}
 tr(ar,en){return this.getLang()==='ar'?ar:en} validPage(p){return Number.isInteger(p)&&p>=1&&p<=604}
 save(){try{localStorage.setItem('salati-quran',JSON.stringify({page:this.page,activeSurah:this.activeSurah,bookmark:this.bookmark,size:this.size,layoutVersion:2,reciter:this.reciter.id,audioSurah:this.audioSurah,repeat:$('qRepeat').checked,autoNext:$('qAutoNext').checked,follow:this.followEnabled}))}catch{}}
 async open(){if(this.data){this.follow.refresh(true);return true;}if(this.opening)return this.opening;this.opening=this.loadData();try{return await this.opening}finally{this.opening=null}}
 // A fresh entry returns to verse 1 of the selected surah, NOT to a stored
 // scroll offset or a mid-page ayah. The user's explicit bookmark remains saved.
 // Keep background native recitation alive; only reset the reading viewport.
 async enterAtSurahStart(){
  if(!await this.open())return false;
  const surah=this.data.surahs[this.activeSurah-1]||this.data.surahs[0];
  if(!surah)return false;
  this.follow?.clear();
  this.page=surah.page;
  this.readingStart=0;this.readingNext=0;
  this.save();this.refresh();
  $('qVerses').scrollTop=0;
  requestAnimationFrame(()=>requestAnimationFrame(()=>{
   if($('mushaf').hidden)return;
   const sheet=$('qSheet');
   const main=document.querySelector('main');
   const scrollContainer=matchMedia('(max-width:760px)').matches&&main?main:window;
   const top=sheet.getBoundingClientRect().top-
    (scrollContainer===window?0:main.getBoundingClientRect().top)+
    (scrollContainer===window?scrollY:main.scrollTop)-12;
   scrollContainer.scrollTo({top:Math.max(0,top),behavior:'instant'});
  }));
  return true;
 }
 async loadData(){this.loading=true;this.loadFailed=false;$('qTransport').disabled=true;$('qTrack').textContent=this.tr('جارٍ فتح المصحف…','Loading Quran…');$('qLoadStatus').textContent=this.tr('جارٍ فتح المصحف…','Loading Quran…');$('qRetry').hidden=true;try{const r=await fetch('quran/data.json');if(!r.ok)throw Error();const data=await r.json();if(data.pages?.length!==604||data.surahs?.length!==114||data.pages.some(p=>!p.length)||data.pages.flat().length!==6236)throw Error();this.data=data;this.versePages=new Map();this.surahVerses=Array.from({length:114},()=>[]);data.pages.forEach((page,index)=>page.forEach(v=>{this.versePages.set(v.s+':'+v.a,index+1);this.surahVerses[v.s-1].push(v)}));const current=data.pages[this.page-1];const selected=current.some(v=>v.s===this.activeSurah)?this.activeSurah:current[0].s;let restored=false;if(!this.reciter.surahs.includes(selected)){const id=this.reciter.surahs[0];this.page=data.surahs[id-1].page;this.activeSurah=id;restored=true;this.save()}$('qLoadStatus').textContent='';$('qSheet').setAttribute('aria-busy','false');this.refresh();this.pageAudio?.syncNative?.();if(restored)this.audioMessage('السورة المحفوظة غير متاحة بصوت هذا القارئ؛ فُتحت سورة متاحة بصوته.','The saved surah is unavailable for this reciter; an available surah has been opened.');return true}catch{this.loadFailed=true;$('qTrack').textContent=this.tr('افتح المصحف وأعد المحاولة.','Open Quran and retry.');$('qLoadStatus').textContent=this.tr('تعذر فتح المصحف. تحقق من الاتصال وأعد المحاولة.','Could not load Quran. Check your connection and retry.');$('qRetry').hidden=false;return false}finally{this.loading=false}}
 async openVerse(surah,ayah){
  if(!Number.isInteger(surah)||surah<1||surah>114||!Number.isInteger(ayah)||ayah<1||!await this.open())return false;
  const page=this.versePages.get(surah+':'+ayah);if(!page)return false;
  this.stop();this.go(page,surah);const verse=$('qVerses').querySelector('[data-ayah="'+surah+':'+ayah+'"]');if(!verse)return false;
  verse.closest('.quran-reading-page').style.contentVisibility='visible';verse.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'center'});verse.focus({preventScroll:true});return true;
 }
 go(page,surah,autoplay=false){if(!this.data||!this.validPage(page))return;const ids=this.data.pages[page-1].map(v=>v.s);const selected=ids.includes(surah)?surah:ids[0];const targetVerse=this.data.pages[page-1].find(v=>v.s===selected);const resume=autoplay||!this.player.paused;const keep=this.surahMode()&&selected===this.activeSurah&&this.pageAudio.active&&!this.player.paused&&this.pageAudio.surahKey===this.reciter.id+':'+selected;if(!keep)this.stop();this.page=page;this.activeSurah=selected;this.save();this.refresh();(this.continuousReading()?document.querySelector('[data-ayah="'+selected+':'+targetVerse.a+'"]'):$('qSheet'))?.scrollIntoView({behavior:'smooth',block:'start'});if(resume&&!keep)this.play()}
 resize(delta){this.size=Math.max(22,Math.min(36,this.size+delta));this.save();this.refresh()}
 makeReadingPage(index){
  // Remove only font-dependent decorative round-zero / verse-circle marks from
  // rendered display; the canonical licensed JSON remains byte-for-byte intact.
  const printable=text=>text.replace(/[\u06DD\u06DE\u06DF\u06E0]/gu,'');
 const verses=this.data.pages[index],page=document.createElement('section');page.className='quran-reading-page';page.dataset.readingPage=index+1;
 
 const fragment=document.createDocumentFragment();let paragraph;for(const original of verses){const v={...original,t:printable(original.t)};if(!paragraph||v.a===1){if(v.a===1){const h=document.createElement('h3');h.className='quran-surah-title';h.textContent='سورة '+this.data.surahs[v.s-1].name;fragment.append(h)}paragraph=document.createElement('p');paragraph.className='quran-text';fragment.append(paragraph)}const span=document.createElement('span');span.dataset.ayah=v.s+':'+v.a;span.tabIndex=0;span.setAttribute('aria-label','الآية '+v.a+'، استماع');const basmala=v.t.split(' ').slice(0,4).join(' ');if(v.a===1&&v.s!==9&&v.t.startsWith(basmala)){if(v.s===1){span.classList.add('quran-basmala');span.textContent=v.t+' '}else{const opening=document.createElement('span');opening.className='quran-basmala';opening.textContent=basmala;span.append(opening,document.createTextNode(v.t.slice(basmala.length)+' '))}}else span.textContent=v.t+' ';const mark=document.createElement('span');mark.className='ayah-number';mark.textContent='﴿'+new Intl.NumberFormat('ar').format(v.a)+'﴾';mark.setAttribute('aria-label','الآية '+v.a);span.append(mark,document.createTextNode(' '));paragraph.append(span)}page.append(fragment);const walker=document.createTreeWalker(page,NodeFilter.SHOW_TEXT);const affected=[];while(walker.nextNode())if(/[\u06df\u06e0]/u.test(walker.currentNode.textContent))affected.push(walker.currentNode);for(const node of affected){const replacement=document.createDocumentFragment();for(const token of node.textContent.split(/(\s+)/u)){if(/[\u06df\u06e0]/u.test(token)){const word=document.createElement('span');word.className='quran-compatible-mark';word.textContent=token;replacement.append(word)}else replacement.append(document.createTextNode(token))}node.replaceWith(replacement)}
 const number=document.createElement('div');number.className='reading-page-number';number.textContent=new Intl.NumberFormat('ar').format(index+1);page.append(number);return page;
 }
 renderReadingPages(){
 if(this.page>=this.readingStart&&this.page<=this.readingNext)return;this.readingObserver?.disconnect();const container=$('qVerses');container.replaceChildren();$('qSheet').classList.add('continuous-sheet');this.readingStart=this.page;this.readingNext=this.page-1;const sentinel=document.createElement('div');sentinel.className='reading-page-sentinel';sentinel.setAttribute('aria-hidden','true');
 const append=this.appendReadingPage=()=>{if(!sentinel.isConnected)return;if(this.readingNext>=604){this.readingObserver?.disconnect();sentinel.remove();return}const page=this.makeReadingPage(this.readingNext++);container.insertBefore(page,sentinel);page.style.contentVisibility='auto';page.style.containIntrinsicSize='auto 900px';};
 container.append(sentinel);append();this.readingObserver=new IntersectionObserver(entries=>{if(entries.some(e=>e.isIntersecting)){append();this.readingObserver.unobserve(sentinel);requestAnimationFrame(()=>{if(sentinel.isConnected)this.readingObserver.observe(sentinel)})}},{rootMargin:'600px 0px'});this.readingObserver.observe(sentinel);
 }
 refresh(){const name=s=>this.getLang()==='ar'?s.name:s.transliteration;const select=(id,options,value)=>{const el=$(id);el.replaceChildren(...options.map(([val,label])=>new Option(label,val)));el.value=String(value)};
 select('qReciter',this.reciters.map(r=>[r.id,r[this.getLang()]]),this.reciter.id);$('qFollowToggle').checked=this.followEnabled&&!this.reciter.fullSurahOnly;$('qFollowToggle').disabled=!!this.reciter.fullSurahOnly;const followLabel=$('qFollowToggle').parentElement?.querySelector('span');if(followLabel)followLabel.textContent=this.reciter.fullSurahOnly?this.tr('هذه النسخة تعمل بالسورة كاملة','This edition plays complete surahs'):this.tr('متابعة الآية','Follow verse');this.refreshBookmarkControls();$('qSmaller').disabled=this.size<=22;$('qLarger').disabled=this.size>=36;$('qVerses').style.fontSize=this.size+'px';
 $('qTransport').disabled=!this.data;if(!this.data){$('qTrack').textContent=this.loadFailed?this.tr('افتح المصحف وأعد المحاولة.','Open Quran and retry.'):this.tr('جارٍ فتح المصحف…','Loading Quran…');return;}const pageVerses=this.data.pages[this.page-1];if(!pageVerses.some(v=>v.s===this.activeSurah)&&!this.pageAudio.active&&!this.pageAudio.loading)this.activeSurah=pageVerses[0].s;const continuous=this.continuousReading(),verses=pageVerses,first=pageVerses.find(v=>v.s===this.activeSurah)||pageVerses[0];const audible=this.pageAudio.active||this.pageAudio.loading;const currentClip=audible?this.pageAudio.queue?.[this.pageAudio.index]:null;this.audioSurah=audible?(currentClip?.surah||currentClip?.verse?.s||this.follow?.current?.verse?.s||this.audioSurah||this.activeSurah):this.activeSurah;$('qPageNumber').value=this.page;select('qSurah',this.data.surahs.map(s=>[s.id,s.id+' · '+name(s)]),this.activeSurah);select('qJuz',Array.from({length:30},(_,i)=>[i+1,this.tr('الجزء ','Juz ')+(i+1)]),first.j);$('qSurah').disabled=$('qJuz').disabled=false;const ids=continuous?[this.activeSurah]:[...new Set(verses.map(v=>v.s))];$('qPageSurah').textContent=ids.map(id=>this.data.surahs[id-1].name).join(' · ');$('qPageJuz').textContent='الجزء '+new Intl.NumberFormat('ar').format(first.j);$('qPageLabel').textContent=new Intl.NumberFormat('ar').format(this.page);$('qProgress').textContent=this.page+' / 604';$('qPageForm').hidden=continuous;$('qPageLabel').hidden=continuous;if(continuous){$('qProgress').textContent=this.activeSurah+' / 114';}
 this.renderReadingPages();this.follow?.refresh();
 const available=this.reciter.surahs.includes(this.audioSurah);$('qPlay').disabled=!available;$('qCoverage').textContent=this.reciter.surahs.length===114?this.tr('جميع السور متاحة بصوت هذا القارئ.','All surahs available for this reciter.'):this.tr('السور المتاحة بصوت هذا القارئ: '+this.reciter.surahs.length+'؛ اختر منها في القائمة.','Available surahs for this reciter: '+this.reciter.surahs.length+'. Choose from the list.');$('qCoverage').hidden=this.surahMode();if(this.surahMode())$('qCoverage').textContent='';$('qRepeat').parentElement.querySelector('span').textContent=this.surahMode()?this.tr('تكرار السورة','Repeat surah'):this.tr('تكرار الصفحة','Repeat page');$('qAutoNext').parentElement.querySelector('span').textContent=this.surahMode()?this.tr('السورة التالية تلقائيًا','Auto-play next surah'):this.tr('الصفحة التالية تلقائيًا','Auto-play next page');if(available){const currentVerse=audible?(this.follow?.current?.verse?.s===this.audioSurah?this.follow.current.verse:currentClip?.verse):undefined;const currentReader=audible?(this.player?.nativeQuran?(this.reciters.find(r=>r.id===this.player.state.reciter)||this.reciter):(this.playingReciter||this.reciter)):this.reciter;this.renderTrack(this.audioSurah,currentVerse,currentReader);}else $('qTrack').textContent=this.tr('اختر سورة من قائمة السور المتاحة','Choose a surah from the available list');}
 audioMessage(ar,en){$('qAudioStatus').textContent=this.tr(ar,en)}
 async play(){this.versePlayback=false;if(!this.data)return;this.refresh();const surah=this.activeSurah,options=this.player.nativeQuran?{surah,repeat:$('qRepeat').checked,autoNext:$('qAutoNext').checked,nextSurahs:this.surahVerses.slice(surah),surahNames:this.data.surahs.map(s=>s.name)}:{surah};if(!recitationUrl(this.reciter,surah)){this.audioMessage('هذه السورة غير متاحة بصوت القارئ المختار.','This surah is unavailable for this reciter.');return;}this.beforePlay();this.playingReciter=this.reciter;$('qStop').disabled=false;if(this.reciter.fullSurahOnly){this.audioMessage('هذه التلاوة تعمل بالسورة كاملة؛ متابعة الآيات غير متاحة لهذا التسجيل.','This recording plays complete surahs; verse tracking is unavailable.');await this.pageAudio.playSurah(this.reciter,surah,options);return;}if(navigator.onLine===false){this.audioMessage('جارٍ فتح التسجيل المحفوظ؛ متابعة الآيات تحتاج اتصالًا بالإنترنت.','Opening saved audio; verse tracking needs an internet connection.');await this.pageAudio.playSurah(this.reciter,surah,options);return;}this.audioMessage('جارٍ تحميل التلاوة مع متابعة الآيات…','Loading recitation with verse tracking…');await this.pageAudio.play(this.reciter,this.surahVerses[surah-1],options);}
 stop(){this.versePlayback=false;this.pageAudio?.stop();$('qStop').disabled=true;$('qAudioStatus').textContent='';this.follow?.clear()}
 pauseForAdhan(){if(this.pageAudio.active||this.pageAudio.loading){if(!this.player.nativeQuran)this.stop();this.audioMessage('توقفت التلاوة مؤقتًا لبدء الأذان.','Recitation paused for adhan.')}}
}
