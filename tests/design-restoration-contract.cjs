const assert=require('node:assert/strict'),fs=require('node:fs');
const css=fs.readFileSync('dist/design-restoration-v1.0.110.css','utf8');
const html=fs.readFileSync('dist/index.html','utf8'),sw=fs.readFileSync('dist/sw.js','utf8');
const marker='design-restoration-v1.0.110.css';
assert(html.includes('<link rel="stylesheet" href="'+marker+'">'),'Restored CSS must be loaded by main app');
assert(html.indexOf(marker)>html.indexOf('reference-layout-v1.0.109.css'),'Restored CSS must override legacy charcoal styles');
assert(sw.includes("'./"+marker+"'"),'New PWA cache must include restored CSS');
assert(sw.includes("salati-shell-v149"),'Old cached CSS must be invalidated');
for(const selector of ['.prayer-switches input[type=checkbox]:checked','#fajrAnnouncementToggle','.announcement-settings input.compact-switch:checked','#audioEnable[aria-checked="true"]','.quran-play-options input[type=checkbox]:checked','#mushaf .quran-reading-page','#mushaf .reference-player','#qibla .qibla-card .compass','dialog.choice-sheet','.choice-option']) {
 assert(css.includes(selector),'Missing restoration target: '+selector);
}
assert(css.includes('#2563EB'),'Activated switch must be blue');
assert(!css.includes('#D6A84F') && !css.includes('rgba(214,168,79') && !css.includes('#E3B85C'),'No gold is allowed in the user-approved dark reference');
assert(css.includes('background:rgba(255,255,255,.035)!important'),'Sliding selection must be neutral translucent glass');
assert(css.includes('transition:background-color 280ms'),'Transitions must remain smooth');
assert(css.includes('background:#141B23!important'),'Quran reading surface must be legible charcoal');
assert(css.includes('background:#101720'),'Qibla panel must be legible');
assert(css.includes('#202933'),'Surah selection rows must be distinct');
assert.equal((css.match(/\{/g)||[]).length,(css.match(/\}/g)||[]).length,'Balanced CSS declarations');
for(const selector of ['--salati-approved-page:#0B0E13','--salati-approved-deep:#040509','--salati-approved-card:#15181D','--salati-approved-edge:#32383F','background:#20252B!important']) assert(css.includes(selector),'Approved screenshot color lock missing: '+selector);
assert(css.indexOf("User's approved 2026-10-31 charcoal screenshot")>css.indexOf('background:#17212B'),'Approved colors must be loaded after legacy blue-gray rules');
console.log('PASS: exact approved charcoal palette lock, CSS ordering and PWA cache update.');
