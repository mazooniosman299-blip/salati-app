// Selected Madinah1441 originals; do not retype or reconstruct printed artwork.
const NS='http://www.w3.org/2000/svg';
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
  // Retain the unchanged text as the offline/error fallback. Only one active
  // set of ayah targets is present, so following/focusing never finds hidden text.
  for(const node of page.querySelectorAll('[data-ayah]')){node.removeAttribute('data-ayah');node.removeAttribute('tabindex');}
  const fallback=document.createElement('div');fallback.className='printed-text-fallback';fallback.hidden=true;fallback.append(...page.childNodes);page.append(fallback,artwork);
  const label=document.createElement('div');label.className='printed-page-index';label.textContent=new Intl.NumberFormat('ar').format(number);page.append(label);page.classList.add('original-printed-page');
  page.dispatchEvent(new CustomEvent('printedpage',{bubbles:true}));
 }catch{
  // No guessed plate or mismatched hit regions. The canonical text remains readable.
  page.dataset.printedStatus='text-fallback';
 }
}
