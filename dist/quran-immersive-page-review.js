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
    // The already approved player is directly AFTER the complete page in
    // real document flow; swipe down for controls. It cannot cover an ayah.
    style(player,{position:'relative',inset:'auto',display:'block',flex:'0 0 auto',
      alignSelf:'stretch',width:'100%',maxWidth:'100%',margin:'0',padding:'0',borderRadius:'0',
      scrollSnapAlign:'start',zIndex:'auto'});
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