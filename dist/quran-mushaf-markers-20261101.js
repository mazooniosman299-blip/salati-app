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
  };
  new MutationObserver(refresh).observe(root,{subtree:true,childList:true});
  refresh();
})();