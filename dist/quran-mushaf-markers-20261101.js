/* Quran-only visual normalization; leave verse text and recitation datasets untouched.
   Converting the existing angled brackets into Arabic-Indic numerals lets
   the original open-licensed medallion artwork surround each verse marker.
   The text remains selectable; no Quran verse strings are altered. */
(()=>{
  const root=document.getElementById('qVerses');
  if(!root)return;
  const arabicDigit=c=>/[0-9]/.test(c)?String.fromCharCode(0x660+c.charCodeAt(0)-48):c;
  function normalizeMarker(mark){
    if(mark.dataset.mushafOrnament==='1')return;
    const current=mark.textContent.trim();
    const digits=current.match(/[0-9٠-٩۰-۹]+/gu);
    if(!digits||!digits.length)return;
    const number=digits.join('').replace(/[0-9]/g,arabicDigit);
    if(number!==current)mark.textContent=number;
    mark.dataset.mushafOrnament='1';
  }
  const refresh=()=>{
    root.querySelectorAll('.ayah-number:not([data-mushaf-ornament])').forEach(normalizeMarker);
    root.querySelectorAll('.reading-page-number:not([data-mushaf-ornament])').forEach(mark=>{
      const original=mark.textContent.trim();
      const normalized=original.replace(/[0-9]/g,arabicDigit);
      if(normalized!==original)mark.textContent=normalized;
      mark.dataset.mushafOrnament='1';
    });
    // U+06DD (end-of-ayah) and U+06DE (rub el hizb) are decorative,
    // font-dependent circular symbols. In this UI the ayah number has its
    // own reliable medallion; the extra glyph can appear as a solid BLACK
    // dot with a broken/dotted ring on some Android Quran fonts.
    // Strip only these two redundant symbols from RENDERED text nodes.
    // Never modify quran/data.json, words, tajwid marks or ayah numbers.
    const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);
    const toClean=[];
    while(walker.nextNode()){
      const node=walker.currentNode;
      if(node.parentElement?.closest('.ayah-number,.reading-page-number'))continue;
      if(/[\u06DD\u06DE]/u.test(node.nodeValue||''))toClean.push(node);
    }
    for(const node of toClean)node.nodeValue=node.nodeValue.replace(/[\u06DD\u06DE]/gu,'');
  };
  new MutationObserver(refresh).observe(root,{subtree:true,childList:true});
  refresh();
})();