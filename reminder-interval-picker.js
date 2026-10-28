import {createPopover} from './popover-menu.js';

// The existing select remains the source of settings and dispatches its usual change event.
let control;
export function refreshReminderIntervalPicker(){control?.refresh();}
export function setupReminderIntervalPicker(getLanguage=()=>document.documentElement.lang){
 if(control)return control;
 const select=document.getElementById('approachMinutes');
 if(!select)return null;
 const trigger=document.createElement('button');
 trigger.id='approachMinutesPickerOpen';trigger.type='button';
 trigger.setAttribute('aria-haspopup','listbox');trigger.setAttribute('aria-controls','approachMinutesOptions');trigger.setAttribute('aria-expanded','false');
 const value=document.createElement('span');
 trigger.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m7 10 5 5 5-5"/></svg>';
 trigger.prepend(value);select.hidden=true;select.after(trigger);
 const popup=createPopover({id:'approachMinutesMenu',className:'reminder-interval-menu',width:190,height:180,onClose:()=>trigger.setAttribute('aria-expanded','false')});
 const list=popup.element;list.id='approachMinutesOptions';list.setAttribute('role','listbox');
 const title=()=>getLanguage()==='ar'?'قبل الصلاة':'Before prayer';
 const options=()=>[...list.querySelectorAll('button:not(:disabled)')];
 function render(){
  list.dir=document.documentElement.dir;list.setAttribute('aria-label',title());
  const fragment=document.createDocumentFragment();
  for(const option of select.options){
   if(option.hidden)continue;
   const item=document.createElement('button');item.type='button';item.textContent=option.textContent;
   item.dataset.value=option.value;item.setAttribute('role','option');item.setAttribute('aria-selected',String(option.value===select.value));item.tabIndex=option.value===select.value?0:-1;item.disabled=option.disabled;
   item.onclick=()=>{select.value=option.value;select.dispatchEvent(new Event('change',{bubbles:true}));refresh();popup.close(true);};fragment.append(item);
  }
  list.replaceChildren(fragment);popup.reposition();
 }
 function refresh(){
  value.textContent=select.selectedOptions[0]?.textContent||'';trigger.disabled=select.disabled;trigger.setAttribute('aria-label',title()+': '+value.textContent);
  if(select.disabled&&popup.isOpen)popup.close();
  if(popup.isOpen)render();
 }
 function open(){
  if(select.disabled)return;
  render();popup.open(trigger);trigger.setAttribute('aria-expanded','true');
  (list.querySelector('[aria-selected="true"]:not(:disabled)')||options()[0])?.focus({preventScroll:true});
 }
 trigger.onclick=()=>popup.isOpen?popup.close(true):open();
 trigger.onkeydown=event=>{if(['ArrowDown','ArrowUp'].includes(event.key)){event.preventDefault();open();}};
 list.onkeydown=event=>{
  if(event.key==='Tab'){popup.close(true);return;}
  const items=options(),index=items.indexOf(document.activeElement);let next;
  if(event.key==='ArrowDown')next=(index+1)%items.length;
  else if(event.key==='ArrowUp')next=(index-1+items.length)%items.length;
  else if(event.key==='Home')next=0;
  else if(event.key==='End')next=items.length-1;
  if(next!==undefined&&items[next]){event.preventDefault();items.forEach(item=>item.tabIndex=-1);items[next].tabIndex=0;items[next].focus({preventScroll:true});}
 };
 select.addEventListener('change',refresh);
 new MutationObserver(refresh).observe(select,{childList:true,subtree:true,characterData:true,attributes:true,attributeFilter:['disabled','selected']});
 control={trigger,popup,refresh};refresh();return control;
}
