import {animate} from 'motion';

// The existing tab controller remains responsible for navigation and ARIA state.
// Motion only moves the non-interactive frosted selection beneath its active button.
export function setupGlassNavigation(){
 const nav=document.querySelector('header>.site-nav');
 if(!nav||nav.querySelector('.nav-selection'))return;
 const marker=document.createElement('span');marker.className='nav-selection';marker.setAttribute('aria-hidden','true');
 nav.prepend(marker);nav.classList.add('has-glass-navigation');
 const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
 let animation,started=false;
 function update(shouldAnimate=true){
  const active=nav.querySelector('button.active');if(!active)return;
  const box=active.getBoundingClientRect(),origin=marker.offsetParent?.getBoundingClientRect()||{left:0,top:0};
  const next={left:box.left-origin.left,top:box.top-origin.top,width:box.width,height:box.height};
  animation?.stop();
  if(started&&shouldAnimate&&!reduced.matches){animation=animate(marker,next,{duration:.26,ease:[.22,1,.36,1]});}
  else{for(const [key,value] of Object.entries(next))marker.style[key]=value+'px';}
  started=true;
 }
 new MutationObserver(()=>update()).observe(nav,{attributes:true,subtree:true,attributeFilter:['class']});
 // A direction change reorders equal-sized items without firing ResizeObserver.
 new MutationObserver(()=>update(false)).observe(document.documentElement,{attributes:true,attributeFilter:['dir','lang']});
 const geometry=new ResizeObserver(()=>update(false));geometry.observe(nav);nav.querySelectorAll('button').forEach(button=>geometry.observe(button));
 window.addEventListener('resize',()=>update(false));reduced.addEventListener('change',()=>update(false));
 update(false);
 return {marker,refresh:()=>update(false)};
}
