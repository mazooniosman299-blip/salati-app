/* Real Salati 604-page Quran reader + full-screen Mushaf mode.
   No images, modified scripture, substitute player, fake audio or other-tab edits.
   Wave bars visualize progress of the existing audio seek slider; their height
   pattern is illustrative (NOT decoded acoustic waveform of a remote MP3). */
(() => {
 'use strict';
 const $=id=>document.getElementById(id);
 document.addEventListener('DOMContentLoaded',()=>{
  const mushaf=$('mushaf'),reader=$('qVerses'),source=$('qSurah');
  const previous=$('qPrevSurah'),next=$('qNextSurah'),loop=$('qLoopSurah');
  const repeat=$('qRepeat'),seek=$('qSeek'),player=$('mushafPlayerSlot');
  const back=$('qFullBack'),menu=$('qFullMenu'),playerToggle=$('qFullPlayerToggle');
  const title=$('qFullSurah'),juz=$('qFullJuz');
  if(!mushaf||!reader||!source||!previous||!next||!loop||
     !repeat||!seek||!player||!back||!menu||!playerToggle)return;

  // Treat fullscreen as a state of the real Quran tab, not a second app screen.
  // The original app's tab control remains the single navigation source.
  const exitFullscreen=()=>{
   document.querySelector('header>.site-nav button[data-tab="times"]')?.click();
  };
  const syncFullscreen=()=>{
   const open=!mushaf.hidden;
   document.body.classList.toggle('salati-quran-fullscreen',open);
   if(!open){
    mushaf.classList.remove('q-full-menu-open');
    menu.setAttribute('aria-expanded','false');
   }
   else {
    const main=document.querySelector('main');
    if(main) main.scrollTop=0;
   }
  };
  new MutationObserver(syncFullscreen).observe(mushaf,{attributes:true,attributeFilter:['hidden']});
  syncFullscreen();
  back.addEventListener('click',exitFullscreen);
  document.addEventListener('keydown',event=>{
   if(event.key!=='Escape'||mushaf.hidden)return;
   if(mushaf.classList.contains('q-full-menu-open')){
    mushaf.classList.remove('q-full-menu-open');
    menu.setAttribute('aria-expanded','false');
   }else exitFullscreen();
  });
  menu.addEventListener('click',()=>{
   const open=mushaf.classList.toggle('q-full-menu-open');
   menu.setAttribute('aria-expanded',String(open));
   if(open) $('qSurah')?.focus({preventScroll:true});
  });
  playerToggle.addEventListener('click',()=>{
   const collapsed=mushaf.classList.toggle('q-full-player-hidden');
   playerToggle.setAttribute('aria-expanded',String(!collapsed));
   playerToggle.setAttribute('aria-label',collapsed?'إظهار المشغّل / Show player':'إخفاء المشغّل / Hide player');
  });
  const updateHeader=()=>{
   title.textContent=$('qPageSurah')?.textContent||'المصحف الشريف';
   juz.textContent=$('qPageJuz')?.textContent||'القرآن الكريم';
  };
  ['qPageSurah','qPageJuz'].forEach(id=>{
   const el=$(id);
   if(el)new MutationObserver(updateHeader).observe(el,{characterData:true,childList:true,subtree:true});
  });
  updateHeader();

  // Keep original controls and their real handlers. The hidden Quran selectors
  // are the app's state owners; our transport buttons dispatch their changes.
  const move=step=>{
   const current=Number(source.value);
   if(source.disabled||!Number.isInteger(current)||current<1||current>114)return;
   const target=Math.max(1,Math.min(114,current+step));
   if(target===current)return;
   source.value=String(target);
   source.dispatchEvent(new Event('change',{bubbles:true}));
  };
  previous.addEventListener('click',()=>move(-1));
  next.addEventListener('click',()=>move(1));
  const syncRepeat=()=>{
   const enabled=!!repeat.checked;
   loop.setAttribute('aria-pressed',String(enabled));
   loop.title=enabled?'إلغاء التكرار / Disable repeat':'تكرار السورة / Repeat surah';
  };
  loop.addEventListener('click',()=>{
   repeat.checked=!repeat.checked;
   repeat.dispatchEvent(new Event('change',{bubbles:true}));
   syncRepeat();
  });
  repeat.addEventListener('change',syncRepeat);
  syncRepeat();

  // Real seek and real elapsed/duration values stay owned by QuranReader.
  // Bars are a representative shape, not an inference about the MP3 spectrum.
  const track=$('qWaveBars');
  if(!track)return;
  const COUNT=63;
  const heights=Array.from({length:COUNT},(_,i)=>{
   const x=i/(COUNT-1);
   const envelope=0.3+0.7*Math.pow(Math.sin(Math.PI*(0.07+0.86*x)),0.65);
   const texture=0.24+0.33*Math.abs(Math.sin(i*1.31))+
     0.28*Math.abs(Math.sin(i*0.47+1.2))+
     0.15*Math.abs(Math.sin(i*2.29+0.8));
   return Math.round(6+31*Math.min(1,envelope*texture));
  });
  const bars=heights.map(height=>{
   const span=document.createElement('span');
   span.className='q-wave-bar';
   span.style.height=height+'px';
   track.append(span);
   return span;
  });
  let lastActive=-1;
  const updateWave=()=>{
   const value=Number(seek.value);
   const progress=Number.isFinite(value)?Math.min(100,Math.max(0,value)):0;
   const active=Math.floor(progress/100*COUNT);
   if(active!==lastActive){
    bars.forEach((bar,i)=>bar.classList.toggle('is-played',i<active));
    lastActive=active;
   }
   track.dataset.progress=String(Math.round(progress));
   track.classList.toggle('is-disabled',seek.disabled);
  };
  const progressObserver=new MutationObserver(updateWave);
  progressObserver.observe(seek,{attributes:true,attributeFilter:['style','disabled','value']});
  seek.addEventListener('input',updateWave);
  seek.addEventListener('change',updateWave);
  $('qAudio')?.addEventListener('timeupdate',updateWave);
  $('qAudio')?.addEventListener('loadedmetadata',updateWave);
  updateWave();
 });
})();
