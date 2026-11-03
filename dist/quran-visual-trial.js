/* Real Salati 604-page Quran reader: independent control wiring only.
   The scripture source is dist/quran/data.json (6236 ayahs, 604 pages).
   No photo, remote image, fake buttons, altered Quran text or alternate player. */
(() => {
 'use strict';
 const $ = id => document.getElementById(id);
 document.addEventListener('DOMContentLoaded', () => {
  const previous=$('qPrevSurah'),next=$('qNextSurah'),loop=$('qLoopSurah');
  const source=$('qSurah'),repeat=$('qRepeat'),verses=$('qVerses');
  if(!previous||!next||!loop||!source||!repeat||!verses) return;
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
  const sync=()=>{
    const enabled=!!repeat.checked;
    loop.setAttribute('aria-pressed',String(enabled));
    loop.setAttribute('title',enabled?'إلغاء التكرار / Disable repeat':'تكرار السورة / Repeat Surah');
  };
  loop.addEventListener('click',()=>{
    repeat.checked=!repeat.checked;
    repeat.dispatchEvent(new Event('change',{bubbles:true}));
    sync();
  });
  repeat.addEventListener('change',sync);sync();
  // Keep all original verse interaction and audio listeners on #qVerses.
  // On each page navigation the existing QuranReader renders real DOM verses.
  // No duplicated or hardcoded user-facing Quranic text is introduced here.
 });
})();
