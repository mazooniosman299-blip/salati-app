const assert=require('node:assert/strict'),fs=require('node:fs'),Module=require('node:module'),esbuild=require('esbuild');
const {Node,makeDocument}=require('./quran-dom.cjs');
function load(file){const m=new Module(file,module);m._compile(esbuild.buildSync({entryPoints:[file],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,file);return m.exports;}
const setup=fs.existsSync('back-navigation.js')?load('back-navigation.js').setupBackNavigation:()=>{};
const original={window:global.window,document:global.document};
try{
 const target=new EventTarget(),doc=makeDocument();let dialogs=[];doc.body=new Node(1,'body');doc.querySelectorAll=()=>dialogs;doc.addEventListener=target.addEventListener.bind(target);doc.dispatchEvent=target.dispatchEvent.bind(target);doc.activeElement=null;
 global.document=doc;global.window={innerWidth:390,innerHeight:780,addEventListener(){}};
 setup();assert.equal(typeof window.salatiHandleBack,'function','Native back must ask the web UI to dismiss open controls');assert.equal(window.salatiHandleBack(),false,'No popup means native history/exit may proceed');
 const {createPopover}=load('popover-menu.js');const anchor=new Node(1,'button');anchor.bounds={top:20,bottom:60,right:300};doc.body.append(anchor);let closed=0;
 const menu=createPopover({id:'test-menu',onClose:()=>closed++});menu.open(anchor);assert.equal(window.salatiHandleBack(),true);assert.equal(menu.isOpen,false);assert.equal(closed,1);assert(anchor.focused,'Dismissing restores trigger focus');assert.equal(window.salatiHandleBack(),false);
 menu.open(anchor);let modalClosed=0;const modal={close(){modalClosed++;dialogs=[];}};dialogs=[modal];
 assert.equal(window.salatiHandleBack(),true);assert.equal(modalClosed,1);assert(menu.isOpen,'Modal must close before a menu underneath it');assert.equal(window.salatiHandleBack(),true);assert.equal(closed,2);
 assert.equal(window.salatiHandleBack(),false);
 console.log('PASS: Android back consumes modal/popup dismissal, restores focus, respects modal priority and allows native history/exit only with no open control.');
}finally{Object.assign(global,original);}
