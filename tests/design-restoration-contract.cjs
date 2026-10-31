const assert=require('node:assert/strict'),fs=require('node:fs');
const css=fs.readFileSync('dist/design-restoration-v1.0.110.css','utf8');
const html=fs.readFileSync('dist/index.html','utf8');
const sw=fs.readFileSync('dist/sw.js','utf8');
assert(html.startsWith('<!doctype html>'),'Entry must be a real HTML page, never a placeholder');
assert(html.includes('id="qFollowBar"'),'Full Quran-follow interface must be present');
assert(html.includes('href="design-restoration-v1.0.110.css"'),'Live design stylesheet must load');
assert(html.indexOf('design-restoration-v1.0.110.css')>html.indexOf('reference-layout-v1.0.109.css'),'Design stylesheet must load after reference layout');
assert(sw.includes('salati-shell-v153'),'PWA cache must be invalidated after changes');
for(const color of ['#0B0E13','#040509','#15181D','#FFFFFF'])
 assert(css.includes(color),'Missing required deep charcoal material '+color);
for(const part of ['dialog.choice-sheet','.choice-option','.qibla-card','.prayer-overview','#mushaf .reference-player','input[type=checkbox]'])
 assert(css.includes(part),'Missing design component '+part);
assert.equal((css.match(/\{/g)||[]).length,(css.match(/\}/g)||[]).length,'CSS declarations must be balanced');
console.log('PASS: complete HTML, stylesheet ordering, reference material surfaces and fresh PWA cache');
