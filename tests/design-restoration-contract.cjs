'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs');
const css=fs.readFileSync('dist/design-restoration-v1.0.113.css','utf8');
const html=fs.readFileSync('dist/index.html','utf8');
const sw=fs.readFileSync('dist/sw.js','utf8');
assert(html.startsWith('<!doctype html>') && html.includes('</body></html>'),'Restore complete HTML; never publish placeholder');
for(const id of ['times','mushaf','qibla','dhikr','tasbih','settings','qTransport','qStop','qSeek']){
 assert(html.includes('id="'+id+'"'),'Missing functional DOM node '+id);
}
assert(html.includes('href="design-restoration-v1.0.113.css"'),'Reference layer is loaded');
assert(html.indexOf('design-restoration-v1.0.113.css')>html.indexOf('reference-layout-v1.0.109.css'),'Final CSS must win in cascade');
assert(sw.includes("salati-shell-v158")&&sw.includes('design-restoration-v1.0.113.css'),'Service worker caches current design');
for(const literal of ['--bg:#0B0E13','--card:#040509','--action-fill:#2563EB','background:#2563EB!important','background-image:linear-gradient(180deg,#12151A,#040509)']){
 assert(css.includes(literal),'Approved palette or player missing: '+literal);
}
for(const target of ['dialog.choice-sheet','dialog.voice-sheet','dialog.uniform-menu','.floating-menu','#mushaf .reference-player','#mushaf .reference-player #qTransport::before','#mushaf .reference-player #qStop:not(:disabled)']){
 assert(css.includes(target),'Missing material styling for '+target);
}
const action=css.match(/\/\* One color owner:[\s\S]*?body\.dark header>\.site-nav \.nav-icon-button,/);
assert(action && action[0].includes('background:#0B0E13!important'),'Generic enabled buttons must remain charcoal');
assert(!action[0].includes('background:#153D7A!important'),'Old broad blue-button rule must be removed');
assert(css.includes('border:0!important;outline:0!important'),'Menu frame must not be white');
assert.equal((css.match(/\{/g)||[]).length,(css.match(/\}/g)||[]).length,'Balanced CSS');
console.log('PASS: complete homepage, six tabs, vivid blue Quran playback, charcoal buttons and frameless menus');
