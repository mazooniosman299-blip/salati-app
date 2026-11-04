import {enhancePrintedPage} from './quran-printed-pages.js';
import {quranPlayer} from './native-quran-player.js';
import {fullSurahUrl} from './quran-audio-source.js';
import studioUrls from './sudais-studio-urls.json';
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
 const migrateAutoNext=saved.autoNextPolicy!==1;
 this.savedPrintedEdition=saved.printedEdition;this.page=this.validPage(saved.page)?saved.page:1;this.activeSurah=Number.isInteger(saved.activeSurah)?saved.activeSurah:null;this.bookmark=this.validPage(saved.bookmark)?saved.bookmark:null;this.size=saved.layoutVersion===2&&Number.isFinite(saved.size)?Math.max(22,Math.min(36,saved.size)):26;this.reciter=this.reciters.find(r=>r.id===saved.reciter)||this.reciters[0];this.audioSurah=this.reciter.surahs.includes(saved.audioSurah)?saved.audioSurah:this.reciter.surahs[0];this.player=quranPlayer($('qAudio'));this.player.loop=false;$('qRepeat').checked=!!saved.repeat;$('qAutoNext').checked=migrateAutoNext||saved.autoNext!==false;
 if(this.player.nativeQuran&&this.player.active){this.reciter=this.reciters.find(r=>r.id===this.player.state.reciter)||this.reciter;this.activeSurah=this.audioSurah=this.player.queue[this.player.queueIndex]?.surah||this.audioSurah;$('qRepeat').checked=!!this.player.state.repeat;$('qAutoNext').checked=migrateAutoNext||!!this.player.state.autoNext;}this.offline=new QuranOffline();this.followEnabled=saved.follow!==false;
 this.pageAudio=new PageRecitation({player:this.player,resolveSource:(reciter,surah,url)=>this.offline.resolve(reciter,surah,url),onComplete:()=>{if(this.versePlayback){this.versePlayback=false;this.audioMessage('انتهت تلاوة الآية.','Verse recitation finished.');return}if(this.player.nativeQuran){this.audioMessage('انتهت التلاوة.','Recitation finished.');return;}if($('qRepeat').checked)this.play();else if($('qAutoNext').checked){if(this.surahMode()){const i=this.reciter.surahs.indexOf(this.audioSurah);const id=this.reciter.surahs[i+1];if(id){this.go(this.surahPage(id),id,true);return}}else if(this.page<604){this.go(this.page+1,undefined,true);return}this.audioMessage('انتهت التلاوة.','Recitation finished.')}else this.audioMessage(this.surahMode()?'انتهت تلاوة السورة.':'انتهت تلاوة الصفحة.',this.surahMode()?'Surah recitation finished.':'Page recitation finished.')},onStop:()=>this.follow?.clear(),onError:code=>this.audioMessage(code==='offline'?'التلاوة تحتاج اتصالًا بالإنترنت.':code==='unsupported'?'متابعة الآيات غير متاحة لهذا القارئ. اختر قارئًا آخر.':'تعذر تشغيل التلاوة. تحقق من الاتصال واضغط تشغيل.',code==='offline'?'Recitation needs an internet connection.':code==='unsupported'?'Verse tracking is unavailable for this reciter. Choose another reciter.':'Could not play recitation. Check your connection and press Play.'),onVerse:(v,cue)=>{if(!this.data)return;const id=v?.s||cue?.surah;if(id)this.audioSurah=id;if(this.player.nativeQuran&&id&&!this.entryFollowPaused){this.activeSurah=id;$('qSurah').value=String(id);}if(id)this.renderTrack(id,v,this.player.nativeQuran?(this.reciters.find(r=>r.id===this.player.state.reciter)||this.reciter):(this.versePlayback?this.playingReciter:this.reciter));this.follow.show(v,cue)}});$('qPageForm').onsubmit=e=>{e.preventDefault();this.go(Number($('qPageNumber').value))};$('qSurah').onchange=()=>this.go(this.surahPage(Number($('qSurah').value)),Number($('qSurah').value));$('qJuz').onchange=()=>this.go(this.readingPages().findIndex(p=>p.some(v=>v.j===Number($('qJuz').value)))+1);$('qSmaller').onclick=()=>this.resize(-2);$('qLarger').onclick=()=>this.resize(2);$('qBookmark').onclick=()=>{this.captureReadingPosition();this.bookmark=this.page;this.save();this.refreshBookmarkControls()};$('qResume').onclick=()=>this.go(this.bookmark);$('qRetry').onclick=()=>this.open();
 $('qReciter').onchange=()=>{this.stop();this.reciter=this.reciters.find(r=>r.id===$('qReciter').value);if(this.data&&!this.reciter.surahs.includes(this.activeSurah)){const id=this.reciter.surahs[0];this.go(this.surahPage(id),id);this.audioMessage('السورة السابقة غير متاحة لهذا القارئ؛ فُتحت أول سورة متاحة بصوته.','The previous surah is unavailable for this reciter; the first available surah has been opened.')}this.save();this.refresh()};$('qPlay').onclick=()=>this.play();$('qStop').onclick=()=>this.stop();

 this.setupPrintedReader();this.setupFollow();this.setupPlayer();this.setupVerseActions();this.setupReadingPosition();
 $('qRepeat').onchange=$('qAutoNext').onchange=()=>{if(!this.versePlayback)this.player.setOptions?.($('qRepeat').checked,$('qAutoNext').checked);this.save();};
 this.player.addEventListener('play',()=>{this.beforePlay();this.audioMessage('جارٍ تشغيل التلاوة…','Playing recitation…')});this.player.addEventListener('pause',()=>{if(this.player.src&&!this.player.ended&&this.pageAudio.active)this.audioMessage('التلاوة متوقفة مؤقتًا.','Recitation paused.')});this.player.addEventListener('waiting',()=>this.audioMessage('جارٍ تحميل التلاوة…','Buffering recitation…'));this.player.addEventListener('playing',()=>this.audioMessage('جارٍ تشغيل التلاوة…','Playing recitation…'));this.player.addEventListener('error',()=>this.audioMessage('تعذر تحميل التلاوة. تحقق من الإنترنت أو جرّب سورة أخرى، ثم اضغط تشغيل لإعادة المحاولة.','Could not load recitation. Check your connection or choose another surah, then press Play to retry.'));if(this.player.nativeQuran){const resume=()=>{this.player.sync();this.pageAudio.syncNative();this.follow.refresh(true);};window.addEventListener('salati-native-resume',resume);document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')resume();});}this.refresh();if(migrateAutoNext&&this.player.nativeQuran&&this.player.active)this.player.setOptions?.($('qRepeat').checked,true);if(migrateAutoNext||saved.reciter&&saved.reciter!==this.reciter.id)this.save();
 }
 setupPrintedReader(){
  const panel=$('mushaf');panel.classList.add('printed-reader');
  const dialog=document.createElement('dialog');dialog.id='qReaderOptions';dialog.className='printed-reader-options';
  const close=document.createElement('button');close.type='button';close.className='nav-icon-button';close.textContent='×';close.setAttribute('aria-label',this.tr('إغلاق','Close'));close.onclick=()=>dialog.close();
  dialog.append(close,panel.querySelector('.mushaf-toolbar'),panel.querySelector('.mushaf-credit'));panel.append(dialog);dialog.querySelector('.mushaf-toolbar').append($('qFollowToggle').closest('label'));
  const header=document.createElement('div');header.className='printed-reader-header';
  const options=document.createElement('button');options.type='button';options.className='nav-icon-button';options.textContent='☰';options.setAttribute('aria-label',this.tr('السور وإعدادات المصحف','Surahs and Quran settings'));options.setAttribute('aria-controls',dialog.id);options.onclick=()=>dialog.showModal();
  const back=document.createElement('button');back.type='button';back.id='qReaderBack';back.className='nav-icon-button';back.textContent='←';back.setAttribute('aria-label',this.tr('العودة للمواقيت','Back to prayer times'));back.onclick=()=>document.querySelector('[data-tab="times"]').click();
  header.append(options,panel.querySelector('.mushaf-page-head'),back);panel.prepend(header);
  $('qVerses').addEventListener('printedpage',()=>{if(this.selectedAyahKey){const target=$('qVerses').querySelector('[data-ayah="'+this.selectedAyahKey+'"]');if(target){this.selectedAyah=target;target.classList.add('is-selected');target.setAttribute('aria-pressed','true');}}this.follow?.refresh()});
 }
 setupFollow(){
 const canScroll=()=>!this.entryFollowPaused&&document.visibilityState!=='hidden'&&!$('mushaf').hidden&&!this.verseMenuOpen&&!document.querySelector('dialog[open]');
 this.follow=new QuranFollow({enabled:this.followEnabled,canScroll,
  find:v=>$('qVerses').querySelector('[data-ayah="'+v.s+':'+v.a+'"]'),
  ensure:v=>this.ensurePlayingVerse(v),
  scroll:element=>{const [s,a]=element.dataset.ayah.split(':').map(Number);this.updateReadingPosition({s,a});element.closest('.quran-reading-page').style.contentVisibility='visible';element.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'center'});},
  render:(v,cue)=>{const bar=$('qFollowBar');bar.hidden=!v&&!cue?.intro;if(bar.hidden)return;const surah=this.data.surahs[(v?.s||cue.surah)-1];const name=this.getLang()==='ar'?surah.name:surah.transliteration;const number=n=>new Intl.NumberFormat(this.getLang()).format(n);$('qCurrentVerse').textContent=name+' · '+(v?this.tr('الآية ','Verse ')+number(v.a)+' / '+number(this.surahVerses[v.s-1].length):this.tr('البسملة','Basmala'));}
 });
 $('qFollowToggle').checked=this.followEnabled;$('qFollowToggle').onchange=()=>{this.entryFollowPaused=false;this.followEnabled=$('qFollowToggle').checked;this.follow.setEnabled(this.followEnabled);this.save();};
 }
 setupReadingPosition(){
  const record=()=>{if(this.readingPositionScheduled)return;this.readingPositionScheduled=true;requestAnimationFrame(()=>{this.readingPositionScheduled=false;this.captureReadingPosition()})};
  window.addEventListener('scroll',record,{passive:true});
  document.querySelector('main')?.addEventListener('scroll',record,{passive:true});
  // The reading area now scrolls independently of the application shell.
  $('qVerses').addEventListener('scroll',record,{passive:true});
  for(const event of ['wheel','touchstart','pointerdown','keydown'])$('qVerses').addEventListener(event,()=>{this.readingTargetPage=null},{passive:true});
  document.addEventListener('visibilitychange',()=>{
   if(document.visibilityState==='visible'&&!$('mushaf').hidden)this.enterAtSurahStart(this.activeSurah,true);
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
  // Ignore the previous page while an explicit chapter/bookmark scroll is
  // still travelling. Manual reading input cancels this navigation guard.
  if(this.readingTargetPage){if(Number(page?.dataset.readingPage)!==this.readingTargetPage)return;this.readingTargetPage=null;}
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
  const panel=$('mushaf'),dock=document.createElement('div');
  dock.id='qAyahActions';dock.className='ayah-action-dock';dock.hidden=true;dock.setAttribute('role','toolbar');
  this.ayahActionButtons=new Map();
  for(const [action,icon,ar,en] of [
   ['play','play','تشغيل','Play'],['start','surah-start','بداية السورة','Surah start'],
   ['bookmark','bookmark','حفظ الصفحة','Bookmark'],['close','close','إغلاق','Close']
  ]){
   const button=document.createElement('button');button.type='button';button.className='nav-icon-button';button.dataset.ayahAction=action;
   const image=new Image();image.src='icons/ayah-'+icon+'.svg';image.alt='';image.width=image.height=21;
   const label=document.createElement('span');label.dataset.ar=ar;label.dataset.en=en;label.textContent=this.tr(ar,en);button.append(image,label);
   if(action==='play')button.classList.add('active');dock.append(button);this.ayahActionButtons.set(action,button);
  }
  panel.insertBefore(dock,$('mushafPlayerSlot'));this.ayahActions=dock;
  const selected=()=>{const [s,a]=(this.selectedAyahKey||'').split(':').map(Number);return this.surahVerses?.[s-1]?.[a-1]};
  this.ayahActionButtons.get('play').onclick=()=>{
   const verse=selected();if(!verse)return;
   if(this.pageAudio.active&&this.audioSurah===verse.s&&this.player.getAttribute('src')){
    if(this.player.paused){this.entryFollowPaused=false;this.player.play().catch(()=>this.audioMessage('تعذر التشغيل. حاول مجددًا.','Could not play. Try again.'));}else this.player.pause();
   }else this.playFromAyah(verse);
  };
  this.ayahActionButtons.get('start').onclick=()=>{const verse=selected();if(verse){this.stop();this.go(this.surahPage(verse.s),verse.s,true)}};
  this.ayahActionButtons.get('bookmark').onclick=()=>{const page=this.versePages?.get(this.selectedAyahKey);if(page){this.bookmark=page;this.save();this.refreshBookmarkControls();this.updateAyahActions()}};
  this.ayahActionButtons.get('close').onclick=()=>this.hideAyahActions(true);
  const select=element=>{
   const [s,a]=element.dataset.ayah.split(':').map(Number),verse=this.surahVerses?.[s-1]?.[a-1];if(!verse||verse.a!==a)return;
   this.selectedAyah?.classList.remove('is-selected');this.selectedAyah?.removeAttribute('aria-pressed');
   this.selectedAyah=element;this.selectedAyahKey=element.dataset.ayah;element.classList.add('is-selected');element.setAttribute('aria-pressed','true');
   dock.hidden=false;panel.classList.add('has-ayah-actions');this.updateAyahActions();
   requestAnimationFrame(()=>{if(this.selectedAyah===element&&!dock.hidden)element.scrollIntoView({block:'nearest',inline:'nearest',behavior:'instant'})});
   this.playFromAyah(verse);
  };
  $('qVerses').addEventListener('click',event=>{const selection=window.getSelection();if(selection&&!selection.isCollapsed)return;const verse=event.target.closest('[data-ayah]');if(verse)select(verse)});
  $('qVerses').addEventListener('contextmenu',event=>{const verse=event.target.closest('[data-ayah]');if(verse){event.preventDefault();select(verse)}});
  $('qVerses').addEventListener('keydown',event=>{if((event.key==='Enter'||event.key===' ')&&event.target.matches('[data-ayah]')){event.preventDefault();select(event.target)}});
  panel.addEventListener('keydown',event=>{if(event.key==='Escape'&&!dock.hidden&&!document.querySelector('dialog[open]')){event.preventDefault();this.hideAyahActions(true)}});
  for(const event of ['play','playing','pause','ended','emptied','trackchange'])this.player.addEventListener(event,()=>this.updateAyahActions());
  this.updateAyahActions();
 }
 updateAyahActions(){
  if(!this.ayahActions)return;
  const button=this.ayahActionButtons.get('play'),playing=this.pageAudio.active&&!this.player.paused;
  button.querySelector('img').src='icons/ayah-'+(playing?'pause':'play')+'.svg';
  const label=button.querySelector('span');label.dataset.ar=playing?'إيقاف مؤقت':'تشغيل';label.dataset.en=playing?'Pause':'Play';
  for(const control of this.ayahActionButtons.values()){
   const text=control.querySelector('span');text.textContent=text.dataset[this.getLang()];
  }
  button.setAttribute('aria-label',playing?this.tr('إيقاف مؤقت','Pause'):this.tr('تشغيل من الآية المحددة','Play from selected ayah'));
  this.ayahActions.setAttribute('aria-label',this.tr('إجراءات الآية ','Verse actions ')+(this.selectedAyahKey?.split(':')[1]||''));
 }
 hideAyahActions(focus=false){
  if(!this.ayahActions)return;this.ayahActions.hidden=true;$('mushaf').classList.remove('has-ayah-actions');
  if(focus&&this.selectedAyah?.isConnected)this.selectedAyah.focus({preventScroll:true});
 }
 async playFromAyah(verse){
  if(this.reciter.fullSurahOnly){this.audioMessage('تحديد بداية الآية غير متاح لهذا التسجيل. اختر قارئًا آخر من إعدادات المصحف.','Ayah start times are unavailable for this recording. Choose another reciter in Quran settings.');return;}
  if(navigator.onLine===false){this.audioMessage('التشغيل من الآية يحتاج اتصالًا بالإنترنت لهذا التسجيل. يمكنك تشغيل السورة المحفوظة بزر التشغيل.','Starting at an ayah needs an internet connection for this recording. Use Play for your downloaded surah.');return;}
  this.stop();this.activeSurah=this.audioSurah=verse.s;this.save();this.beforePlay();this.playingReciter=this.reciter;
  $('qStop').disabled=false;this.renderTrack(verse.s,verse);this.audioMessage('جارٍ تحميل التلاوة…','Loading recitation…');
  const options={surah:verse.s,startAyah:verse.a,repeat:$('qRepeat').checked,autoNext:$('qAutoNext').checked,nextSurahs:this.surahVerses.slice(verse.s),surahNames:this.data.surahs.map(s=>s.name)};
  await this.pageAudio.play(this.reciter,this.surahVerses[verse.s-1],options);
 }
 setupPlayer(){
 const player=this.player;player.muted=false;player.volume=1;const seek=$('qSeek');const clock=value=>{const seconds=Math.max(0,Math.floor(value||0));return (seconds>=3600?Math.floor(seconds/3600)+':'+String(Math.floor(seconds/60)%60).padStart(2,'0'):Math.floor(seconds/60))+':'+String(seconds%60).padStart(2,'0')};
 const bounds=()=>{const segment=this.pageAudio.queue[this.pageAudio.index];return {start:segment?.start||0,end:segment?.end??player.duration}};
 const update=()=>{const {start,end}=bounds(),duration=Number.isFinite(end)?Math.max(0,end-start):0,elapsed=Math.max(0,Math.min(duration,player.currentTime-start));seek.disabled=!duration;seek.value=duration?elapsed/duration*100:0;seek.style.setProperty('--seek',seek.value+'%');$('qElapsed').textContent=clock(elapsed);$('qDuration').textContent=duration?clock(duration):'—:—';$('qTransportIcon').setAttribute('d',player.paused?'M8 5v14l11-7z':'M6 5h4v14H6zM14 5h4v14h-4z');$('qTransport').setAttribute('aria-label',player.paused?this.tr('تشغيل','Play'):this.tr('إيقاف مؤقت','Pause'));$('qFollowTransport').textContent=player.paused?this.tr('▶ تشغيل','▶ Play'):this.tr('Ⅱ إيقاف مؤقت','Ⅱ Pause');seek.setAttribute('aria-label',this.pageAudio.queue[this.pageAudio.index]?.verse?this.tr('موضع التشغيل داخل الآية','Playback position within verse'):this.tr('موضع التشغيل داخل السورة','Playback position within surah'));};
 $('qTransport').onclick=()=>{if(!player.paused){player.pause();return}this.entryFollowPaused=false;this.follow.refresh(true);if(this.pageAudio.active&&player.getAttribute('src'))player.play().catch(()=>this.audioMessage('تعذر تشغيل التلاوة. حاول مجددًا.','Could not play. Try again.'));else this.play()};
 $('qFollowTransport').onclick=()=>$('qTransport').click();
 seek.oninput=()=>{const {start,end}=bounds();if(Number.isFinite(end)&&end>start)player.currentTime=start+(end-start)*Number(seek.value)/100;update()};
 for(const event of ['timeupdate','loadedmetadata','durationchange','play','pause','emptied','ended','volumechange'])player.addEventListener(event,update);update();
 }
 readingPages(){return this.printedPages||this.data.pages}
 surahPage(id){return this.versePages?.get(id+':1')||this.data.surahs[id-1].page}
 continuousReading(){return true}
 goSurah(step){const id=this.activeSurah+step;if(this.data&&id>=1&&id<=114)this.go(this.surahPage(id),id,true)}
 renderTrack(surah,verse,reader=this.reciter){const info=this.data?.surahs[surah-1];if(!info)return;const row=this.surahVerses?.[surah-1]?.[(verse?.a||1)-1];const part=row?.j||1;const arabic=this.getLang()==='ar';const partName=part===1&&arabic?'الأول':new Intl.NumberFormat(this.getLang()).format(part);$('qTrackTitle').textContent=this.tr('سورة ','Surah ')+(arabic?info.name:info.transliteration);$('qTrack').textContent=this.tr('الجزء ','Juz ')+partName;$('qTrack').title=reader[this.getLang()]+(verse?' · '+this.tr('الآية ','Verse ')+verse.a:'');}
 surahMode(){return true}
 tr(ar,en){return this.getLang()==='ar'?ar:en} validPage(p){return Number.isInteger(p)&&p>=1&&p<=604}
 save(){try{localStorage.setItem('salati-quran',JSON.stringify({page:this.page,activeSurah:this.activeSurah,bookmark:this.bookmark,size:this.size,layoutVersion:2,printedEdition:this.savedPrintedEdition,reciter:this.reciter.id,audioSurah:this.audioSurah,repeat:$('qRepeat').checked,autoNext:$('qAutoNext').checked,autoNextPolicy:1,follow:this.followEnabled}))}catch{}}
 async open(){if(this.data){this.follow.refresh(true);return true;}if(this.opening)return this.opening;this.opening=this.loadData();try{return await this.opening}finally{this.opening=null}}
 // Explicit tab entry always starts at Fatiha; a visibility resume passes
 // the current surah. Saved bookmarks/preferences remain independent.
 // Keep background native recitation alive; only reset the reading viewport.
 async enterAtSurahStart(surahId=1,resuming=false){
  if(!resuming)this.hideAyahActions?.();
  const navigation=this.readingNavigation=(this.readingNavigation||0)+1;
  if(!await this.open()||navigation!==this.readingNavigation||$('mushaf').hidden)return false;
  const surah=this.data.surahs[surahId-1]||this.data.surahs[0];
  if(!surah)return false;
  this.follow?.clear();
  this.activeSurah=surah.id;
  if(!resuming)this.entryFollowPaused=surah.id===1&&(this.pageAudio.active||this.pageAudio.loading);
  this.page=this.surahPage(surah.id);
  this.readingTargetPage=this.page;
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
 async loadData(){this.loading=true;this.loadFailed=false;$('qTransport').disabled=true;$('qTrack').textContent=this.tr('جارٍ فتح المصحف…','Loading Quran…');$('qLoadStatus').textContent=this.tr('جارٍ فتح المصحف…','Loading Quran…');$('qRetry').hidden=true;try{const r=await fetch('quran/data.json');if(!r.ok)throw Error();const data=await r.json();if(data.pages?.length!==604||data.surahs?.length!==114||data.pages.some(p=>!p.length)||data.pages.flat().length!==6236)throw Error();this.data=data;
 const indexResponse=await fetch('quran/printed-1441/index.json');if(!indexResponse.ok)throw Error('printed index');const printedIndex=await indexResponse.json();
 const canonical=new Map(data.pages.flat().map(v=>[v.s+':'+v.a,v])),keys=printedIndex.pages?.flat();
 if(printedIndex.pages?.length!==604||keys?.length!==6236||new Set(keys).size!==6236||keys.some(key=>!canonical.has(key)))throw Error('printed index');
 this.printedPages=printedIndex.pages.map(page=>page.map(key=>canonical.get(key)));
 this.versePages=new Map();this.surahVerses=Array.from({length:114},()=>[]);this.readingPages().forEach((page,index)=>page.forEach(v=>{this.versePages.set(v.s+':'+v.a,index+1);this.surahVerses[v.s-1].push(v)}));if(this.savedPrintedEdition!=='1441'){if(this.bookmark){const v=data.pages[this.bookmark-1][0];this.bookmark=this.versePages.get(v.s+':'+v.a)||this.bookmark;}this.savedPrintedEdition='1441';this.save();}const current=this.readingPages()[this.page-1];const selected=current.some(v=>v.s===this.activeSurah)?this.activeSurah:current[0].s;let restored=false;if(!this.reciter.surahs.includes(selected)){const id=this.reciter.surahs[0];this.page=data.surahs[id-1].page;this.activeSurah=id;restored=true;this.save()}$('qLoadStatus').textContent='';$('qSheet').setAttribute('aria-busy','false');this.refresh();this.pageAudio?.syncNative?.();if(restored)this.audioMessage('السورة المحفوظة غير متاحة بصوت هذا القارئ؛ فُتحت سورة متاحة بصوته.','The saved surah is unavailable for this reciter; an available surah has been opened.');return true}catch{this.loadFailed=true;$('qTrack').textContent=this.tr('افتح المصحف وأعد المحاولة.','Open Quran and retry.');$('qLoadStatus').textContent=this.tr('تعذر فتح المصحف. تحقق من الاتصال وأعد المحاولة.','Could not load Quran. Check your connection and retry.');$('qRetry').hidden=false;return false}finally{this.loading=false}}
 async openVerse(surah,ayah){
  if(!Number.isInteger(surah)||surah<1||surah>114||!Number.isInteger(ayah)||ayah<1||!await this.open())return false;
  const page=this.versePages.get(surah+':'+ayah);if(!page)return false;
  this.stop();this.go(page,surah);const verse=$('qVerses').querySelector('[data-ayah="'+surah+':'+ayah+'"]');if(!verse)return false;
  verse.closest('.quran-reading-page').style.contentVisibility='visible';verse.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'center'});verse.focus({preventScroll:true});return true;
 }
 go(page,surah,autoplay=false){if(!this.data||!this.validPage(page))return;this.hideAyahActions?.();this.readingNavigation=(this.readingNavigation||0)+1;this.entryFollowPaused=false;this.readingTargetPage=page;const ids=this.readingPages()[page-1].map(v=>v.s);const selected=ids.includes(surah)?surah:ids[0];const targetVerse=this.readingPages()[page-1].find(v=>v.s===selected);const resume=autoplay||!this.player.paused;const keep=this.surahMode()&&selected===this.activeSurah&&this.pageAudio.active&&!this.player.paused&&this.pageAudio.surahKey===this.reciter.id+':'+selected;if(!keep)this.stop();this.page=page;this.activeSurah=selected;this.save();this.refresh();(this.continuousReading()?document.querySelector('[data-ayah="'+selected+':'+targetVerse.a+'"]'):$('qSheet'))?.scrollIntoView({behavior:'smooth',block:'start'});if(resume&&!keep)this.play()}
 resize(delta){this.size=Math.max(22,Math.min(36,this.size+delta));this.save();this.refresh()}
 makeReadingPage(index){
  // Remove only font-dependent decorative round-zero / verse-circle marks from
  // rendered display; the canonical licensed JSON remains byte-for-byte intact.
  const printable=text=>text.replace(/[\u06DD\u06DE\u06DF\u06E0]/gu,'');
 const verses=this.readingPages()[index],page=document.createElement('section');page.className='quran-reading-page';page.dataset.readingPage=index+1;
 
 const fragment=document.createDocumentFragment();let paragraph;for(const original of verses){const v={...original,t:printable(original.t)};if(!paragraph||v.a===1){if(v.a===1){const h=document.createElement('h3');h.className='quran-surah-title';h.textContent='سورة '+this.data.surahs[v.s-1].name;fragment.append(h)}paragraph=document.createElement('p');paragraph.className='quran-text';fragment.append(paragraph)}const span=document.createElement('span');span.dataset.ayah=v.s+':'+v.a;span.tabIndex=0;span.setAttribute('aria-label','الآية '+v.a+'، استماع');const basmala=v.t.split(' ').slice(0,4).join(' ');if(v.a===1&&v.s!==9&&v.t.startsWith(basmala)){if(v.s===1){span.classList.add('quran-basmala');span.textContent=v.t+' '}else{const opening=document.createElement('span');opening.className='quran-basmala';opening.textContent=basmala;span.append(opening,document.createTextNode(v.t.slice(basmala.length)+' '))}}else span.textContent=v.t+' ';const mark=document.createElement('span');mark.className='ayah-number';mark.textContent='﴿'+new Intl.NumberFormat('ar').format(v.a)+'﴾';mark.setAttribute('aria-label','الآية '+v.a);span.append(mark,document.createTextNode(' '));paragraph.append(span)}page.append(fragment);const walker=document.createTreeWalker(page,NodeFilter.SHOW_TEXT);const affected=[];while(walker.nextNode())if(/[\u06df\u06e0]/u.test(walker.currentNode.textContent))affected.push(walker.currentNode);for(const node of affected){const replacement=document.createDocumentFragment();for(const token of node.textContent.split(/(\s+)/u)){if(/[\u06df\u06e0]/u.test(token)){const word=document.createElement('span');word.className='quran-compatible-mark';word.textContent=token;replacement.append(word)}else replacement.append(document.createTextNode(token))}node.replaceWith(replacement)}
 const number=document.createElement('div');number.className='reading-page-number';number.textContent=new Intl.NumberFormat('ar').format(index+1);page.append(number);if(typeof Image==='function')enhancePrintedPage(page,index,verses);return page;
 }
 renderReadingPages(){
 if(this.page>=this.readingStart&&this.page<=this.readingNext)return;this.readingObserver?.disconnect();this.readingHeightObserver?.disconnect?.();const container=$('qVerses');container.style?.removeProperty?.('--salati-quran-window-height');container.replaceChildren();$('qSheet').classList.add('continuous-sheet');this.readingStart=this.page;this.readingNext=this.page-1;const sentinel=document.createElement('div');sentinel.className='reading-page-sentinel';sentinel.setAttribute('aria-hidden','true');
 const append=this.appendReadingPage=()=>{if(!sentinel.isConnected)return;if(this.readingNext>=604){this.readingObserver?.disconnect();sentinel.remove();return}const page=this.makeReadingPage(this.readingNext++);container.insertBefore(page,sentinel);page.style.contentVisibility='auto';page.style.containIntrinsicSize='auto 900px';};
 container.append(sentinel);append();
 // Printed-reader CSS owns the viewport; original image aspect ratios own leaf height.
  this.readingObserver=new IntersectionObserver(entries=>{if(entries.some(e=>e.isIntersecting)){append();this.readingObserver.unobserve(sentinel);requestAnimationFrame(()=>{if(sentinel.isConnected)this.readingObserver.observe(sentinel)})}},{root:container,rootMargin:'600px 0px'});this.readingObserver.observe(sentinel);
 }
 refresh(){this.updateAyahActions?.();const name=s=>this.getLang()==='ar'?s.name:s.transliteration;const select=(id,options,value)=>{const el=$(id);el.replaceChildren(...options.map(([val,label])=>new Option(label,val)));el.value=String(value)};
 select('qReciter',this.reciters.map(r=>[r.id,r[this.getLang()]]),this.reciter.id);$('qFollowToggle').checked=this.followEnabled&&!this.reciter.fullSurahOnly;$('qFollowToggle').disabled=!!this.reciter.fullSurahOnly;const followLabel=$('qFollowToggle').parentElement?.querySelector('span');if(followLabel)followLabel.textContent=this.reciter.fullSurahOnly?this.tr('هذه النسخة تعمل بالسورة كاملة','This edition plays complete surahs'):this.tr('متابعة الآية','Follow verse');this.refreshBookmarkControls();$('qSmaller').disabled=this.size<=22;$('qLarger').disabled=this.size>=36;$('qVerses').style.fontSize=this.size+'px';$('qVerses').style.setProperty?.('--printed-scale',String(this.size/26));
 $('qTransport').disabled=!this.data;if(!this.data){$('qTrack').textContent=this.loadFailed?this.tr('افتح المصحف وأعد المحاولة.','Open Quran and retry.'):this.tr('جارٍ فتح المصحف…','Loading Quran…');return;}const pageVerses=this.readingPages()[this.page-1];if(!pageVerses.some(v=>v.s===this.activeSurah)&&!this.pageAudio.active&&!this.pageAudio.loading)this.activeSurah=pageVerses[0].s;const continuous=this.continuousReading(),verses=pageVerses,first=pageVerses.find(v=>v.s===this.activeSurah)||pageVerses[0];const audible=this.pageAudio.active||this.pageAudio.loading;const currentClip=audible?this.pageAudio.queue?.[this.pageAudio.index]:null;this.audioSurah=audible?(currentClip?.surah||currentClip?.verse?.s||this.follow?.current?.verse?.s||this.audioSurah||this.activeSurah):this.activeSurah;$('qPageNumber').value=this.page;select('qSurah',this.data.surahs.map(s=>[s.id,s.id+' · '+name(s)]),this.activeSurah);select('qJuz',Array.from({length:30},(_,i)=>[i+1,this.tr('الجزء ','Juz ')+(i+1)]),first.j);$('qSurah').disabled=$('qJuz').disabled=false;const ids=continuous?[this.activeSurah]:[...new Set(verses.map(v=>v.s))];$('qPageSurah').textContent=ids.map(id=>this.data.surahs[id-1].name).join(' · ');$('qPageJuz').textContent='الجزء '+new Intl.NumberFormat('ar').format(first.j);$('qPageLabel').textContent=new Intl.NumberFormat('ar').format(this.page);$('qProgress').textContent=this.page+' / 604';$('qPageForm').hidden=continuous;$('qPageLabel').hidden=continuous;if(continuous){$('qProgress').textContent=this.activeSurah+' / 114';}
 this.renderReadingPages();this.follow?.refresh();
 const available=this.reciter.surahs.includes(this.audioSurah);$('qPlay').disabled=!available;$('qCoverage').textContent=this.reciter.surahs.length===114?this.tr('جميع السور متاحة بصوت هذا القارئ.','All surahs available for this reciter.'):this.tr('السور المتاحة بصوت هذا القارئ: '+this.reciter.surahs.length+'؛ اختر منها في القائمة.','Available surahs for this reciter: '+this.reciter.surahs.length+'. Choose from the list.');$('qCoverage').hidden=this.surahMode();if(this.surahMode())$('qCoverage').textContent='';$('qRepeat').parentElement.querySelector('span').textContent=this.surahMode()?this.tr('تكرار السورة','Repeat surah'):this.tr('تكرار الصفحة','Repeat page');$('qAutoNext').parentElement.querySelector('span').textContent=this.surahMode()?this.tr('السورة التالية تلقائيًا','Auto-play next surah'):this.tr('الصفحة التالية تلقائيًا','Auto-play next page');if(available){const currentVerse=audible?(this.follow?.current?.verse?.s===this.audioSurah?this.follow.current.verse:currentClip?.verse):undefined;const currentReader=audible?(this.player?.nativeQuran?(this.reciters.find(r=>r.id===this.player.state.reciter)||this.reciter):(this.playingReciter||this.reciter)):this.reciter;this.renderTrack(this.audioSurah,currentVerse,currentReader);}else $('qTrack').textContent=this.tr('اختر سورة من قائمة السور المتاحة','Choose a surah from the available list');}
 audioMessage(ar,en){$('qAudioStatus').textContent=this.tr(ar,en)}
 async play(){this.entryFollowPaused=false;this.versePlayback=false;if(!this.data)return;this.refresh();const surah=this.activeSurah,options=this.player.nativeQuran?{surah,repeat:$('qRepeat').checked,autoNext:$('qAutoNext').checked,nextSurahs:this.surahVerses.slice(surah),surahNames:this.data.surahs.map(s=>s.name)}:{surah};if(!recitationUrl(this.reciter,surah)){this.audioMessage('هذه السورة غير متاحة بصوت القارئ المختار.','This surah is unavailable for this reciter.');return;}this.beforePlay();this.playingReciter=this.reciter;$('qStop').disabled=false;if(this.reciter.fullSurahOnly){this.audioMessage('هذه التلاوة تعمل بالسورة كاملة؛ متابعة الآيات غير متاحة لهذا التسجيل.','This recording plays complete surahs; verse tracking is unavailable.');await this.pageAudio.playSurah(this.reciter,surah,options);return;}if(navigator.onLine===false){this.audioMessage('جارٍ فتح التسجيل المحفوظ؛ متابعة الآيات تحتاج اتصالًا بالإنترنت.','Opening saved audio; verse tracking needs an internet connection.');await this.pageAudio.playSurah(this.reciter,surah,options);return;}this.audioMessage('جارٍ تحميل التلاوة مع متابعة الآيات…','Loading recitation with verse tracking…');await this.pageAudio.play(this.reciter,this.surahVerses[surah-1],options);}
 stop(){this.entryFollowPaused=false;this.versePlayback=false;this.pageAudio?.stop();$('qStop').disabled=true;$('qAudioStatus').textContent='';this.follow?.clear()}
 pauseForAdhan(){if(this.pageAudio.active||this.pageAudio.loading){if(!this.player.nativeQuran)this.stop();this.audioMessage('توقفت التلاوة مؤقتًا لبدء الأذان.','Recitation paused for adhan.')}}
}
