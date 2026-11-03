/* Salati / approved blue Madinah Mushaf: preview-only, 604 original printed leaves.
 * No invented Quran text, no change to the real Quran/audio controllers.
 * This renderer is inactive until verified local WebP leaves + manifest exist.
 */
(()=>{
'use strict';
const params=new URLSearchParams(location.search);
if(params.get('quran-page-preview')!=='official-blue')return;
const ROOT='quran-blue-pages/',URL_PDF='https://d1.islamhouse.com/data/ar/ih_books/chain_01/Mushaf_AlMadinah/ar_Mushaf_AlMadinah_N_B.pdf';
const EDITION='KFGQPC Hafs 1429H standard blue, printed original',$=id=>document.getElementById(id);
const hash=async bytes=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');
const valid=m=>m?.version===1&&m.edition===EDITION&&m.sourceUrl===URL_PDF&&m.riwaya==='Hafs'&&
  Number.isInteger(m.firstPdfPage)&&m.firstPdfPage>0&&/^[a-f0-9]{64}$/i.test(m.sourceSha256)&&
  m.pageCount===604&&Array.isArray(m.pages)&&m.pages.length===604&&m.pages.every((p,i)=>
   p.quranPage===i+1&&p.pdfPage===m.firstPdfPage+i&&
   p.filename==='page-'+String(i+1).padStart(4,'0')+'.webp'&&
   /^[a-f0-9]{64}$/i.test(p.sha256)&&p.bytes>1000&&p.width>300&&p.height>500);
async function install(){
 const mushaf=$('mushaf'),sheet=$('qSheet'),verses=$('qVerses'),pageField=$('qPageNumber'),form=$('qPageForm');
 if(!mushaf||!sheet||!verses||!pageField||!form||!crypto?.subtle)return;
 let m;
 try{
  const response=await fetch(ROOT+'manifest.json',{cache:'no-store'});
  if(!response.ok)throw Error('No 604-page source asset manifest');
  m=await response.json();if(!valid(m))throw Error('Incomplete or mismatched blue-printed Quran edition');
 }catch(e){console.warn('Original Salati Quran retained:',e.message);return}
 const style=document.createElement('link');style.rel='stylesheet';style.href='quran-approved-blue-pages.css';document.head.append(style);
 const figure=document.createElement('figure');figure.id='qApprovedOriginalPage';figure.hidden=true;
 figure.setAttribute('aria-label','مصحف المدينة الأزرق برواية حفص، صفحات أصلية');
 const first=new Image();first.id='qApprovedOriginalImage';first.alt='مصحف المدينة الأزرق، الصفحة الأصلية';
 const following=document.createElement('div');following.id='qApprovedFollowingPages';
 figure.append(first,following);sheet.insertBefore(figure,verses);
 let requested=0,revision=0,nextPage=0,nextBusy=false,urls=[];
 const revoke=()=>{urls.forEach(URL.revokeObjectURL.bind(URL));urls=[]};
 async function fetchLeaf(number){
  const record=m.pages[number-1];if(!record)throw Error('No page '+number);
  const r=await fetch(ROOT+record.filename,{cache:'force-cache'});
  if(!r.ok)throw Error('Original printed page not available: '+number);
  const bytes=await r.arrayBuffer();
  if(bytes.byteLength!==record.bytes||await hash(bytes)!==record.sha256)
   throw Error('Printed Quran page SHA mismatch: '+number);
  const url=URL.createObjectURL(new Blob([bytes],{type:'image/webp'}));
  const img=new Image();img.src=url;
  try{await img.decode();}catch(e){URL.revokeObjectURL(url);throw e}
  if(img.naturalWidth!==record.width||img.naturalHeight!==record.height){
   URL.revokeObjectURL(url);throw Error('Printed Quran page geometry mismatch')}
  img.alt='مصحف المدينة الأزرق الأصلي، صفحة '+number;
  img.dataset.quranPage=String(number);img.className='q-approved-following-image';
  return {url,img};
 }
 async function show(page){
  const n=Number(page);if(!Number.isInteger(n)||n<1||n>604||n===requested)return;
  requested=n;const rev=++revision;
  try{
   const {url,img}=await fetchLeaf(n);
   if(rev!==revision){URL.revokeObjectURL(url);return}
   revoke();urls.push(url);first.src=url;first.alt=img.alt;
   following.replaceChildren();nextPage=n+1;
   verses.hidden=true;verses.style.display='none';figure.hidden=false;
   mushaf.classList.add('q-original-source-ready');document.body.classList.add('q-blue-mushaf-mode');
   figure.scrollTop=0;
  }catch(e){
   if(rev!==revision)return;
   console.warn('Printed page not proven; original Quran reader retained',e.message);
   revoke();following.replaceChildren();figure.hidden=true;
   verses.hidden=false;verses.style.display='';
   mushaf.classList.remove('q-original-source-ready');document.body.classList.remove('q-blue-mushaf-mode');
   requested=0;nextPage=0;
  }
 }
 async function append(){
  if(nextBusy||nextPage>604||!nextPage||figure.hidden)return;
  nextBusy=true;const n=nextPage,rev=revision;
  try{
   const {url,img}=await fetchLeaf(n);
   if(rev!==revision){URL.revokeObjectURL(url);return}
   following.append(img);urls.push(url);nextPage=n+1;
  }catch(e){console.warn('No substitute for missing printed next page',e.message);nextPage=0}
  finally{nextBusy=false}
 }
 figure.addEventListener('scroll',()=>{
  if(figure.scrollHeight-figure.scrollTop-figure.clientHeight<figure.clientHeight*1.2)append();
 },{passive:true});
 const reciter=$('qReciter'),header=$('qApprovedReadingHeader'),settings=$('qApprovedSettings');
 if(reciter&&header&&settings){
  const button=document.createElement('button');button.id='qBlueReciterTrigger';button.type='button';
  button.setAttribute('aria-label','تغيير صوت القارئ');
  const update=()=>button.textContent='القارئ: '+(reciter.selectedOptions[0]?.textContent?.trim()||'اختر القارئ')+' ▾';
  reciter.addEventListener('change',update);update();
  button.addEventListener('click',()=>{settings.click();reciter.focus({preventScroll:true})});
  header.append(button);
  $('qApprovedReaderMenu')?.addEventListener('click',()=>document.body.classList.toggle('q-blue-reader-menu-open'));
 }
 const start=Math.min(604,Math.max(1,Number(params.get('page')||pageField.value||2)));
 let tries=0;
 const boot=setInterval(()=>{
  if($('qSurah')?.disabled||mushaf.hidden){if(++tries>150)clearInterval(boot);return}
  clearInterval(boot);pageField.value=String(start);
  form.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));show(start);
 },120);
 form.addEventListener('submit',()=>setTimeout(()=>show(pageField.value),40));
 for(const id of ['qSurah','qJuz'])$(id)?.addEventListener('change',()=>setTimeout(()=>show(pageField.value),90));
 const label=$('qPageLabel');
 if(label)new MutationObserver(()=>setTimeout(()=>show(pageField.value),70)).observe(label,{childList:true,characterData:true,subtree:true});
 window.addEventListener('pagehide',revoke,{once:true});
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install,{once:true});else install();
})();
