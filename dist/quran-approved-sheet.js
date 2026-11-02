/* Salati — approved Quran player UI. Uses the actual QuranReader/HTMLAudioElement
 * and native Android playback bridge; never replaces Quran/audio assets.
 * No chevron, notch, reader field, clock, padlock or generated Quran content.
 */
(()=>{
  'use strict';
  const byId=id=>document.getElementById(id);
  const make=(tag,id,label,html)=>{
    const e=document.createElement(tag);
    e.id=id;if(tag==='button')e.type='button';
    if(label)e.setAttribute('aria-label',label);
    if(html)e.innerHTML=html;
    return e;
  };
  const arrow='<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true"><path fill="currentColor" d="M6 5v14h2V5H6Zm13 7L9 5v14l10-7Z"/></svg>';
  const gear='<svg viewBox="0 0 24 24" width="25" height="25" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M10 2h4l1 2.4 2.4 1 2.4-1 2.8 2.8-1 2.4L22 12l-.4 2.4 1 2.4-2.8 2.8-2.4-1-2.4 1L14 22h-4l-1-2.4-2.4-1-2.4 1-2.8-2.8 1-2.4L2 12l.4-2.4-1-2.4 2.8-2.8 2.4 1 2.4-1L10 2Z"/><circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="2"/></svg>';
  const loop='<svg viewBox="0 0 24 24" width="29" height="29" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M17 2l4 4-4 4M3 11V9a3 3 0 0 1 3-3h15M7 22l-4-4 4-4m14-1v2a3 3 0 0 1-3 3H3"/></svg>';
  const cross='<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" d="M5 5l14 14M19 5L5 19"/></svg>';
  const install=()=>{
    const tab=byId('mushaf'),slot=byId('mushafPlayerSlot'),player=slot?.querySelector('.recitation-player'),
      qTransport=byId('qTransport'),qStop=byId('qStop'),select=byId('qReciter'),seek=byId('qSeek'),
      qRepeat=byId('qRepeat'),qAudio=byId('qAudio');
    if(!tab||!slot||!player||!qTransport||!qStop||!select||!seek||!qRepeat||!qAudio||
       byId('qApprovedClose'))return;
    slot.classList.add('q-approved-player');
    player.classList.add('q-approved-inner');
    const close=make('button','qApprovedClose','إخفاء مشغّل التلاوة',cross);
    const settings=make('button','qApprovedSettings','إعدادات التلاوة',gear);
    const speed=make('button','qApprovedSpeed','سرعة التلاوة');
    speed.textContent='1.0×';
    const previous=make('button','qApprovedPrevious','السورة السابقة',arrow);
    previous.querySelector('svg').style.transform='rotate(180deg)';
    const next=make('button','qApprovedNext','السورة التالية',arrow);
    const repeat=make('button','qApprovedRepeat','تكرار السورة',loop);
    const opener=make('button','qApprovedOpen','إظهار مشغّل التلاوة');
    opener.textContent='التلاوة';
    const back=make('button','qApprovedReaderBack','العودة إلى أقسام صلاتي');
    back.textContent='←';
    const panel=make('div','qApprovedSettingsPanel');
    panel.hidden=true;panel.setAttribute('role','group');panel.setAttribute('aria-label','إعدادات مشغّل القرآن');
    const panelTitle=make('strong','qApprovedOptionsTitle');
    panelTitle.textContent='إعدادات التلاوة';
    const reciter=select.closest('label');
    if(reciter)panel.append(reciter);
    const slider=seek.closest('.recitation-timeline');
    if(slider)panel.append(slider);
    const stopRow=make('div','qApprovedStopRow');stopRow.append(qStop);
    panel.prepend(panelTitle);panel.append(stopRow);
    const header=make('div','qApprovedHeader');
    header.append(close,player.querySelector('.recitation-caption'),settings);
    const actions=make('div','qApprovedActions');
    actions.append(speed,previous,qTransport,next,repeat);
    player.prepend(header);
    player.append(actions,panel);
    tab.append(opener,back);
    settings.setAttribute('aria-expanded','false');
    const show=()=>{slot.hidden=false;opener.hidden=true;slot.classList.remove('q-player-closed');};
    const hide=()=>{slot.hidden=true;opener.hidden=false;panel.hidden=true;settings.setAttribute('aria-expanded','false');};
    close.onclick=hide;opener.onclick=show;show();
    settings.onclick=()=>{panel.hidden=!panel.hidden;settings.setAttribute('aria-expanded',String(!panel.hidden));if(!panel.hidden)select.focus({preventScroll:true});};
    const speeds=[1,1.25,1.5,2];let rateIndex=0;
    const nativeAudio=typeof window.SalatiNative?.quranPlay==='function';
    if(nativeAudio){speed.disabled=true;speed.title='تغيير سرعة التلاوة غير متاح في مشغّل أندرويد الأصلي';speed.setAttribute('aria-label',speed.title);}
    speed.onclick=()=>{if(nativeAudio)return;rateIndex=(rateIndex+1)%speeds.length;
      qAudio.playbackRate=speeds[rateIndex];speed.textContent=(speeds[rateIndex]===1?'1.0':String(speeds[rateIndex]))+'×';
      speed.setAttribute('aria-label','سرعة التلاوة '+speed.textContent);};
    const changeSurah=step=>{
      const q=byId('qSurah');
      if(!q||q.disabled)return;
      const available=Array.from(q.options).filter(o=>o.value&&!o.disabled).map(o=>Number(o.value));
      const index=available.indexOf(Number(q.value));
      if(index<0||index+step<0||index+step>=available.length)return;
      q.value=String(available[index+step]);q.dispatchEvent(new Event('change',{bubbles:true}));
    };
    previous.onclick=()=>changeSurah(-1);next.onclick=()=>changeSurah(1);
    repeat.onclick=()=>{qRepeat.checked=!qRepeat.checked;qRepeat.dispatchEvent(new Event('change',{bubbles:true}));};
    const sync=()=>{repeat.setAttribute('aria-pressed',String(qRepeat.checked));repeat.dataset.active=String(qRepeat.checked);};
    qRepeat.addEventListener('change',sync);sync();
    document.addEventListener('keydown',event=>{
      if(event.key==='Escape'&&!panel.hidden){panel.hidden=true;settings.setAttribute('aria-expanded','false');settings.focus();}
    });
    const activate=()=>{if(tab.hidden){document.body.classList.remove('salati-quran-approved-screen');return;}
      document.body.classList.add('salati-quran-approved-screen');};
    new MutationObserver(activate).observe(tab,{attributes:true,attributeFilter:['hidden']});
    back.onclick=()=>{document.body.classList.remove('salati-quran-approved-screen');
      const times=document.querySelector('header>.site-nav button[data-tab="times"]');
      if(times)times.click();else tab.hidden=true;};
    activate();
    // The source Quran remains in the original live reader; full vertical scrolling
    // and its 604-page text data are preserved, including when this overlay is closed.
    window.addEventListener('pagehide',()=>{document.body.classList.remove('salati-quran-approved-screen')},{once:true});
  };
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install,{once:true});
  else install();
})();