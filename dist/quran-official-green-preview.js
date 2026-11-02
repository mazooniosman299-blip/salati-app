/* Authentic green Mushaf preview only. No approximation, no production activation.
 * Requires byte-verified, independently rendered samples from the publisher's PDF.
 * The selected chat reference (#5) remains UNVERIFIED against this edition.
 */
(() => {
  const params=new URLSearchParams(location.search);
  if(params.get('mushaf-preview')!=='official-green') return;
  const ROOT='quran-green-review/';
  const q=id=>document.getElementById(id);
  const md=text=>{const p=document.createElement('p');p.textContent=text;return p};
  const allowed=pages=>Array.isArray(pages)&&pages.length>0&&pages.length<=660&&
    pages.every(p=>Number.isInteger(p.pdfPage)&&p.pdfPage>0&&p.pdfPage<=700&&
      /^pdf-[0-9]{4}\.webp$/.test(p.filename)&&
      /^[a-f0-9]{64}$/.test(p.sha256)&&Number.isInteger(p.bytes)&&p.bytes>1024);
  const hex=bytes=>Array.from(new Uint8Array(bytes),x=>x.toString(16).padStart(2,'0')).join('');
  async function initialize(){
    const res=await fetch(ROOT+'manifest.json',{cache:'no-store'});
    if(!res.ok) return;
    const manifest=await res.json();
    if(manifest.edition!=='KFGQPC Hafs standard39-2 green PDF'||
       manifest.sourceSha256!=='5c4297de1fb6b654f641eed33242408d89432cbecf8a96ff5d297cb45fea7f07'||
       !allowed(manifest.pages))return;
    const sheet=q('qSheet'),verses=q('qVerses'),player=q('mushafPlayerSlot');
    if(!sheet||!verses||!player||!sheet.contains(player))return;
    const section=document.createElement('section');section.id='qGreenOriginalReview';
    section.setAttribute('aria-label','معاينة صفحات الطبعة الخضراء الأصلية');
    Object.assign(section.style,{background:'#F9F6EF',color:'#27231E',padding:'8px',display:'grid',gap:'8px'});
    const notice=md('معاينة تجريبية من PDF رسمي · لم يُثبت تطابقها مع اختيارك رقم ٥ · لم تُنشر');
    Object.assign(notice.style,{color:'#282622',fontSize:'12px',margin:'4px',textAlign:'center',lineHeight:'1.6'});
    const img=document.createElement('img');img.alt='صفحة كاملة غير مقصوصة من نسخة مجمع الملك فهد الأصلية';
    Object.assign(img.style,{width:'100%',height:'auto',display:'block',objectFit:'contain',background:'white'});
    const controls=document.createElement('div');Object.assign(controls.style,{display:'flex',gap:'8px',alignItems:'center',justifyContent:'space-around'});
    const back=document.createElement('button'),next=document.createElement('button'),label=document.createElement('span');
    back.type=next.type='button';back.textContent='السابقة';next.textContent='التالية';label.style.fontSize='12px';
    controls.append(back,label,next);
    section.append(notice,img,controls);
    // Existing audio player stays an in-flow child of #qSheet; no overlay ever.
    verses.before(section);
    const previousHidden=verses.hidden;verses.hidden=true;
    let index=0, activeUrl='', requestId=0;
    async function show(i){
      index=i;const entry=manifest.pages[index],generation=++requestId;
      back.disabled=index===0;next.disabled=index===manifest.pages.length-1;
      label.textContent='صفحة PDF '+entry.pdfPage+' — نموذج للمراجعة';
      const res=await fetch(ROOT+entry.filename,{cache:'no-store'});
      if(!res.ok)throw Error('PDF preview sample missing');
      const bytes=await res.arrayBuffer();
      if(bytes.byteLength!==entry.bytes||!crypto?.subtle)throw Error('Preview integrity unavailable');
      const digest=hex(await crypto.subtle.digest('SHA-256',bytes));
      if(digest!==entry.sha256)throw Error('Preview page differs from approved PDF render');
      if(generation!==requestId)return;
      const url=URL.createObjectURL(new Blob([bytes],{type:'image/webp'}));
      img.onload=()=>{if(activeUrl&&activeUrl!==url)URL.revokeObjectURL(activeUrl);activeUrl=url};
      img.src=url;
    }
    async function choose(i){
      try{await show(i)}catch(error){
        section.remove();verses.hidden=previousHidden;
        if(activeUrl)URL.revokeObjectURL(activeUrl);
        const status=q('qLoadStatus');if(status)status.textContent='معاينة الصفحات الأصلية غير متاحة أو غير موثقة؛ المصحف الحالي لم يتغير.';
        console.warn('Verified Quran PDF preview failed:',error.message);
      }
    }
    back.addEventListener('click',()=>choose(Math.max(0,index-1)));
    next.addEventListener('click',()=>choose(Math.min(manifest.pages.length-1,index+1)));
    choose(0);
  }
  // Delayed until the actual original Salati app DOM exists, no alternate UI.
  document.addEventListener('DOMContentLoaded',()=>initialize().catch(()=>{}),{once:true});
})();