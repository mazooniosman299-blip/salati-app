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
