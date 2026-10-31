const assert=require('node:assert/strict'),fs=require('node:fs');
const css=fs.readFileSync('dist/design-restoration-v1.0.110.css','utf8');
const html=fs.readFileSync('dist/index.html','utf8');
const sw=fs.readFileSync('dist/sw.js','utf8');
assert(html.includes('href="design-restoration-v1.0.110.css"'),'Original design owner must be loaded');
assert(html.indexOf('design-restoration-v1.0.110.css')>html.indexOf('reference-layout-v1.0.109.css'),'The reference stylesheet must load last');
assert(sw.includes('salati-shell-v153'),'Invalidate stale color assets');
for(const literal of ['--salati-page:#0B0E13','--salati-deep:#040509','--salati-card:#15181D','--salati-border:#32383F','--salati-select:#20252B'])
 assert(css.includes(literal),'Missing approved original palette '+literal);
for(const target of ['dialog.choice-sheet','.choice-option[aria-selected="true"]','#qibla .qibla-card','.prayer-overview #prayers .prayer.active','.quran-reading-page','#mushaf .reference-player'])
 assert(css.includes(target),'Missing material surface '+target);
assert(css.includes('background-image:linear-gradient(160deg,rgba(255,255,255,.025),transparent 75%)!important'),'Restore gentle original glass depth');
assert(!css.includes('#1C232A')&&!css.includes('#2E3740')&&!css.includes('#202A35'),'No new navy gray palette');
assert(!css.includes('#A0ADBA')&&!css.includes('#596774'),'No unapproved high contrast gray borders');
assert(!css.includes('/* Canonical charcoal surface system'),'No additional competing color systems');
assert.equal((css.match(/{/g)||[]).length,(css.match(/}/g)||[]).length,'Balanced CSS');
console.log('PASS: exact 2026-10-29 charcoal palette and one authoritative stylesheet');
