/* Salati Mushaf numerals: cosmetic ayah medallion labels ONLY.
   Never strip Quranic Unicode marks (including U+06DF/U+06E0) or modify
   verses/words; these are significant scriptural orthographic signs. */
(()=>{
 const root=document.getElementById('qVerses');
 if(!root)return;
 const arabicDigit=c=>/[0-9]/.test(c)?String.fromCharCode(0x660+c.charCodeAt(0)-48):c;
 function normalizeMarker(mark){
  if(mark.dataset.mushafOrnament==='1')return;
  const digits=mark.textContent.trim().match(/[0-9٠-٩۰-۹]+/gu);
  if(!digits||!digits.length)return;
  const normalized=digits.join('').replace(/[0-9]/g,arabicDigit);
  if(normalized!==mark.textContent.trim())mark.textContent=normalized;
  mark.dataset.mushafOrnament='1';
 }
 const refresh=()=>{
  root.querySelectorAll('.ayah-number:not([data-mushaf-ornament]),.reading-page-number:not([data-mushaf-ornament])')
   .forEach(normalizeMarker);
 };
 new MutationObserver(refresh).observe(root,{subtree:true,childList:true});
 refresh();
})();
