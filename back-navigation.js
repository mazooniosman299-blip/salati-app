// Native Android asks the current page before using WebView history or exiting.
export function setupBackNavigation(){
 window.salatiHandleBack=()=>{
  const dialogs=[...document.querySelectorAll('dialog[open]')];
  const focused=document.activeElement?.closest?.('dialog[open]');
  const dialog=focused||dialogs.at(-1);
  if(dialog){dialog.close();return true;}
  return !document.dispatchEvent(new Event('salati-back',{cancelable:true}));
 };
}
