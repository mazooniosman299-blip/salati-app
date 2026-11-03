/* Salati Mushaf Book Reader — independent Quran page view, adapted from
 * Mushaf Companion (MIT, Copyright (c) 2026 Mushaf Companion contributors):
 * https://github.com/abda-dc/mushaf-companion
 * License notice: dist/quran/SOURCES.txt and MIT notice in this file.
 *
 * Layout: verified local 604-page Madani word/line map, originally indexed
 * by ouryhamdalaye/madinah-mushaf-json (CC BY-SA 4.0); immutable Quran text
 * is always from dist/quran/data.json (Tanzil). Never use page JPG or fetched
 * scripture, and never synthesize glyphs or claim pixel-perfect QCF V2.
 *
 * UI architecture is a complete independent page component, not an overlay
 * over the legacy paragraph typesetter. Audio, preferences and other tabs
 * remain with the original Salati controller.
 */
(() => {
  "use strict";
  const AR_NUMBER=new Intl.NumberFormat("ar");
  const elt=(tag,classes,text)=>{
    const node=document.createElement(tag);
    if(classes)node.className=classes;
    if(text!==undefined)node.textContent=text;
    return node;
  };
  const wordKey=(s,a)=>s+":"+a;
  const bookTitle=(reader,s)=>reader.data.surahs[s-1]?.name||"المصحف الشريف";

  function lineFromPositions(reader,row,cache,index){
    const line=elt("div","mushaf-book-line quran-madinah-line");
    line.dataset.lineIndex=String(index+1);
    line.dir="rtl";
    let currentVerse="",fragment=null;
    for(const pos of row.slice(1)){
      if(!Array.isArray(pos)||pos.length!==3)throw Error("Invalid Quran word address");
      const [s,a,w]=pos;
      const key=wordKey(s,a);
      let words=cache.get(key);
      if(!words){
        const verse=reader.surahVerses?.[s-1]?.[a-1];
        if(!verse||verse.s!==s||verse.a!==a)throw Error("Missing canonical verse "+key);
        words=reader.displayWords(verse);
        cache.set(key,words);
      }
      if(!Number.isInteger(w)||w<0||w>=words.length)throw Error("Missing canonical word "+key+" "+w);
      if(currentVerse!==key){
        fragment=elt("span","mushaf-book-verse quran-ayah-fragment");
        fragment.dataset.ayah=key;
        fragment.tabIndex=0;
        fragment.setAttribute("aria-label","الآية "+a+"، استماع");
        line.append(fragment);
        currentVerse=key;
      }
      fragment.append(document.createTextNode(words[w]+" "));
      if(w===words.length-1){
        const rosette=elt("span","mushaf-book-rosette ayah-number",AR_NUMBER.format(a));
        rosette.setAttribute("aria-label","الآية "+a);
        fragment.append(rosette);
      }
    }
    return line;
  }

  function render(reader,index){
    const lines=reader.lineLayout?.pages?.[index];
    if(!Array.isArray(lines)||!lines.length||index<0||index>603){
      return reader.makeFallbackReadingPage(index);
    }
    try{
      const canonicalPage=reader.data.pages[index];
      const first=canonicalPage[0];
      if(!first)throw Error("Missing source page");
      const pageNumber=index+1,opening=pageNumber<=2;
      const page=elt("section","quran-reading-page quran-fixed-lines mushaf-book-page");
      page.dataset.readingPage=String(pageNumber);
      page.dataset.lineCount=String(lines.length);
      page.dataset.layoutOrigin="mushaf-companion-mit-port";
      if(lines.length!==(opening?8:15)){
        page.dataset.printVariant="true";
        page.dataset.printLineCount=String(lines.length);
      }
      page.setAttribute("aria-label","صفحة المصحف "+pageNumber);
      page.dir="rtl";page.lang="ar";page.setAttribute("translate","no");
      const frameOuter=elt("div","mushaf-book-frame-outer");
      const frameInner=elt("div","mushaf-book-frame-inner");
      frameOuter.setAttribute("aria-hidden","true");frameInner.setAttribute("aria-hidden","true");
      page.append(frameOuter,frameInner);
      for(const c of ["tl","tr","bl","br"]){
        const corner=elt("span","mushaf-book-corner corner-"+c);
        corner.setAttribute("aria-hidden","true");page.append(corner);
      }
      const left=elt("span","mushaf-book-side side-left"),right=elt("span","mushaf-book-side side-right");
      left.setAttribute("aria-hidden","true");right.setAttribute("aria-hidden","true");
      page.append(left,right);

      const top=elt("div","mushaf-book-top");
      top.append(
        elt("span","mushaf-book-surah-name","سورة "+bookTitle(reader,first.s)),
        elt("span","mushaf-book-part","الجزء "+AR_NUMBER.format(first.j))
      );
      page.append(top);

      // The 15 slots are a page's structural grid, not CSS paragraph wraps.
      // Pages 1-2 have eight printed slots by the edition's design.
      const grid=elt("div","mushaf-book-grid");
      grid.style.setProperty("--book-line-count",String(Math.max(opening?8:15,lines.length)));
      const cache=new Map();
      for(let i=0;i<lines.length;i++){
        const line=lines[i];
        if(!Array.isArray(line)||line.length===0)throw Error("Empty Quran line descriptor");
        const slot=elt("div","mushaf-book-row line-slot");
        slot.dataset.line=String(i+1);
        if(line[0]==="h"){
          const name=bookTitle(reader,Number(line[1]));
          const header=elt("div","mushaf-book-chapter quran-surah-title quran-fixed-heading","سورة "+name);
          slot.append(header);
        }else if(line[0]==="b"){
          const s=Number(line[1]),v=reader.surahVerses?.[s-1]?.[0];
          if(!v||v.a!==1||s===1||s===9)throw Error("Invalid original bismillah slot");
          slot.append(elt("div","mushaf-book-basmala quran-basmala-line",v.t.trim().split(/\s+/u).slice(0,4).join(" ")));
        }else if(line[0]==="t"&&line.length>1){
          slot.append(lineFromPositions(reader,line,cache,i));
        }else throw Error("Unknown layout row type "+line[0]);
        grid.append(slot);
      }
      // Do not invent omitted verses or fabricate lines in exceptional
      // publisher pages. Empty layout slots are clearly marked and validated.
      for(let i=lines.length;i<Math.max(opening?8:15,lines.length);i++){
        const slot=elt("div","mushaf-book-row line-slot mushaf-book-unverified-slot");
        slot.dataset.line=String(i+1);slot.setAttribute("aria-hidden","true");
        grid.append(slot);
      }
      page.append(grid);
      const footer=elt("footer","mushaf-book-footer reading-page-number");
      footer.append(elt("span","mushaf-book-number",AR_NUMBER.format(pageNumber)));
      page.append(footer);
      return page;
    }catch(e){
      console.error("Salati MushafBook: verified page "+(index+1)+" cannot be rendered; original Quran view used",e);
      return reader.makeFallbackReadingPage(index);
    }
  }

  window.SalatiMushafBook={render,source:"Mushaf Companion (MIT) page view adaptation"};
})();
