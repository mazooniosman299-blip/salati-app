const assert=require('node:assert/strict'),fs=require('node:fs');
const css=fs.readFileSync('dist/design-restoration-v1.0.110.css','utf8');
const html=fs.readFileSync('dist/index.html','utf8'),sw=fs.readFileSync('dist/sw.js','utf8');
const marker='design-restoration-v1.0.110.css';
assert(html.includes('<link rel="stylesheet" href="'+marker+'">'),'Restored CSS must be loaded by main app');
assert(html.indexOf(marker)>html.indexOf('reference-layout-v1.0.109.css'),'Restored CSS must override legacy charcoal styles');
assert(sw.includes("'./"+marker+"'"),'New PWA cache must include restored CSS');
assert(sw.includes("salati-shell-v147"),'Old cached CSS must be invalidated');
for(const selector of ['.prayer-switches input[type=checkbox]:checked','#fajrAnnouncementToggle','.announcement-settings input.compact-switch:checked','#audioEnable[aria-checked="true"]','.quran-play-options input[type=checkbox]:checked','#mushaf .quran-reading-page','#mushaf .reference-player','#qibla .qibla-card .compass','dialog.choice-sheet','.choice-option']) {
 assert(css.includes(selector),'Missing restoration target: '+selector);
}
assert(css.includes('#2368C4'),'Activated switch must be blue');
assert(css.includes('#1A232D'),'Quran reading page must separate from near-black body');
assert(css.includes('#171F28'),'Qibla panel must be legible');
assert(css.includes('#202933'),'Surah selection rows must be distinct');
assert.equal((css.match(/\{/g)||[]).length,(css.match(/\}/g)||[]).length,'Balanced CSS declarations');
console.log('PASS: five requested visual repairs, correct CSS ordering, and PWA cache update.');
