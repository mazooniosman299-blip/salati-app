#!/usr/bin/env node
'use strict';
/** Real UI preview in a review-only artifact. Never modifies production sources. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..');
const source=path.join(root,'dist'),out=path.join(root,'reports/isolated-pr-preview');
const original=fs.readFileSync(path.join(source,'index.html'));
assert(original.includes(Buffer.from('href="/downloads/salati-')),'Missing original download link');
fs.rmSync(out,{force:true,recursive:true});
fs.mkdirSync(out,{recursive:true});
fs.cpSync(source,out,{recursive:true,filter:(name)=>{
 const rel=path.relative(source,name).replace(/\\/g,'/');
 return rel!=='downloads'&&!rel.startsWith('downloads/')&&!/\.apk$/.test(name);
}});
const entry=path.join(out,'index.html');
let html=fs.readFileSync(entry,'utf8');
const replaced=html.replace(/href="\/downloads\/salati-[^"]+\.apk"/g,'href="#" data-preview-only-no-apk="true" aria-disabled="true"');
assert.notEqual(replaced,html,'No production APK download link disabled');
html=replaced.replace(/<head>/i,'<head><meta name="robots" content="noindex,nofollow,noarchive">');
html=html.replace(/<body([^>]*)>/i,'<body$1><div role="status" id="salati-preview-notice" style="position:relative;z-index:999;background:#161b20;color:#fff;text-align:center;padding:8px;font:700 13px sans-serif">معاينة فقط — غير منشورة / REVIEW ONLY — NOT PRODUCTION</div>');
fs.writeFileSync(entry,html);
fs.writeFileSync(path.join(out,'_headers'),'/*\n  X-Robots-Tag: noindex, nofollow, noarchive\n  Cache-Control: no-store\n');
fs.writeFileSync(path.join(out,'PREVIEW_README.txt'),'SALATI REVIEW ONLY. This local UI review artifact is NOT official Cloudflare production or a signed Android release. Run python3 -m http.server 8080 --directory . inside this folder. No APK is bundled. Review original image parity and actual app interaction before any public release.\n');
assert(fs.readFileSync(path.join(source,'index.html')).equals(original),'Review preview altered original app source');
console.log('PASS independent Salati static review: no APK, no official release mutation, noindex, explicit preview label');
