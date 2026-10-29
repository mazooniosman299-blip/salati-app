// Public city/privacy pages follow the app's preference without requiring its full bundle.
(()=>{
 const system=window.matchMedia('(prefers-color-scheme: dark)');
 function refresh(){
  let dark=system.matches;
  try{const saved=JSON.parse(localStorage.getItem('salati')||'null');if(typeof saved?.dark==='boolean')dark=saved.dark;}catch{}
  document.body.classList.toggle('dark',dark);
 }
 refresh();window.addEventListener('storage',event=>{if(event.key==='salati'||event.key===null)refresh();});system.addEventListener?.('change',refresh);
})();
