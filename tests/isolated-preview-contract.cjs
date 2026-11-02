#!/usr/bin/env node
'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),out=path.join(root,'reports/isolated-pr-preview');
const html=fs.readFileSync(path.join(out,'index.html'),'utf8');
const prod=fs.readFileSync(path.join(root,'dist/index.html'),'utf8');
assert(html.includes('id="salati-preview-notice"'),'Preview not clearly marked');
assert(html.includes('name="robots" content="noindex,nofollow,noarchive"'),'Preview not flagged noindex');
assert(!/href="\/downloads\/salati-[^"]+\.apk"/.test(html),'Review exposes signed-release link');
assert(prod.includes('href="/downloads/salati-'),'Original source changed');
assert(!fs.existsSync(path.join(out,'downloads')),'Release APK leaked into preview');
assert(fs.readFileSync(path.join(out,'_headers'),'utf8').includes('X-Robots-Tag: noindex'),'No noindex header');
for(const f of ['app-v1.0.109.js','salati-ui.css','quran/data.json'])assert(fs.existsSync(path.join(out,f)),'Missing real app asset '+f);
console.log('PASS no-APK live-source review ZIP; production unchanged');
