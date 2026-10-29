const assert=require('node:assert/strict'),Module=require('node:module'),esbuild=require('esbuild');
const {Node,makeDocument}=require('./quran-dom.cjs');
function load(file){const m=new Module(file,module);m._compile(esbuild.buildSync({entryPoints:[file],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,file);return m.exports;}
const {popoverGeometry}=load('popover-menu.js'),{QuranReader,QURAN_RECITERS}=load('quran-controller.js'),{setupCompactCategory}=load('choice-picker.js');
for(const rect of [{top:20,bottom:50,right:30},{top:720,bottom:760,right:370},{top:-40,bottom:10,right:390}]){
 const box=popoverGeometry(rect,{width:390,height:780},{width:230,height:240});assert(box.left>=8);assert(box.left+box.width<=382);assert(box.top>=8);assert(box.top+box.maxHeight<=772);
}

const {choiceMatches}=load('choice-picker.js');
assert(choiceMatches({textContent:'أذكار الصباح',dataset:{}},'اذكار الصباح'));
assert(!choiceMatches({textContent:'أذكار المساء',dataset:{}},'الصباح'));
console.log('PASS: bounded popover geometry and normalized choice search. Modal selection/verse behavior is covered by tests/selection-menus.py and tests/reference-media.py.');
