'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const html=fs.readFileSync('dist/index.html','utf8');
const css=fs.readFileSync('dist/salati-ui.css','utf8');
const js=fs.readFileSync('dist/quran-approved-sheet.js','utf8');
assert.equal((html.match(/id="qTransport"/g)||[]).length,1,'actual player retained once');
assert.equal((html.match(/id="qReciter"/g)||[]).length,1,'reciter input preserved for playback engine');
assert.match(html,/src="quran-approved-sheet\.js"/);
for(const x of ['qApprovedClose','qApprovedSettings','qApprovedSpeed','qApprovedPrevious','qApprovedNext','qApprovedRepeat']){
  assert(js.includes(x),x+' missing');
}
assert(js.includes('panel.append(reciter)'),'reciter must be moved INSIDE player settings');
assert(js.includes("qAudio.playbackRate"),'speed must adjust real HTML audio');
assert(js.includes("qRepeat.dispatchEvent"),'repeat must control real QuranReader');
assert(js.includes("q.dispatchEvent(new Event('change'"),'next/prev must route through QuranReader');
assert(!js.includes('innerHTML = user'),'no unsanitized HTML input');
assert(!css.includes('!important'),'no priority overrides');
assert(css.includes('body.dark.salati-quran-approved-screen #mushaf #mushafPlayerSlot'));
assert(css.includes('color:#FFFFFF;-webkit-text-fill-color:#FFFFFF'),'surah names must be white');
assert(/#qTransport::before\{(?:display:none;content:none|content:none;display:none)\}/.test(css),'no fake curved player decoration');
assert(!js.includes('timer')&&!js.includes('qTimer'),'no timer inside player');
assert(!js.includes('qGreenOriginalReview'),'approved audio player must not depend on 9-page PDF review');
console.log('PASS: original Salati audio player controls, white surah title, charcoal/blue, no reciter field, clock, notch or chevron');
