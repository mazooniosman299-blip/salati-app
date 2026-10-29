import {choiceMatches} from './choice-picker.js';
export const LOCATION_ICON='<svg class="location-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 10c0 5-7 11-7 11S5 15 5 10a7 7 0 1 1 14 0Z"/><circle cx="12" cy="10" r="2.5"/></svg>';

export function setupLocationPicker({country,city,trigger,getLanguage,getLabel,isBusy,getStatus,onAutomatic,onCoordinates}){
 const tr=(ar,en)=>getLanguage()==='ar'?ar:en;
 const dialog=document.createElement('dialog');dialog.id='locationMenu';dialog.className='choice-sheet location-sheet';dialog.setAttribute('aria-labelledby','locationMenuTitle');
 const handle=document.createElement('div');handle.className='sheet-handle';handle.setAttribute('aria-hidden','true');
 const heading=document.createElement('div');heading.className='choice-heading';
 const title=document.createElement('h2');title.id='locationMenuTitle';
 const copy=document.createElement('div'),count=document.createElement('small');copy.append(count,title);const close=document.createElement('button');close.type='button';close.className='choice-close';close.textContent='×';heading.append(copy,close);
 const searchWrap=document.createElement('div');searchWrap.className='choice-search-wrap';
 const search=document.createElement('input');search.type='search';search.autocomplete='off';searchWrap.append(search);
 const back=document.createElement('button');back.type='button';back.className='location-back';
 const options=document.createElement('div');options.id='locationOptions';options.className='location-options';options.setAttribute('role','listbox');
 const automatic=document.createElement('button');automatic.type='button';automatic.id='locationAutomaticOption';automatic.className='choice-option location-automatic';automatic.setAttribute('role','option');automatic.setAttribute('aria-selected','false');
 const message=document.createElement('p');message.className='note';message.setAttribute('role','status');
 dialog.append(handle,heading,searchWrap,back,options,message);document.body.append(dialog);let stage='country';
 trigger.setAttribute('aria-haspopup','dialog');trigger.setAttribute('aria-controls',dialog.id);trigger.setAttribute('aria-expanded','false');
 function content(button,label,subtitle,selected=false){
  const icon=document.createElement('span');icon.className='choice-badge location-mark';icon.setAttribute('aria-hidden','true');icon.innerHTML=LOCATION_ICON;
  const text=document.createElement('span');text.className='choice-option-text';text.textContent=label;
  if(subtitle){const detail=document.createElement('small');detail.className='choice-option-detail';detail.dir='auto';detail.textContent=subtitle;text.append(detail);}
  const mark=document.createElement('span');mark.className='choice-mark';mark.setAttribute('aria-hidden','true');mark.textContent=selected?'✓':'';button.replaceChildren(icon,text,mark);
 }
 function render(){
  title.textContent=tr('الموقع','Location');close.setAttribute('aria-label',tr('إغلاق','Close'));
  content(automatic,isBusy()?tr('جارٍ تحديد الموقع…','Detecting location…'):tr('الموقع التلقائي','Automatic location'));automatic.disabled=isBusy();
  back.hidden=stage==='country';back.textContent=tr('‹ جميع الدول','‹ All countries');
  search.placeholder=stage==='country'?tr('ابحث عن موقعك…','Search locations…'):tr('ابحث داخل الدولة…','Search within this country…');search.setAttribute('aria-label',search.placeholder);
  options.setAttribute('aria-label',tr('الموقع','Location'));const fragment=document.createDocumentFragment();let found=0,places=0;
  for(const option of (stage==='country'?country:city).options){
   if(!option.value||option.hidden||stage==='city'&&!option.value.startsWith('W:')&&option.value!=='__coords__'||!choiceMatches(option,search.value))continue;
   found++;if(option.value.startsWith('W:'))places++;if(stage==='city'&&found>200)continue;
   const item=document.createElement('button');item.type='button';item.className='choice-option';item.dataset.value=option.value;item.setAttribute('role','option');item.setAttribute('aria-selected',String(option.selected));item.disabled=option.disabled;content(item,option.textContent,stage==='country'?option.dataset.subtitle:'',option.selected);
   item.onclick=()=>{
    if(stage==='country'){stage='city';search.value='';country.value=option.value;country.dispatchEvent(new Event('change',{bubbles:true}));render();search.focus();return;}
    dialog.close();if(option.value==='__coords__'){onCoordinates();return;}city.value=option.value;city.dispatchEvent(new Event('change',{bubbles:true}));refresh();
   };fragment.append(item);
  }
  options.replaceChildren(automatic,fragment);count.textContent=(found+1)+tr(' خيار',' choices');message.textContent=stage==='city'&&!search.value&&!places?getStatus():found?(stage==='city'&&found>200?tr('حدّد البحث لإظهار بقية النتائج.','Refine your search to find more results.'):''):(stage==='city'&&!search.value?getStatus():tr('لا توجد نتائج','No matches'));message.hidden=!message.textContent;
 }
 function refresh(){const label=getLabel();trigger.querySelector('.choice-value').textContent=label;trigger.setAttribute('aria-label',tr('الموقع: ','Location: ')+label);if(dialog.open)render();}
 automatic.onclick=()=>{if(isBusy())return;dialog.close();onAutomatic();};close.onclick=()=>dialog.close();
 back.onclick=()=>{stage='country';search.value='';render();search.focus();};search.oninput=render;
 trigger.onclick=()=>{stage='country';search.value='';dialog.dir=document.documentElement.dir;render();dialog.showModal();trigger.setAttribute('aria-expanded','true');if(automatic.disabled)search.focus();else automatic.focus({preventScroll:true});};
 dialog.addEventListener('close',()=>{trigger.setAttribute('aria-expanded','false');trigger.focus({preventScroll:true});});
 dialog.addEventListener('click',event=>{if(event.target===dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();}});
 dialog.addEventListener('keydown',event=>{if(event.key==='Escape'){event.preventDefault();dialog.close();return;}const items=[...options.querySelectorAll('button')].filter(item=>!item.disabled),index=items.indexOf(document.activeElement);let next;if(event.key==='ArrowDown')next=Math.min(index+1,items.length-1);else if(event.key==='ArrowUp')next=Math.max(index-1,0);else if(document.activeElement!==search&&event.key==='Home')next=0;else if(document.activeElement!==search&&event.key==='End')next=items.length-1;if(next!==undefined&&items[next]){event.preventDefault();items[next].focus();}});
 for(const select of [country,city])new MutationObserver(refresh).observe(select,{childList:true,subtree:true,attributes:true,attributeFilter:['disabled','selected']});
 refresh();return {refresh,dialog};
}
