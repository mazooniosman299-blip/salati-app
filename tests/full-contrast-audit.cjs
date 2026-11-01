const assert = require('node:assert/strict');
const fs = require('node:fs');
const read = p => fs.readFileSync(p, 'utf8');
const palette = read('dist/light-theme.css');
const paletteVersioned = read('dist/light-theme-v1.0.109.css');
const css = read('dist/reference-layout.css');
const cssVersioned = read('dist/reference-layout-v1.0.109.css');
const html = read('dist/index.html');
const quran = read('dist/icons/quran.svg');
const nav = read('dist/icons/navigation.svg');
const nativeSelection = read('android/app/src/main/res/drawable/widget_prayer_active.xml');
const nativeStrip = read('android/app/src/main/res/drawable/widget_glass_strip.xml');
const canonical=html.includes('href="salati-ui.css"');
if(!canonical){assert.equal(palette, paletteVersioned, 'The versioned CSS must receive all palette edits');
assert.equal(css, cssVersioned, 'The versioned CSS must receive all contrast edits');}
else assert(read('dist/salati-ui.css').includes('--bg:#0B0E13'),'Canonical CSS contains approved colors');
const tokens = Object.fromEntries([...palette.matchAll(/--([\w-]+):([^;]+)/g)].map(m => [m[1], m[2]]));
assert.equal(tokens.bg, '#0B0E13', 'Exact supplied screenshot page color');
assert.equal(tokens.card, '#040509', 'Exact supplied screenshot card color');
assert.equal(tokens.ink, '#FFFFFF', 'Never dim normal text');
assert.equal(tokens.muted, '#AAB4C2', 'Use the approved readable muted label color');
assert.equal(tokens['control-disabled-ink'], '#FFFFFF', 'Disabled text must remain legible');
assert.equal(tokens['action-fill'], '#2563EB', 'Approved play/stop blue');
assert.equal(tokens.accent, '#FFFFFF', 'Navigation accent must match the user reference white, without gold');
assert(tokens['progress-track'].includes('.55'), 'Clear progress track');
assert(canonical || html.includes('href="reference-layout-v1.0.109.css"'), 'App uses the edited CSS');
assert(canonical || html.includes('href="light-theme-v1.0.109.css"'), 'App uses the edited palette');
for (const id of ['times','mushaf','dhikr','qibla','tasbih','settings']) {
  assert(new RegExp('id="'+id+'"').test(html), 'Missing tab: '+id);
}
const appendix=css.slice(css.indexOf('/* Full interface contrast audit, 2026-10-31.'));
assert(appendix.length > 1500, 'Missing comprehensive contrast fix');
for (const id of ['.note','.eyebrow','.quran-track','.qibla-card .cardinal','.tasbih-total','.choice-option-detail','.city-directory-grid span']) {
  assert(appendix.includes(id), 'Missing legible label override '+id);
}
assert(appendix.includes('body.dark input::placeholder'), 'Placeholder must not look disabled');
assert(appendix.includes('opacity:1!important'), 'Disabled controls must not fade');
assert(appendix.includes('background:#2563EB!important'), 'Selected switches use approved blue');
assert(appendix.includes('body.dark #mushaf .reference-player #qTransport::before'));
assert(appendix.includes('body.dark #mushaf .reference-player #qStop:not(:disabled)'));
assert(!appendix.includes('background:#32383F'), 'No pale gray backgrounds introduced in new fixes');
assert(quran.includes('stroke-width="2.1"'), 'Mushaf icon stays readable');
assert(nav.includes('stroke-width="2.1"'), 'Navigation Mushaf icon stays readable');
assert(nativeSelection.includes('#FF3D3D3D') && nativeSelection.includes('#FF5D5D5D') && nativeSelection.includes('android:radius="100dp"'), 'Native upcoming time must have a short gray capsule matching approved home widget reference');
assert(nativeStrip.includes('#FF242424') && nativeStrip.includes('#FF3B3B3B') && nativeStrip.includes('android:radius="28dp"'), 'Visible outline belongs only to the six-prayer strip');
assert.equal((css.match(/\{/g)||[]).length,(css.match(/\}/g)||[]).length, 'CSS braces');
console.log('PASS: reference colors, six tabs, neutral selection without gold, blue ON switches, white icons, APK widget and versioned assets.');
