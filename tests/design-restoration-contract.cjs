const assert=require('node:assert/strict'),fs=require('node:fs');
const css=fs.readFileSync('dist/design-restoration-v1.0.110.css','utf8');
const html=fs.readFileSync('dist/index.html','utf8'),sw=fs.readFileSync('dist/sw.js','utf8');
const marker='design-restoration-v1.0.110.css';
assert(html.includes('<link rel="stylesheet" href="'+marker+'">'),'Restored CSS must be loaded by main app');
assert(html.indexOf(marker)>html.indexOf('reference-layout-v1.0.109.css'),'Restored CSS must override legacy charcoal styles');
assert(sw.includes("'./"+marker+"'"),'New PWA cache must include restored CSS');
assert(sw.includes("salati-shell-v150"),'Old cached CSS must be invalidated');
for(const selector of ['.prayer-switches input[type=checkbox]:checked','#fajrAnnouncementToggle','.announcement-settings input.compact-switch:checked','#audioEnable[aria-checked="true"]','.quran-play-options input[type=checkbox]:checked','#mushaf .quran-reading-page','#mushaf .reference-player','#qibla .qibla-card .compass','dialog.choice-sheet','.choice-option']) {
 assert(css.includes(selector),'Missing restoration target: '+selector);
}
assert(css.includes('#2563EB'),'Activated switch must be blue');
assert(!css.includes('#D6A84F') && !css.includes('rgba(214,168,79') && !css.includes('#E3B85C'),'No gold is allowed in the user-approved dark reference');
assert(css.includes('background:rgba(255,255,255,.035)!important'),'Sliding selection must be neutral translucent glass');
assert(css.includes('transition:background-color 280ms'),'Transitions must remain smooth');
const finalLock=css.indexOf('/* Canonical charcoal surface system');
assert(finalLock>css.indexOf('/* Exact requested reference:'),'Single canonical palette must load last');
const surfaces=css.slice(finalLock);
for(const color of ['--salati-approved-page:#0B0E13','--salati-approved-deep:#040509','--salati-approved-card:#192027','--salati-approved-sheet:#10161C','--salati-approved-row:#1C232A','--salati-approved-selected:#2E3740','--salati-approved-edge:#596774','--salati-approved-selected-edge:#A0ADBA'])
 assert(surfaces.includes(color),'Canonical material token missing: '+color);
for(const selector of ['dialog.choice-sheet','dialog.voice-sheet','.choice-option[aria-selected="true"]','#qibla .qibla-card','.prayer-overview #prayers .prayer.active','.quran-reading-page'])
 assert(surfaces.includes(selector),'Unstyled surface: '+selector);
assert(surfaces.includes('background-image:linear-gradient(180deg,#232B33 0%,#1A2027 100%)!important'),'Rows need genuine depth, not flat washed-out fill');
assert(surfaces.includes('background-image:linear-gradient(180deg,#36414C 0%,#2A333D 100%)!important'),'Selection must remain visually distinct');
assert(!surfaces.includes('background-image:none!important;\n  border-color:#424B55!important'),'Do not restore old flat option fill');
assert(css.indexOf('/* Calm, legible picker:')===-1,'Legacy competing picker palette must be removed');
assert.equal((css.match(/\{/g)||[]).length,(css.match(/\}/g)||[]).length,'Balanced CSS declarations');
console.log('PASS: one canonical charcoal palette, raised picker rows, selected states and cache refresh.');
