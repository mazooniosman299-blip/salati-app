/* Salati 2026-11-03: installable review-only visual trial.
   The original interactive 604-page reader remains the fallback; no Quran JSON,
   audio engine, prayer UI, or saved preferences are rewritten.
   One third-party reference photograph is linked for visual evaluation only:
   it must NOT be treated as a page-mapped, rights-cleared Mushaf release. */
(() => {
 'use strict';
 const $=id=>document.getElementById(id);
 document.addEventListener('DOMContentLoaded',()=>{
  const mushaf=$('mushaf'),plate=$('qTrialPlate'),img=$('qTrialPlateImage'),toggle=$('qTrialSwitch');
  const previous=$('qPrevSurah'),next=$('qNextSurah'),loop=$('qLoopSurah');
  const source=$('qSurah'),repeat=$('qRepeat');
  if(!mushaf||!plate||!img||!toggle||!source||!repeat||!previous||!next||!loop)return;
  const textMode=()=>{
   mushaf.classList.remove('quran-trial-active');
   plate.hidden=true;
   toggle.textContent='معاينة شكل المصحف';
   toggle.setAttribute('aria-pressed','false');
   $('qVerses')?.removeAttribute('aria-hidden');
  };
  const plateMode=()=>{
   if(!img.complete||img.naturalWidth<100)return;
   mushaf.classList.add('quran-trial-active');
   plate.hidden=false;
   toggle.hidden=false;
   toggle.textContent='القراءة التفاعلية للآيات';
   toggle.setAttribute('aria-pressed','true');
   $('qVerses')?.setAttribute('aria-hidden','true');
  };
  img.addEventListener('load',plateMode,{once:true});
  img.addEventListener('error',()=>{textMode();toggle.hidden=true},{once:true});
  if(img.complete && img.naturalWidth>100)plateMode();
  toggle.onclick=()=>mushaf.classList.contains('quran-trial-active')?textMode():plateMode();
  const goSurah=delta=>{
   if(source.disabled||!source.options?.length)return;
   const current=Number(source.value),id=Math.max(1,Math.min(114,current+delta));
   if(id===current)return;
   textMode();source.value=String(id);
   source.dispatchEvent(new Event('change',{bubbles:true}));
  };
  previous.onclick=()=>goSurah(-1);
  next.onclick=()=>goSurah(1);
  const sync=()=>{const checked=!!repeat.checked;loop.setAttribute('aria-pressed',String(checked));};
  loop.onclick=()=>{repeat.checked=!repeat.checked;repeat.dispatchEvent(new Event('change',{bubbles:true}));sync()};
  repeat.addEventListener('change',sync);
  sync();
  // The trial image is a single design reference, not all 604 numbered pages.
  // When user selects another Surah/Juz, show the faithful interactive text.
  ['qSurah','qJuz'].forEach(id=>$(id)?.addEventListener('change',textMode));
 });
})();
