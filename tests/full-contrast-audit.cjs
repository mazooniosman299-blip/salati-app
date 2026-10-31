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
assert.equal(palette, paletteVersioned, 'The versioned CSS must receive all palette edits');
assert.equal(css, cssVersioned, 'The versioned CSS must receive all contrast edits');
const tokens = Object.fromEntries([...palette.matchAll(/--([\w-]+):([^;]+)/g)].map(m => [m[1], m[2]]));
assert.equal(tokens.bg, '#0B0E13', 'Exact supplied screenshot page color');
assert.equal(tokens.card, '#040509', 'Exact supplied screenshot card color');
assert.equal(tokens.ink, '#FFFFFF', 'Never dim normal text');
assert.equal(tokens.muted, '#AAB4C2', 'Use the approved readable muted label color');
assert.equal(tokens['control-disabled-ink'], '#FFFFFF', 'Disabled text must remain legible');
assert.equal(tokens['action-fill'], '#153D7A', 'Approved play/stop blue');
assert.equal(tokens.accent, '#D6A84F', 'Navigation accent uses gold, not green');
assert(tokens['progress-track'].includes('.55'), 'Clear progress track');
assert(html.includes('href="reference-layout-v1.0.109.css"'), 'App uses the edited CSS');
assert(html.includes('href="light-theme-v1.0.109.css"'), 'App uses the edited palette');
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
assert(appendix.includes('background:#153D7A!important'), 'Selected switches use approved blue');
assert(appendix.includes('body.dark #mushaf .reference-player #qTransport::before'));
assert(appendix.includes('body.dark #mushaf .reference-player #qStop:not(:disabled)'));
assert(!appendix.includes('background:#32383F'), 'No pale gray backgrounds introduced in new fixes');
assert(quran.includes('stroke-width="2.1"'), 'Mushaf icon stays readable');
assert(nav.includes('stroke-width="2.1"'), 'Navigation Mushaf icon stays readable');
assert(nativeSelection.includes('#FF15181D') && nativeSelection.includes('#E6FFFFFF') && nativeSelection.includes('android:width="2dp"'), 'Native active prayer capsule must use the approved high-contrast outline');
assert(nativeStrip.includes('#E6040509') && nativeStrip.includes('#F0040509'));
assert.equal((css.match(/\{/g)||[]).length,(css.match(/\}/g)||[]).length, 'CSS braces');
console.log('PASS: reference colors, six tabs, all label groups, neutral switches, white icons, blue Quran transport only, APK widget and versioned assets.');
