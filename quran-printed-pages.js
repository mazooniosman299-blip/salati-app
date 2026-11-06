// Selected Madinah1441 originals; do not retype or reconstruct printed artwork.
const NS='http://www.w3.org/2000/svg';
// The banner index is derived from authentic printed pixel colors at build
// time, not guessed browser heights. Keep one request across all 604 pages.
let surahBannersPromise;
function loadSurahBanners(base){
 if(!surahBannersPromise)surahBannersPromise=fetch(base+'surah-title-regions.json')
  .then(r=>{if(!r.ok)throw Error('surah frame index');return r.json()})
  .then(registry=>{if(registry.count!==114)throw Error('incomplete surah frame index');return registry;})
  .catch(error=>{surahBannersPromise=null;throw error;});
 return surahBannersPromise;
}
function addReferenceSurahFrame(artwork,image,heading,base,height){
 if(!Number.isInteger(heading.surah)||!Number.isInteger(heading.y)||!Number.isInteger(heading.h)||
    heading.h<=0||heading.y<0||heading.y+heading.h>height)throw Error('invalid heading geometry');
 const frame=document.createElement('div');frame.className='printed-reference-surah-heading';
 frame.dataset.surahFrame=String(heading.surah);frame.setAttribute('aria-hidden','true');
 frame.style.top=(heading.y/height*100)+'%';frame.style.height=(heading.h/height*100)+'%';
 const decoration=new Image();decoration.src=base+'ornaments/user-reference-surah-frame.svg';
 decoration.alt='';decoration.className='printed-reference-surah-decoration';
 const inkWindow=document.createElement('div');inkWindow.className='printed-reference-original-ink';
 const ink=new Image();ink.src=image.src;ink.alt='';ink.decoding='async';
 ink.style.top=(-heading.y/heading.h*100)+'%';
 inkWindow.append(ink);frame.append(decoration,inkWindow);artwork.append(frame);
}
export async function enhancePrintedPage(page,index,verses){
 const number=index+1,base='quran/printed-1441/';
 try{
  const image=new Image();image.decoding='async';image.src=(globalThis.window?.SalatiNative&&number>2?'https://salati-app-ctc.pages.dev/':'')+base+'pages/'+number+'.png';
  const regionPromise=fetch(base+'regions/'+number+'.json').then(r=>{if(!r.ok)throw Error('regions');return r.json()});
  let timer;
  const decoded=Promise.race([image.decode(),new Promise((_,reject)=>{timer=setTimeout(()=>reject(Error('page timeout')),15000)})]);
  let regions;try{[regions]=await Promise.all([regionPromise,decoded])}finally{clearTimeout(timer)}
  if(regions.page!==number||regions.width!==image.naturalWidth||regions.height!==image.naturalHeight||!Array.isArray(regions.transform)||regions.transform.length!==6||!regions.transform.every(Number.isFinite))throw Error('edition');
  const canonical=new Map(verses.map(v=>[v.s+':'+v.a,v]));
  if(!Array.isArray(regions.verses)||regions.verses.length!==canonical.size||regions.verses.some(v=>!canonical.has(v.key)||typeof v.path!=='string'||!/^[MLZmlz0-9.,\s-]+$/.test(v.path)))throw Error('ayahs');
  const svg=document.createElementNS(NS,'svg'),group=document.createElementNS(NS,'g');
  svg.classList.add('printed-ayah-regions');svg.setAttribute('viewBox','0 0 '+regions.width+' '+regions.height);svg.setAttribute('aria-label','آيات الصفحة '+number);
  group.setAttribute('transform','matrix('+regions.transform.join(' ')+')');
  for(const region of regions.verses){const verse=canonical.get(region.key),path=document.createElementNS(NS,'path');path.classList.add('printed-ayah');path.dataset.ayah=region.key;path.setAttribute('d',region.path);path.setAttribute('tabindex','0');path.setAttribute('role','button');path.setAttribute('aria-pressed','false');path.setAttribute('aria-label',verse.t+'، الآية '+verse.a);group.append(path);}
  svg.append(group);image.className='printed-page-image';image.alt='صفحة '+number+' من مصحف المدينة، طبعة ١٤٤١هـ';image.width=regions.width;image.height=regions.height;image.draggable=false;
  const artwork=document.createElement('div');artwork.className='printed-page-artwork';artwork.append(image,svg);
  const starts=verses.filter(v=>v.a===1).map(v=>v.s);
  if(number>2&&starts.length){
   const registry=await loadSurahBanners(base);
   const node=registry.pages?.[number];
   if(!node||node.width!==regions.width||node.height!==regions.height||
      node.headings?.length!==starts.length||
      node.headings.some((heading,i)=>heading.surah!==starts[i]))throw Error('surah heading index mismatch');
   for(const heading of node.headings)addReferenceSurahFrame(artwork,image,heading,base,regions.height);
  }
  if(number<=2&&regions.displayViewport){
   const [x,y,w,h]=regions.displayViewport;
   if(x!==0||w!==regions.width||![y,h].every(Number.isFinite)||y<0||h<=0||y+h>regions.height)throw Error('viewport');
   // Original opening plates have large transparent margins. Shift BOTH the
   // untouched image and its exact hit layer inside one ink-safe display frame.
   artwork.classList.add('opening-printed-artwork');
   artwork.style.setProperty('--opening-ratio',w+' / '+h);
   artwork.style.setProperty('--opening-offset',(-y/h*100)+'%');
   artwork.style.setProperty('--opening-full-height',(regions.height/h*100)+'%');
  }
  // Retain the unchanged text as the offline/error fallback. Only one active
  // set of ayah targets is present, so following/focusing never finds hidden text.
  for(const node of page.querySelectorAll('[data-ayah]')){node.removeAttribute('data-ayah');node.removeAttribute('tabindex');}
  const fallback=document.createElement('div');fallback.className='printed-text-fallback';fallback.hidden=true;fallback.append(...page.childNodes);page.append(fallback,artwork);
  if(number<=2){
   const title=document.createElement('h3');title.className='printed-opening-title';
   const calligraphy=new Image();calligraphy.src=base+'ornaments/surah-'+number+'.svg';calligraphy.alt=number===1?'سورة الفاتحة':'سورة البقرة';
   title.append(calligraphy);page.insertBefore(title,artwork);
  }
  const label=document.createElement('div');label.className='printed-page-index';label.textContent=new Intl.NumberFormat('ar').format(number);page.append(label);page.classList.add('original-printed-page');
  page.dispatchEvent(new CustomEvent('printedpage',{bubbles:true}));
 }catch{
  // No guessed plate or mismatched hit regions. The canonical text remains readable.
  page.dataset.printedStatus='text-fallback';
 }
}
