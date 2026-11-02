/* AUTHENTIC publisher full Mushaf page renderer.
 * Never substitutes generated/reflowed text. Uses only the SHA-256 approved
 * King Fahd Complex full-page scans, with WHITE EXTERIOR MARGINS removed.
 * Until 604 authorized pages are hosted, this is an explicitly preview-only
 * mode. No fake page may be displayed for unavailable Quran pages.
 */
(()=>{
 'use strict';
 const params=new URLSearchParams(location.search);
 if(params.get('quran-page-preview')!=='official-green')return;
 const SOURCE='5c4297de1fb6b654f641eed33242408d89432cbecf8a96ff5d297cb45fea7f07';
 const ROOT='quran-green-proof/';
 const q=id=>document.getElementById(id);
 const sha256=async bytes=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),n=>n.toString(16).padStart(2,'0')).join('');
 const valid=(m)=>m?.version===1&&m.sourceSha256===SOURCE&&m.riwaya==='Hafs'&&Array.isArray(m.pages)
   &&m.pages.length>0&&m.pages.length<=604&&m.pages.every(p=>
   Number.isInteger(p.quranPage)&&p.quranPage>=1&&p.quranPage<=604&&
   Number.isInteger(p.pdfPage)&&p.pdfPage===p.quranPage+3&&
   /^page-\d{4}\.webp$/.test(p.filename)&&/^[a-f0-9]{64}$/.test(p.sha256)&&p.bytes>2000);
 function install(){
   const mushaf=q('mushaf'),sheet=q('qSheet'),verses=q('qVerses'),pageInput=q('qPageNumber');
   if(!mushaf||!sheet||!verses||!pageInput)return;
   const figure=document.createElement('figure');figure.id='qApprovedOriginalPage';figure.hidden=true;
   figure.setAttribute('aria-label','صفحة كاملة أصلية من مصحف المدينة برواية حفص');
   const img=document.createElement('img');img.id='qApprovedOriginalImage';
   img.alt='الصفحة الأصلية من مصحف المدينة دون إعادة كتابة أو تعديل';
   figure.append(img);sheet.insertBefore(figure,verses);
   let revision=0,activeUrl='',loadedPage=0,loadingPage=0;
   async function load(page,manifest){
     if(page===loadedPage||page===loadingPage)return; // no repeat fetch/flicker on qPageLabel mutations
     const record=manifest.pages.find(x=>x.quranPage===page);
     const rev=++revision;
     loadingPage=page;
     if(!record){
       loadedPage=0;loadingPage=0;
       figure.hidden=true;verses.hidden=false;verses.style.display='';
       mushaf.classList.remove('q-original-source-ready');return;
     }
     let candidate='';
     try{
       const response=await fetch(ROOT+record.filename,{cache:'force-cache'});
       if(!response.ok)throw Error('Missing original page '+page);
       const bytes=await response.arrayBuffer();
       if(bytes.byteLength!==record.bytes||!crypto?.subtle||
          await sha256(bytes)!==record.sha256)throw Error('Original Quran page integrity mismatch');
       if(rev!==revision)return;
       candidate=URL.createObjectURL(new Blob([bytes],{type:'image/webp'}));
       const decoded=new Image();
       decoded.src=candidate;
       await decoded.decode(); // do not expose blank image between page updates
       if(rev!==revision)return;
       const prior=activeUrl;
       img.src=candidate;img.alt='مصحف المدينة، صفحة '+page+' كاملة بالرسم العثماني';
       activeUrl=candidate;candidate='';
       loadedPage=page;loadingPage=0;
       verses.hidden=true;verses.style.display='none';figure.hidden=false;
       mushaf.classList.add('q-original-source-ready');
       if(prior)URL.revokeObjectURL(prior);
     }catch(error){
       if(rev!==revision)return;
       loadingPage=0;loadedPage=0;
       figure.hidden=true;verses.hidden=false;verses.style.display='';
       mushaf.classList.remove('q-original-source-ready');
       console.warn('Original Quran page unavailable. Original, verified text reader retained.',error.message);
     }finally{
       if(candidate)URL.revokeObjectURL(candidate);
     }
   }
   fetch(ROOT+'manifest.json',{cache:'no-store'})
     .then(r=>{if(!r.ok)throw Error('No signed original page manifest');return r.json()})
     .then(manifest=>{
       if(!valid(manifest)||new Set(manifest.pages.map(x=>x.quranPage)).size!==manifest.pages.length)
         throw Error('Incomplete/untrusted original page inventory');
       const requested=Number(params.get('page')||'17');
       const target=manifest.pages.some(x=>x.quranPage===requested)?requested:manifest.pages[0].quranPage;
       let ticks=0;
       const timer=setInterval(()=>{
         const surah=q('qSurah'),form=q('qPageForm');
         if(mushaf.hidden||!surah||surah.disabled||!form){if(++ticks>140)clearInterval(timer);return;}
         clearInterval(timer);
         pageInput.value=String(target);
         form.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));
         load(target,manifest);
       },120);
       const refresh=()=>setTimeout(()=>load(Number(pageInput.value),manifest),40);
       q('qPageForm')?.addEventListener('submit',refresh);
       q('qSurah')?.addEventListener('change',refresh);
       q('qJuz')?.addEventListener('change',refresh);
       // QuranReader can update the page programmatically during verse playback.
       new MutationObserver(refresh).observe(q('qPageLabel'),{childList:true,characterData:true,subtree:true});
     }).catch(err=>{
       figure.remove();
       console.warn('Publisher full-page proof unavailable; canonical text unchanged.',err.message);
     });
   window.addEventListener('pagehide',()=>{if(activeUrl)URL.revokeObjectURL(activeUrl)},{once:true});
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install,{once:true});
 else install();
})();