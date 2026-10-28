import collection from './adhkar-collection.json';

const normalize=text=>String(text).normalize('NFKD').replace(/[\u0300-\u036f\u064b-\u065f\u0670\u0640]/g,'').replace(/[أإآٱ]/g,'ا').replace(/ى/g,'ي').replace(/ة/g,'ه').toLowerCase().trim();
export function filterAdhkar(category,query){
 const words=normalize(query).split(/\s+/).filter(Boolean);
 return collection.items.filter(item=>(!category||item.categories.includes(category))&&words.every(word=>normalize([item.text,item.titleAr,item.titleEn,item.noteAr||'',item.source.label,...item.categories.map(id=>{const c=collection.categories.find(c=>c.id===id);return c.ar+' '+c.en;})].join(' ')).includes(word)));
}
export function repetitionFor(item,category){return item.repeatByCategory&&Object.hasOwn(item.repeatByCategory,category)?item.repeatByCategory[category]:item.repeat;}
const localDay=()=>{const now=new Date();return [now.getFullYear(),now.getMonth()+1,now.getDate()].join('-');};
const savedStorage=()=>{try{return globalThis.localStorage;}catch{return null;}};
const referencesFor=item=>[item.source,...(item.sources||[])].filter((s,i,list)=>list.findIndex(other=>other.url===s.url&&other.label===s.label)===i);
export class AdhkarProgress{
 constructor({storage=savedStorage(),day=localDay}={}){
  this.storage=storage;this.day=day;this.date=day();this.counts={};
  try{const saved=JSON.parse(storage?.getItem('salati-adhkar-progress')||'null');if(saved?.date===this.date&&saved.counts&&typeof saved.counts==='object'&&!Array.isArray(saved.counts))this.counts=saved.counts;}catch{}
 }
 checkDay(){const today=this.day();if(today!==this.date){this.date=today;this.counts={};}}
 key(item,category){return (category||'all')+':'+item.id;}
 limit(item,category){return repetitionFor(item,category)??1;}
 value(item,category){this.checkDay();const value=this.counts[this.key(item,category)];return Number.isInteger(value)?Math.max(0,Math.min(this.limit(item,category),value)):0;}
 save(){try{this.storage?.setItem('salati-adhkar-progress',JSON.stringify({date:this.date,counts:this.counts}));}catch{}}
 increment(item,category){const value=this.value(item,category);this.counts[this.key(item,category)]=Math.min(this.limit(item,category),value+1);this.save();return this.value(item,category);}
 reset(items,category){this.checkDay();for(const item of items)delete this.counts[this.key(item,category)];this.save();}
}

