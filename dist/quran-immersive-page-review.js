/* User reference: ONE complete Mushaf page fills the reading screen.
 * Review-only opt-in; requires licensed original green image verified by the
 * existing quran-official-green-preview.js. Never crop/stretch Quran artwork.
 * Other Salati tabs, default reader, and signed production APK are unchanged.
 */
(()=>{
  const q=new URLSearchParams(location.search);
  if(q.get('mushaf-preview')!=='official-green'||q.get('layout')!=='immersive')return;
  const one=id=>document.getElementById(id);
  function openFullPage(section){
    if(one('salatiImmersivePageExit'))return;
    const image=section.querySelector('img');
    const sheet=one('qSheet'),player=one('mushafPlayerSlot'),mushaf=one('mushaf');
    if(!image||!image.naturalWidth||!sheet?.contains(section)||!sheet.contains(player)||!mushaf)return;
    const style=(node,values)=>{if(node)Object.assign(node.style,values)};
    // The single unchanged publisher print page is the viewport: no card,
    // no rounded clipping, no secondary dark panel and no cropped border.
    style(mushaf,{position:'fixed',inset:'0',width:'100vw',height:'100dvh',margin:'0',padding:'0',
      maxWidth:'none',zIndex:'100000',background:'#FFFFFF',overflow:'hidden'});
    style(sheet,{position:'fixed',inset:'0',width:'100vw',height:'100dvh',maxWidth:'none',
      display:'flex',flexDirection:'column',alignItems:'stretch',gap:'0',overflowY:'auto',
      overflowX:'hidden',margin:'0',padding:'0',border:'0',borderRadius:'0',boxShadow:'none',
      background:'#FFFFFF',scrollSnapType:'y proximity',overscrollBehavior:'contain',
      WebkitOverflowScrolling:'touch',zIndex:'100001'});
    // No toolbars from the rest of Salati compete for the screen.
    for(const node of [
      mushaf.querySelector('.mushaf-heading'),mushaf.querySelector('.mushaf-toolbar'),
      mushaf.querySelector('.mushaf-pagination'),mushaf.querySelector('.mushaf-credit'),
      one('qFollowBar'),one('qPageLabel')
    ])style(node,{display:'none'});
    style(section,{display:'flex',flex:'0 0 100dvh',width:'100vw',maxWidth:'100%',
      height:'100dvh',minHeight:'100dvh',margin:'0',padding:'0',gap:'0',border:'0',
      borderRadius:'0',boxShadow:'none',background:'#FFFFFF',
      overflow:'hidden',alignItems:'center',justifyContent:'center',
      scrollSnapAlign:'start'});
    const note=section.querySelector('p'),paging=section.querySelector('div');
    style(note,{display:'none'});style(paging,{display:'none'});
    style(image,{display:'block',width:'100vw',maxWidth:'100%',height:'100dvh',
      maxHeight:'100dvh',margin:'0',padding:'0',border:'0',borderRadius:'0',
      boxShadow:'none',objectFit:'contain',objectPosition:'center',
      background:'#FFFFFF'});
    // Reference player arrangement with the EXISTING Salati charcoal/blue/white
    // palette. Reserve its own bottom area: shrink the COMPLETE Quran leaf with
    // contain, never overlay/clip a single ayah or ornament.
    const dockHeight=108;
    const fullLeafHeight='calc(100dvh - '+dockHeight+'px - env(safe-area-inset-bottom, 0px))';
    style(sheet,{overflowY:'hidden',scrollSnapType:'none'});
    style(section,{flex:'0 0 '+fullLeafHeight,height:fullLeafHeight,minHeight:fullLeafHeight,
      maxHeight:fullLeafHeight});
    style(image,{height:'100%',maxHeight:'100%'});
    style(player,{position:'relative',inset:'auto',display:'block',flex:'0 0 auto',
      alignSelf:'stretch',width:'100%',maxWidth:'100%',height:dockHeight+'px',
      minHeight:dockHeight+'px',maxHeight:'none',margin:'0',padding:'0',
      border:'0',borderTop:'1px solid #414249',borderRadius:'0',
      background:'#18191D',boxShadow:'none',overflow:'hidden',zIndex:'auto'});
    const controls=player.querySelector('.recitation-player.reference-player');
    const caption=player.querySelector('.recitation-caption');
    const timeline=player.querySelector('.recitation-timeline');
    const transport=one('qTransport'),stop=one('qStop'),seek=one('qSeek');
    const times=player.querySelector('.recitation-times');
    style(controls,{position:'relative',display:'grid',direction:'ltr',
      gridTemplateColumns:'46px minmax(0,1fr) 36px',
      gridTemplateRows:'24px 50px',columnGap:'10px',rowGap:'3px',
      alignItems:'center',boxSizing:'border-box',width:'100%',height:'100%',
      minHeight:'0',maxHeight:'none',margin:'0',padding:'8px 12px',
      border:'0',borderRadius:'0',background:'#18191D',boxShadow:'none',
      overflow:'hidden'});
    style(caption,{gridArea:'1/1/2/4',display:'flex',direction:'rtl',
      gap:'8px',alignItems:'center',justifyContent:'flex-start',maxWidth:'100%',
      minWidth:'0',height:'24px',margin:'0',overflow:'hidden',
      textOverflow:'ellipsis',whiteSpace:'nowrap'});
    const status=one('qAudioStatus');
    style(status,{position:'absolute',left:'-10000px',width:'1px',height:'1px',
      overflow:'hidden'}); // Status remains audible to assistive technology.
    style(transport,{gridArea:'2/1/3/2',justifySelf:'center',alignSelf:'center',
      width:'44px',height:'44px',minWidth:'44px',minHeight:'44px',
      maxWidth:'44px',maxHeight:'44px',margin:'0',padding:'0',
      borderRadius:'50%'});
    style(stop,{gridArea:'2/3/3/4',justifySelf:'center',alignSelf:'center',
      width:'34px',height:'34px',minWidth:'34px',minHeight:'34px',
      maxWidth:'34px',maxHeight:'34px',padding:'0',margin:'0'});
    style(timeline,{gridArea:'2/2/3/3',display:'flex',flexDirection:'column',
      direction:'ltr',justifyContent:'center',gap:'2px',width:'100%',height:'44px',
      maxWidth:'100%',minWidth:'0',margin:'0',padding:'0',overflow:'visible'});
    style(seek,{width:'100%',height:'21px',minHeight:'21px',maxHeight:'21px',
      margin:'0',padding:'0',flex:'0 0 21px'});
    style(times,{display:'flex',direction:'ltr',justifyContent:'space-between',
      alignItems:'center',width:'100%',height:'17px',minHeight:'17px',
      margin:'0',padding:'0',whiteSpace:'nowrap'});
    // This verified PDF sample is leaf 20 = printed Hafs page 17 (Al-Baqarah).
    // Keep the genuine QuranReader / audio engine, but align its selected surah
    // with the visible Quran artwork so the player never labels it Al-Fatiha.
    // The complete-surah recording still starts from verse 1, not page 17.
    let alignmentAttempts=0;
    const alignReader=()=>{
      if(!one('salatiImmersivePageExit')&&alignmentAttempts>0)return;
      const form=one('qPageForm'),input=one('qPageNumber'),surah=one('qSurah');
      if(form&&input&&surah&&!surah.disabled){
        if(input.value!=='17'||surah.value!=='2'){
          input.value='17';
          form.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));
        }
      }else if(++alignmentAttempts<30){
        setTimeout(alignReader,150);
      }
    };
    alignReader();
    // A tap on the paper hides the dock and enlarges the ENTIRE sheet;
    // another tap restores controls. Audio continues uninterrupted.
    let dockVisible=true;
    section.addEventListener('click',()=>{
      dockVisible=!dockVisible;
      player.style.display=dockVisible?'block':'none';
      section.style.flex=dockVisible?'0 0 '+fullLeafHeight:'0 0 100dvh';
      section.style.height=dockVisible?fullLeafHeight:'100dvh';
      section.style.minHeight=dockVisible?fullLeafHeight:'100dvh';
      section.style.maxHeight=dockVisible?fullLeafHeight:'100dvh';
    });
    const exit=document.createElement('button');
    exit.id='salatiImmersivePageExit';exit.type='button';
    exit.textContent='رجوع';exit.setAttribute('aria-label','العودة إلى صلاتي');
    style(exit,{position:'fixed',zIndex:'100003',top:'max(9px, env(safe-area-inset-top))',
      left:'10px',padding:'8px 12px',background:'rgba(20,20,20,.76)',border:'0',
      borderRadius:'12px',color:'#fff',font:'600 13px sans-serif',opacity:'.35'});
    exit.addEventListener('click',()=>{
      const u=new URL(location.href);
      u.searchParams.delete('layout');u.searchParams.delete('mushaf-preview');
      location.href=u.href;
    });
    exit.addEventListener('focus',()=>{exit.style.opacity='1'});
    document.body.append(exit);
    sheet.addEventListener('click',e=>{
      if(e.target.closest('button,input,a'))return;
      exit.style.opacity=exit.style.opacity==='.35'?'1':'.35';
    });
    document.addEventListener('keydown',e=>{if(e.key==='Escape')exit.click()});
    document.body.classList.add('salati-mushaf-fullpage-review');
    sheet.scrollTop=0;
  }
  document.addEventListener('DOMContentLoaded',()=>{
    const target=one('qVerses');
    if(!target)return;
    let found=false;
    const observer=new MutationObserver(()=>{
      if(found)return;
      const section=one('qGreenOriginalReview');
      const image=section?.querySelector('img');
      if(!image)return;
      found=true;observer.disconnect();
      if(image.complete&&image.naturalWidth)openFullPage(section);
      else image.addEventListener('load',()=>openFullPage(section),{once:true});
    });
    observer.observe(target.parentElement||document.body,{childList:true,subtree:true});
    // No original authenticated green sample: never make a fake fullscreen Quran.
  },{once:true});
})();