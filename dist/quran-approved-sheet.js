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
  const gear='<svg viewBox="0 0 256 256" width="25" height="25" aria-hidden="true" focusable="false"><use href="icons/navigation.svg#settings"/></svg>';
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
    // The QuranReader continues updating its original metadata node. Mirror only
    // the surah title into this compact WHITE caption; don't mutate QuranReader data.
    const titleTrack=byId('qTrack'),caption=header.querySelector('.recitation-caption');
    const middleDot=make('span','qApprovedTitleDot');middleDot.textContent='·';
    const shortSurah=make('span','qApprovedSurahTitle');
    if(caption&&titleTrack){
      caption.append(middleDot,shortSurah);
      const refreshSurah=()=>{
        shortSurah.textContent=(titleTrack.textContent||'').split('·')[0].trim();
      };
      new MutationObserver(refreshSurah).observe(titleTrack,{childList:true,characterData:true,subtree:true});
      refreshSurah();
      Object.assign(titleTrack.style,{position:'absolute',width:'1px',height:'1px',
        overflow:'hidden',clipPath:'inset(50%)',pointerEvents:'none'});
      for(const e of [middleDot,shortSurah])Object.assign(e.style,{
        display:'block',flex:'0 1 auto',minWidth:'0',margin:'0',padding:'0',
        color:'#FFFFFF',WebkitTextFillColor:'#FFFFFF',fontSize:'clamp(11px,3.1vw,15px)',
        fontWeight:'800',whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis'});
    }
    const actions=make('div','qApprovedActions');
    actions.append(speed,previous,qTransport,next,repeat);
    player.prepend(header);
    player.append(actions,panel);
    // Compatibility with prior high-specificity mobile Quran CSS. Explicit
    // component geometry wins without !important or rewriting the global theme.
    Object.assign(slot.style,{background:'#18191D',backgroundImage:'none',height:'auto',
      minHeight:'146px',maxHeight:'none',borderRadius:'28px'});
    Object.assign(player.style,{display:'flex',flexDirection:'column',background:'#18191D',
      backgroundImage:'none',width:'100%',height:'auto',minHeight:'142px',maxHeight:'none',
      gap:'8px',padding:'12px 12px 15px',border:'0',borderRadius:'28px',
      overflow:'visible',boxShadow:'none'});
    Object.assign(header.style,{display:'grid',gridTemplateColumns:'43px minmax(0,1fr) 43px',
      gridTemplateRows:'44px',alignItems:'center',gap:'5px',minHeight:'44px',
      width:'100%',direction:'ltr'});
    if(caption)Object.assign(caption.style,{gridArea:'1/2/2/3',gridColumn:'2',gridRow:'1',
      display:'flex',justifyContent:'center',alignItems:'center',minWidth:'0',maxWidth:'100%',
      width:'100%',height:'42px',overflow:'hidden',pointerEvents:'none'});
    Object.assign(close.style,{gridArea:'1/1/2/2',gridColumn:'1',gridRow:'1',
      zIndex:'3',position:'relative',justifySelf:'center'});
    Object.assign(settings.style,{gridArea:'1/3/2/4',gridColumn:'3',gridRow:'1',
      zIndex:'3',position:'relative',justifySelf:'center'});
    // Avoid legacy outlined utility buttons: original approved player uses
    // plain WHITE glyphs, only its central play button is BLUE.
    for(const control of [close,settings,speed,previous,next,repeat]){
      Object.assign(control.style,{border:'0',background:'transparent',
        backgroundImage:'none',boxShadow:'none',borderRadius:'50%',width:'42px',
        height:'42px',minWidth:'0',minHeight:'0',padding:'0',margin:'0',
        color:'#FFFFFF',WebkitTextFillColor:'#FFFFFF'});
    }
    close.style.background='#343842';
    Object.assign(actions.style,{display:'grid',
      gridTemplateColumns:'minmax(0,1fr) minmax(0,1fr) minmax(64px,1.2fr) minmax(0,1fr) minmax(0,1fr)',
      gridTemplateRows:'64px',gap:'4px',alignItems:'center',width:'100%',minHeight:'64px',direction:'ltr'});
    Object.assign(qTransport.style,{gridArea:'1/3/2/4',justifySelf:'center',
      alignSelf:'center',width:'62px',height:'62px',minWidth:'62px',minHeight:'62px',
      maxWidth:'62px',maxHeight:'62px',background:'#2563EB',
      backgroundImage:'none',borderRadius:'50%',padding:'0',margin:'0'});
    const verses=byId('qVerses');
    if(verses)Object.assign(verses.style,{paddingBottom:'240px',scrollPaddingBottom:'220px'});
    tab.append(opener);
    // Full-page reader must keep genuine Surah/Juz navigation reachable.
    // Relocate existing selects, never create a competing Quran metadata model.
    const readingHeader=make('div','qApprovedReadingHeader');
    const currentSurah=byId('qSurah')?.closest('label');
    const currentJuz=byId('qJuz')?.closest('label');
    const readerMenu=make('button','qApprovedReaderMenu','إعدادات التلاوة',gear);
    readingHeader.append(back);
    if(currentSurah)readingHeader.append(currentSurah);
    if(currentJuz)readingHeader.append(currentJuz);
    readingHeader.append(readerMenu);
    // Native original Salati gear icon, NOT a generic replacement glyph.
    // Both player gear and Quran header reuse the exact settings sprite.
    for(const button of [settings,readerMenu]){
      const svg=button.querySelector('svg');
      if(svg)Object.assign(svg.style,{display:'block',width:'25px',height:'25px',
        color:'#FFFFFF',fill:'currentColor',stroke:'none'});
    }
    tab.append(readingHeader);
    readerMenu.onclick=()=>{show();settings.click();};
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