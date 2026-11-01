const assert=require('node:assert/strict'),Module=require('node:module'),esbuild=require('esbuild');
const m=new Module('download-controls',module);m._compile(esbuild.buildSync({entryPoints:['quran-download-controls.js'],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,'download-controls.cjs');
const old={document:global.document,window:global.window,setInterval:global.setInterval};
const elements=new Map();const element=id=>{if(!elements.has(id))elements.set(id,{hidden:false,disabled:false,textContent:'',showModal(){this.open=true},close(){this.open=false}});return elements.get(id)};
(async()=>{
 try{
  global.document={getElementById:element,addEventListener(){}};global.window={addEventListener(){}};let tickMs=0;global.setInterval=(fn,ms)=>{tickMs=ms;return 0};
  const qatami={id:'qatami',ar:'ناصر القطامي',en:'Nasser Al-Qatami',surahs:[1,2]},shatri={id:'shatri',ar:'الشاطري',en:'Al-Shatri',surahs:[1,2]};
  let selected=qatami,stopped=false;const calls=[];
  const offline={available:true,list:async reciter=>reciter.id==='qatami'?[{surah:1,state:'saved'}]:[],download:async(...args)=>calls.push(['download',...args]),cancel:async(...args)=>calls.push(['cancel',...args]),remove:async(...args)=>{assert(stopped,'Playback must stop before deleting a saved source');calls.push(['remove',...args]);}};
  const controls=new m.exports.QuranDownloadControls({offline,getReciter:()=>selected,getSurah:()=>1,getLang:()=>'ar',beforeRemove:()=>{stopped=true}});
  assert.equal(tickMs,15000,'Never scan Quran files every 2 seconds');
  await controls.refresh();assert.equal(controls.activeTransfers,false);assert(element('qDownloadSurah').disabled);assert(!element('qDownloadDelete').hidden);
  selected=shatri;await controls.refresh();assert(!element('qDownloadSurah').disabled);assert(element('qDownloadDelete').hidden);
  element('qDownloadAll').onclick();assert(element('qDownloadConfirm').open);assert.equal(calls.length,0,'Full download must wait for the explicit confirmation button');
  selected=qatami;element('qDownloadConfirmYes').onclick();await new Promise(resolve=>setImmediate(resolve));assert.deepEqual(calls[0],['download',shatri]);
  await element('qDownloadCancel').onclick();assert.deepEqual(calls.at(-1),['cancel',qatami]);
  await element('qDownloadDelete').onclick();assert.deepEqual(calls.at(-1),['remove',qatami,1]);
  console.log('Quran download controls: saved state follows selected reciter, full-download confirmation retains that reciter, cancel routes correctly and deletion stops playback first.');
 }finally{Object.assign(global,old);}
})().catch(error=>{console.error(error);process.exitCode=1;});
