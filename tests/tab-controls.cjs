const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const html=fs.readFileSync('dist/index.html','utf8'),source=fs.readFileSync('app-source.js','utf8');
const keys=[...html.matchAll(/data-tab="([^"]+)"/g)].map(m=>m[1]);assert.deepEqual(keys,['times','mushaf','qibla','dhikr','tasbih','settings']);
const marker="document.querySelectorAll('[data-tab]').forEach(b=>b.onclick=",handler=source.indexOf(marker),prefix=source.lastIndexOf('const tabPositions=',handler),start=prefix>=0?prefix:handler,end=source.indexOf(";$('counter').onclick",handler);assert(start>=0&&end>start);
for(const direction of ['rtl','ltr']){
 let focusedPanel=null,blurred=0,opened=0;const field={blur(){blurred++;focusedPanel=null;}},panels=keys.map(id=>({id,hidden:id!=='times',contains:e=>e===field&&focusedPanel===id})),buttons=keys.map(tab=>({dataset:{tab},attributes:{},active:tab==='times',classList:{},setAttribute(k,v){this.attributes[k]=v;}}));
 for(const b of buttons){b.classList.toggle=(k,v)=>{b.active=v;};b.classList.contains=()=>b.active;}
 const status={textContent:'stale'},window={scrollY:0,scrollTo({top,behavior}){assert.equal(behavior,'instant');this.scrollY=top;}};
 const context={window,document:{activeElement:field,documentElement:{dir:direction},querySelectorAll:q=>q==='.tab'?panels:buttons},$:id=>id==='status'?status:panels.find(p=>p.id===id),mushaf:{open(){opened++;}}};
 vm.runInNewContext(source.slice(start,end),context);
 for(const b of buttons.slice(1)){b.onclick();assert.deepEqual(panels.filter(p=>!p.hidden).map(p=>p.id),[b.dataset.tab]);assert.equal(buttons.filter(p=>p.active).length,1);assert.equal(b.attributes['aria-pressed'],'true');assert.equal(status.textContent,'');}
 assert.equal(opened,1);
 buttons[1].onclick();window.scrollY=4800;focusedPanel='mushaf';buttons[5].onclick();assert.equal(window.scrollY,0,'First settings visit must start at the top, even after reading deep into Quran');assert.equal(blurred,1,'Leaving a panel must blur its focused field');
 window.scrollY=620;buttons[1].onclick();assert.equal(window.scrollY,4800,'Return to the Quran reading scroll position');
 const count=opened;buttons[1].onclick();assert.equal(opened,count,'Active section must not reopen or jump');assert.equal(window.scrollY,4800);
 buttons[5].onclick();assert.equal(window.scrollY,620,'Restore independent settings position');
 // Opening Quran may deliberately follow the playing verse; do not override it afterwards.
 context.mushaf.open=()=>{window.scrollY=5100;};buttons[1].onclick();assert.equal(window.scrollY,5100);
}
console.log('PASS: six-section navigation, RTL/LTR, active/ARIA state, independent scroll restore, keyboard blur, repeated clicks and Quran follow priority.');
