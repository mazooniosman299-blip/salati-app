'use strict';
/** Production design contract: inspect only actual linked and executing sources. */
const assert=require('node:assert/strict'),fs=require('node:fs');
const read=p=>fs.readFileSync(p,'utf8');
const html=read('dist/index.html'),css=read('dist/salati-ui.css'),sw=read('dist/sw.js');
assert(html.startsWith('<!doctype html>') && html.includes('</body></html>'),'Complete real homepage required');
const links=[...html.matchAll(/<link\b[^>]*\brel="stylesheet"[^>]*\bhref="([^"]+)"/g)].map(m=>m[1]);
assert.deepEqual(links,['salati-ui.css'],'No legacy or city-only styles loaded on app homepage');
assert(css.startsWith('@layer salati-base,salati-priority;'),'Active stylesheet must define reviewed layers');
assert(!/!\s*important\b/i.test(css),'Canonical CSS must not silently restore forced priority');
assert(!/!\s*important\b/i.test(html),'Home CSS cannot restore inline forced priority');
assert(!/preview-sample-location-20261101/.test(html),'Never start preview location setter on signed Android');
for(const id of ['times','mushaf','qibla','dhikr','tasbih','settings','qTransport','qStop','qSeek']) {
 assert(html.includes('id="'+id+'"'),'Missing actual live DOM node '+id);
}
for(const text of ['--bg:#0B0E13','--card:#040509','--action-fill:#2563EB','#mushaf .reference-player','nav-icon-button.active','body.dark']) {
 assert(css.includes(text),'Loaded design lost required component/property: '+text);
}
assert(sw.includes("'./salati-ui.css'"),'Offline shell must cache the currently linked stylesheet');
// The old bottom-only placement was superseded by the latest scoped user request.
// Preserve actual Quran tab ownership; runtime screenshot/ayah nonoverlap is tested separately.
const start=html.indexOf('<section id="mushaf"'),end=html.indexOf('<section id="qibla"');
assert(start>=0&&end>start,'Dedicated original Mushaf section missing');
for(const id of ['qSheet','qVerses','mushafPlayerSlot','qTransport','qSeek']){
 const at=html.indexOf('id="'+id+'"');
 assert(at>start&&at<end,'Mushaf control escaped its own tab: '+id);
}
assert(!/href="[^"]*(?:light-theme|design-restoration|eight-mobile-root-fixes|mobile-layout-contract)[^"]*\.css"/.test(html));
console.log('PASS: approved charcoal design, Quran-only player and six tabs verified against active canonical stylesheet and DOM');
