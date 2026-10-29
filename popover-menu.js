export function popoverGeometry(rect,viewport,{width=260,height=280,point}={}){
 const gap=8,availableWidth=Math.max(1,viewport.width-gap*2),menuWidth=Math.min(width,availableWidth);
 const anchorTop=Math.max(gap,Math.min(viewport.height-gap,point?.y??rect.top));
 const anchorBottom=Math.max(gap,Math.min(viewport.height-gap,point?.y??rect.bottom));
 const below=Math.max(0,viewport.height-anchorBottom-gap*2),above=Math.max(0,anchorTop-gap*2),useAbove=below<Math.min(height,180)&&above>below;
 const maxHeight=Math.max(1,Math.min(height,useAbove?above:below,viewport.height-gap*2));
 const left=Math.max(gap,Math.min((point?.x??rect.right)-menuWidth,viewport.width-menuWidth-gap));
 const top=useAbove?Math.max(gap,anchorTop-maxHeight-gap):Math.min(viewport.height-maxHeight-gap,anchorBottom+gap);
 return {left,top,width:menuWidth,maxHeight};
}

export function createPopover({id,className='',label='',width=260,height=280,matchAnchor=false,onClose=()=>{}}={}){
 const element=document.createElement('div');element.id=id;element.className='floating-menu '+className;element.hidden=true;element.setAttribute('aria-label',label);document.body.append(element);
 if(['compact-select-popover','verse-reciter-menu'].some(kind=>className.includes(kind)))return selectionSurface(element,{id,label,onClose});
 let anchor,point,opened=false;
 function reposition(){if(!opened)return;if(!anchor?.isConnected){close();return;}const viewport={width:window.innerWidth,height:window.visualViewport?.height||window.innerHeight};const box=popoverGeometry(anchor.getBoundingClientRect(),viewport,{width:matchAnchor?Math.max(width,Math.min(anchor.offsetWidth||0,360)):width,height,point});Object.assign(element.style,{left:box.left+'px',top:box.top+'px',width:box.width+'px',maxHeight:box.maxHeight+'px'});}
 function close(restoreFocus=false){if(!opened)return;opened=false;element.hidden=true;onClose();if(restoreFocus&&anchor?.isConnected)anchor.focus({preventScroll:true});}
 function open(target,options={}){anchor=target;point=options.point;opened=true;element.hidden=false;reposition();}
 document.addEventListener('salati-back',event=>{if(opened&&!event.defaultPrevented){event.preventDefault();close(true);}});
 document.addEventListener('pointerdown',event=>{if(opened&&!element.contains(event.target)&&!anchor?.contains(event.target))close();});
 document.addEventListener('keydown',event=>{if(opened&&event.key==='Escape'){event.preventDefault();close(true);}});
 document.addEventListener('scroll',event=>{if(opened&&!element.contains(event.target))close();},true);
 window.addEventListener('resize',reposition);
 return {element,open,close,reposition,get isOpen(){return opened;}};
}

// Preserve each caller's list, selected value and handlers; share only dialog presentation.
function selectionSurface(element,{id,label,onClose}){
 const dialog=document.createElement('dialog');dialog.className='choice-sheet uniform-menu';dialog.id=id+'Dialog';
 const handle=document.createElement('div');handle.className='sheet-handle';handle.setAttribute('aria-hidden','true');
 const heading=document.createElement('div');heading.className='choice-heading';
 const copy=document.createElement('div'),count=document.createElement('small'),title=document.createElement('h2');title.id=id+'Title';copy.append(count,title);
 const closeButton=document.createElement('button');closeButton.type='button';closeButton.className='choice-close';closeButton.textContent='×';heading.append(copy,closeButton);
 const wrap=document.createElement('div');wrap.className='choice-search-wrap';const search=document.createElement('input');search.type='search';search.autocomplete='off';wrap.append(search);
 dialog.setAttribute('aria-labelledby',title.id);dialog.append(handle,heading,wrap,element);document.body.append(dialog);
 let anchor,opened=false;
 const ar=()=>document.documentElement.lang==='ar';
 function refresh(){
  const embedded=element.querySelector('input[type=search]');wrap.hidden=!!embedded;
  const input=embedded||search;input.classList.add('menu-search');if(!embedded){input.placeholder=ar()?'ابحث هنا…':'Search…';input.setAttribute('aria-label',input.placeholder);}
  let visible=0;for(const button of element.querySelectorAll('button')){
   button.classList.add('choice-option');if(!button.querySelector('.choice-option-text')){
    const text=document.createElement('span');text.className='choice-option-text';text.textContent=button.textContent;
    const badge=document.createElement('span');badge.className='choice-badge';const image=document.createElement('img');image.src='icons/'+(element.classList.contains('verse-reciter-menu')?'waveform':'list-bullets')+'.svg';image.alt='';badge.append(image);
    const mark=document.createElement('span');mark.className='choice-mark';mark.setAttribute('aria-hidden','true');button.replaceChildren(badge,text,mark);
   }
   const selected=button.getAttribute('aria-checked')==='true'||button.getAttribute('aria-selected')==='true',mark=button.querySelector('.choice-mark'),check=selected?'✓':'';
   if(mark.textContent!==check)mark.textContent=check;
   if(!embedded){const query=search.value.normalize('NFKD').replace(/[\u064b-\u065f\u0670]/g,'').trim().toLowerCase(),name=button.textContent.normalize('NFKD').replace(/[\u064b-\u065f\u0670]/g,'').toLowerCase();button.hidden=!!query&&!name.includes(query);}
   if(!button.hidden)visible++;
  }
  const caption=visible+(ar()?' خيار':' choices');if(count.textContent!==caption)count.textContent=caption;
 }
 function cleanup(){if(!opened)return;opened=false;element.hidden=true;onClose();anchor?.focus?.({preventScroll:true});}
 dialog.addEventListener('close',cleanup);dialog.addEventListener('cancel',event=>{event.preventDefault();close();});closeButton.onclick=()=>close();
 dialog.addEventListener('click',event=>{if(event.target===dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)close();}});
 dialog.addEventListener('keydown',event=>{if(event.target===search&&['ArrowDown','ArrowUp'].includes(event.key)){const items=[...element.querySelectorAll('button')].filter(item=>!item.hidden&&!item.disabled);const item=event.key==='ArrowDown'?items[0]:items.at(-1);if(item){event.preventDefault();item.focus();}}});
 search.oninput=refresh;new MutationObserver(()=>{if(opened)refresh();}).observe(element,{childList:true,subtree:true,attributes:true,attributeFilter:['aria-selected','aria-checked']});
 function open(target){anchor=target;opened=true;element.hidden=false;dialog.dir=document.documentElement.dir;title.textContent=element.getAttribute('aria-label')||label;closeButton.setAttribute('aria-label',ar()?'إغلاق':'Close');search.value='';refresh();dialog.showModal();}
 function close(){if(dialog.open)dialog.close();cleanup();}
 return{element,open,close,reposition:refresh,get isOpen(){return opened;}};
}
