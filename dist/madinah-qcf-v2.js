/* Salati genuine Madinah QCF V2 typesetter (review-only).
 * Publisher original per-page glyph codes use matching per-page QCF2 fonts.
 * Source KFGQPC/QUL data in pinned manaf/KFGQPC-Madinah-Mushaf dad9cf6.
 * Font source is Quran Foundation documented QCF v2 page fonts.
 * Immutable Tanzil text and original audio/reciter state remain intact.
 */
(() => {
 "use strict";
 const fontCache=new Map(),dataCache=new Map();
 const text=(tag,cls,content)=>{
  const e=document.createElement(tag);
  if(cls)e.className=cls;
  if(content!==undefined)e.textContent=content;
  return e;
 };
 const pageKey=n=>String(n).padStart(3,"0");
 async function loadPage(n){
  if(!dataCache.has(n))dataCache.set(n,(async()=>{
   const r=await fetch("quran/qcf-v2/page-"+pageKey(n)+".json",{cache:"force-cache"});
   if(!r.ok)throw Error("Madinah QCF page "+n+" is not bundled");
   const d=await r.json();
   if(d.page!==n||d.lines?.length!==15||!d.lines.every(x=>Array.isArray(x)&&["t","h","b","_"].includes(x[0])))
    throw Error("Invalid QCF page metadata "+n);
   return d;
  })());
  return dataCache.get(n);
 }
 async function loadFont(n){
  if(!fontCache.has(n))fontCache.set(n,(async()=>{
   const family="SalatiMadinahQCF2Page"+n;
   const source='url("fonts/qcf-v2/p'+n+'.woff2") format("woff2")';
   const face=new FontFace(family,source,{display:"swap"});
   await face.load();
   document.fonts.add(face);
   return family;
  })());
  return fontCache.get(n);
 }
 function buildQcf(reader,doc,fontFamily){
  const grid=text("div","mushaf-book-grid qcf-madinah-grid");
  grid.style.setProperty("--book-line-count","15");
  const markers=new Set();
  for(let i=0;i<15;i++){
   const row=doc.lines[i],slot=text("div","mushaf-book-row line-slot qcf-madinah-slot");
   slot.dataset.line=String(i+1);
   if(row[0]==="h"){
    const name=reader.data.surahs?.[row[1]-1]?.name;
    if(!name)throw Error("QCF heading not matched with canonical surah");
    slot.append(text("div","mushaf-book-chapter quran-surah-title quran-fixed-heading","سورة "+name));
   }else if(row[0]==="b"){
    const next=doc.lines.slice(i+1).find(x=>x[0]==="t");
    const first=next?.[1]?.[0]?.[0];
    const [s]=first?.split(":").map(Number)||[];
    const verse=reader.surahVerses?.[s-1]?.[0];
    if(!verse||s===1||s===9)throw Error("Invalid original bismillah reference");
    slot.append(text("div","mushaf-book-basmala quran-basmala-line",
      verse.t.trim().split(/\s+/u).slice(0,4).join(" ")));
   }else if(row[0]==="t"){
    const line=text("div","mushaf-book-line quran-madinah-line qcf-madinah-line");
    line.dir="rtl";line.style.fontFamily='"'+fontFamily+'",serif';
    let key="",fragment=null;
    for(const [location,glyph,isMarker] of row[1]){
     const [s,a,w]=location.split(":").map(Number);
     if(!reader.surahVerses?.[s-1]?.[a-1])throw Error("Missing immutable Quran verse "+location);
     if(!glyph||![...glyph].every(ch=>ch.codePointAt(0)>=0xE000))
      throw Error("Unexpected QCF glyph address "+location);
     const newKey=s+":"+a;
     if(key!==newKey){
      fragment=text("span","mushaf-book-verse quran-ayah-fragment qcf-madinah-verse");
      fragment.dataset.ayah=newKey;fragment.tabIndex=0;
      fragment.setAttribute("aria-label","الآية "+a+"، استماع");
      fragment.title=reader.surahVerses[s-1][a-1].t;
      line.append(fragment);key=newKey;
     }
     if(isMarker){
      const marker=text("span","qcf-madinah-ayah-end",glyph);
      marker.setAttribute("aria-label","نهاية الآية "+a);
      fragment.append(marker);
      markers.add(newKey);
     }else fragment.append(document.createTextNode(glyph+" "));
    }
    slot.append(line);
   }
   grid.append(slot);
  }
  return {grid,markerCount:markers.size};
 }
 function enhance(reader,page,index){
  const n=index+1;
  if(!page?.classList?.contains("mushaf-book-page")||n<1||n>604)return;
  Promise.all([loadPage(n),loadFont(n)]).then(([doc,family])=>{
   if(!page.isConnected)return;
   const {grid}=buildQcf(reader,doc,family);
   const previous=page.querySelector(".mushaf-book-grid");
   if(!previous)return;
   previous.replaceWith(grid);
   page.dataset.qcfReady="true";
   page.dataset.layoutOrigin="kfgqpc-madinah-qcf-v2";
   page.dataset.qcfPage=String(n);
   page.style.removeProperty("--mushaf-word-size");
   requestAnimationFrame(()=>reader.fitMushafPage?.(page));
  }).catch(err=>{
   page.dataset.qcfReady="fallback";
   console.warn("Genuine QCF V2 unavailable: original full Quran stays visible",n,err);
  });
 }
 window.SalatiMadinahQCFV2={enhance};
})();
