#!/usr/bin/env node
'use strict';
/** Compare actual generated app bundle against esbuild compilation of current upstream. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),esbuild=require('esbuild');
const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'dist/index.html'),'utf8');
const match=html.match(/<script[^>]*src="(app(?:-v[\d.]+)?\.js)(?:\?[^"]*)?"/);
assert(match,'Cannot identify executing JS from live HTML');
const output=path.join(root,'dist',match[1]);
const active=fs.readFileSync(output);
const built=esbuild.buildSync({entryPoints:[path.join(root,'app-source.js')],bundle:true,minify:true,outfile:output,write:false}).outputFiles;
assert.equal(built.length,1,'Multiple generated JS outputs require review');
assert(active.equals(Buffer.from(built[0].contents)),'Published JS generated file diverges from actual app-source.js; rebuilding discards an apparent UI fix');
assert(fs.readFileSync(path.join(root,'dist/app.js')).equals(active),'Backward-compatible generated app.js diverges from executing bundle');
for(const name of ['quran-controller.js','quran-page-audio.js','glass-navigation.js','choice-picker.js']){
 assert(fs.existsSync(path.join(root,name)),'Missing live upstream JS module '+name);
}
console.log('PASS actual JS build from upstream exactly reproduces HTML-linked bundle; SHA256 '+crypto.createHash('sha256').update(active).digest('hex'));