export function setupAdhkar({getLang}){
 const el=id=>document.getElementById(id),category=el('adhkarCategory'),search=el('adhkarSearch'),list=el('adhkarList'),progress=new AdhkarProgress();
 let initialCategory='morning';
 const number=value=>new Intl.NumberFormat(getLang()).format(value);
 function updateCounter(item,scope,button,reset,card){
  const value=progress.value(item,scope),target=progress.limit(item,scope),done=value>=target;
  button.textContent=done?(getLang()==='ar'?'تمّ الذكر ✓':'Completed ✓'):(getLang()==='ar'?'ذكرتُه':'Recited')+(repetitionFor(item,scope)===null?'':' · '+number(value)+' / '+number(target));
  button.disabled=done;button.setAttribute('aria-label',item[getLang()==='ar'?'titleAr':'titleEn']+' · '+button.textContent);reset.disabled=value===0;card.classList.toggle('is-complete',done);
 }
 async function copy(item,button){
  const text=item.text+'\n'+referencesFor(item).map(source=>source.label).join('؛ ');
  try{if(navigator.clipboard?.writeText)await navigator.clipboard.writeText(text);else{const area=document.createElement('textarea');area.value=text;document.body.append(area);area.select();const copied=document.execCommand('copy');area.remove();if(!copied)throw Error('copy');}button.textContent=getLang()==='ar'?'تم النسخ':'Copied';setTimeout(()=>{button.textContent=getLang()==='ar'?'نسخ':'Copy';},1500);}catch{button.textContent=getLang()==='ar'?'حدّد النص لنسخه':'Select text to copy';}
 }
 function render(){
  const ar=getLang()==='ar',chosen=initialCategory??category.value,valid=collection.categories.some(c=>c.id===chosen);initialCategory=null;
  category.replaceChildren(new Option(ar?'كل الأذكار':'All adhkar',''),...collection.categories.map(c=>new Option(ar?c.ar:c.en,c.id)));category.value=valid?chosen:'';
  search.placeholder=ar?'ابحث في الأذكار…':'Search adhkar…';
  const scope=category.value,items=filterAdhkar(scope,search.value),fragment=document.createDocumentFragment();
  el('adhkarCount').textContent=number(items.length)+' '+(ar?'ذكرًا':'adhkar');
  for(const shortcut of el('adhkarShortcuts').querySelectorAll('button'))shortcut.setAttribute('aria-pressed',String(shortcut.dataset.adhkarCategory===scope));
  for(const item of items){
   const card=document.createElement('article');card.className='adhkar-card';card.dataset.adhkar=item.id;
   const title=document.createElement('h3');title.textContent=ar?item.titleAr:item.titleEn;
   const badge=document.createElement('span');badge.className='adhkar-repeat';const repeat=repetitionFor(item,scope);badge.textContent=repeat===null?(ar?(item.repeatByCategory?'حسب المناسبة':'عند المناسبة'):(item.repeatByCategory?'By occasion':'When applicable')):(ar?'التكرار: ':'Repetitions: ')+number(repeat);
   const text=document.createElement('p');text.className='adhkar-text';text.lang='ar';text.dir='rtl';text.textContent=item.text;
   card.append(title,badge,text);
   if(item.noteAr){const note=document.createElement('p');note.className='note adhkar-note';note.lang='ar';note.dir='rtl';note.textContent=item.noteAr;card.append(note);}
   const actions=document.createElement('div');actions.className='adhkar-actions';
   const source=document.createElement('details');source.className='adhkar-source';const sourceTitle=document.createElement('summary');sourceTitle.textContent=ar?'المصادر':'References';source.append(sourceTitle);for(const reference of referencesFor(item)){const link=document.createElement('a');link.href=reference.url;link.target='_blank';link.rel='noopener noreferrer';link.textContent=reference.label;source.append(link);}
   const copyButton=document.createElement('button');copyButton.type='button';copyButton.textContent=ar?'نسخ':'Copy';copyButton.onclick=()=>copy(item,copyButton);
   const counter=document.createElement('button');counter.type='button';counter.className='adhkar-counter';
   const reset=document.createElement('button');reset.type='button';reset.className='adhkar-reset';reset.textContent='↺';reset.setAttribute('aria-label',(ar?'إعادة عدّ ':'Reset ')+(ar?item.titleAr:item.titleEn));
   counter.onclick=()=>{progress.increment(item,scope);updateCounter(item,scope,counter,reset,card);};
   reset.onclick=()=>{progress.reset([item],scope);updateCounter(item,scope,counter,reset,card);};
   updateCounter(item,scope,counter,reset,card);actions.append(copyButton,counter,reset);card.append(source,actions);fragment.append(card);
  }
  if(!items.length){const empty=document.createElement('p');empty.className='note';empty.textContent=ar?'لا توجد أذكار مطابقة للبحث.':'No adhkar match your search.';fragment.append(empty);}
  list.replaceChildren(fragment);el('adhkarReset').disabled=items.length===0;
 }
 category.onchange=render;search.oninput=render;
 for(const button of el('adhkarShortcuts').querySelectorAll('button'))button.onclick=()=>{category.value=button.dataset.adhkarCategory;search.value='';render();};
 el('adhkarReset').onclick=()=>{progress.reset(filterAdhkar(category.value,search.value),category.value);render();};
 render();return {refresh:render};
}
