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
assert(css.includes('background:#141C25'),'Quran page must have clear ink-on-glass contrast');
assert(css.includes('background:#101720'),'Qibla panel must use the reference glass charcoal');
assert(css.includes('background:#131B25'),'Surah selection rows must be distinct, not pale gray');
assert(css.includes('background:#0B1017'),'Reference player must be dark, not gray');
assert(css.includes('linear-gradient(180deg,#151B23 0%,#0C1118 74%,#080C12 100%)'),'Navigation must match user screenshot gradient');
assert(css.includes('cubic-bezier(.22,.61,.36,1)'),'Gentle motion must match user screenshot');
assert(css.includes('prefers-reduced-motion:reduce'),'Honor reduced-motion preferences');
assert(css.includes('transition:background-color 280ms'),'Switches and glass must not snap harshly');
assert.equal((css.match(/\\{/g)||[]).length,(css.match(/\}/g)||[]).length,'Balanced CSS declarations');
console.log('PASS: five requested visual repairs, correct CSS ordering, and PWA cache update.');
