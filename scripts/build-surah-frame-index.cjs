#!/usr/bin/env node
'use strict';
// Read ONLY the existing original printed PNG plates. Locate their real cyan
// surah-name plaques; fail closed rather than guessing a coordinate over Quran.
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const root=path.resolve(__dirname,'..');
const base=path.join(root,'dist/quran/printed-1441');
const index=JSON.parse(fs.readFileSync(path.join(base,'index.json'),'utf8'));
const starts=new Map();
index.pages.forEach((verses,i)=>{
 const chapters=verses.filter(v=>/^[0-9]+:1$/.test(v)).map(v=>Number(v.split(':')[0]));
 if(chapters.length)starts.set(i+1,chapters);
});
if([...starts.values()].flat().length!==114)throw Error('Expected exactly 114 surah openings');
const original=new Set([...starts.values()].flat());
if(original.size!==114||![...original].every(v=>v>=1&&v<=114))throw Error('Duplicate/missing surah start');

function readPalettePng(file){
 const input=fs.readFileSync(file);
 if(!input.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10])))throw Error('PNG signature '+file);
 let at=8,width,height,depth,type,palette=null,idats=[];
 while(at<input.length){
  const size=input.readUInt32BE(at),name=input.toString('ascii',at+4,at+8),body=input.subarray(at+8,at+8+size);
  at+=size+12;
  if(name==='IHDR'){width=body.readUInt32BE(0);height=body.readUInt32BE(4);depth=body[8];type=body[9];}
  if(name==='PLTE')palette=body;
  if(name==='IDAT')idats.push(body);
  if(name==='IEND')break;
 }
 if(depth!==8||type!==3||!palette||width<400||height<600)throw Error('Unexpected original PNG format: '+file);
 const inflated=zlib.inflateSync(Buffer.concat(idats)),colors=Array.from({length:palette.length/3},(_,n)=>{
  const r=palette[n*3],g=palette[n*3+1],b=palette[n*3+2];
  return b>=112&&b>r*1.35&&b>g*1.06&&g>r*1.14&&(b-r)>55;
 });
 const marked=[];let cursor=0,previous=Buffer.alloc(width);
 for(let y=0;y<height;y++){
  const filter=inflated[cursor++],row=Buffer.allocUnsafe(width);
  for(let x=0;x<width;x++){
   const raw=inflated[cursor++],left=x?row[x-1]:0,up=previous[x],upperLeft=x?previous[x-1]:0;
   let predictor=0;
   if(filter===1)predictor=left;
   else if(filter===2)predictor=up;
   else if(filter===3)predictor=(left+up)>>1;
   else if(filter===4){const p=left+up-upperLeft,a=Math.abs(p-left),b=Math.abs(p-up),c=Math.abs(p-upperLeft);predictor=a<=b&&a<=c?left:b<=c?up:upperLeft;}
   else if(filter!==0)throw Error('Unsupported PNG filter '+filter);
   row[x]=(raw+predictor)&255;
  }
  if(y%4===0){
   let cyan=0;
   for(let x=8;x<width-8;x+=12)if(colors[row[x]])cyan++;
   if(cyan>=11)marked.push(y);
  }
  previous=row;
 }
 const groups=[];
 for(const y of marked){
  const last=groups[groups.length-1];
  if(last&&y-last.end<=32){last.end=y;last.samples++;}
  else groups.push({start:y,end:y,samples:1});
 }
 const candidates=groups.filter(g=>g.end-g.start>=52&&g.samples>=14)
   // The canonical image's dark horizontal top hairline sits ABOVE the cyan plaque.
   // Cover that whole original header rule, not only its colored center;
   // otherwise a black stroke is left between Al-Falaq and An-Nas on p604.
   .map(g=>({y:Math.max(0,g.start-32),h:Math.min(height,g.end+15)-Math.max(0,g.start-32)}));
 return {width,height,candidates};
}
const pages={};let total=2;
for(const [page,chapters] of starts){
 if(page<=2)continue; // Authentic external opening lettering already handled independently.
 const data=readPalettePng(path.join(base,'pages',page+'.png'));
 if(data.candidates.length!==chapters.length){
  throw Error('SURAH FRAME BLOCK: page '+page+' expected '+chapters.join(',')+' but detected '+JSON.stringify(data.candidates));
 }
 const regions=JSON.parse(fs.readFileSync(path.join(base,'regions',page+'.json'),'utf8'));
 if(regions.width!==data.width||regions.height!==data.height)throw Error('Artwork/geometry dimensions mismatch '+page);
 pages[page]={width:data.width,height:data.height,headings:data.candidates.map((box,i)=>({
  surah:chapters[i],y:box.y,h:box.h
 }))};
 total+=chapters.length;
}
if(total!==114)throw Error('Surah heading manifest incomplete '+total);
const output={edition:'Madinah 1441, immutable original plates',reference:'user-supplied reference screenshot; only decorative overlay',count:114,opening_pages:[1,2],pages};
const target=path.join(base,'surah-title-regions.json');
fs.writeFileSync(target,JSON.stringify(output)+'\n');
console.log('PASS '+total+' original surah headings: deterministic asset-derived positions and preserved 604 PNGs');
