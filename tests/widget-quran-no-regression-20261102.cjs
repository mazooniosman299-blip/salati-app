'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs');
const read=p=>fs.readFileSync(p,'utf8');
const xml=read('android/app/src/main/res/layout/prayer_widget.xml');
const html=read('dist/index.html');
const css=read('dist/salati-ui.css');
const js=read('quran-controller.js');
const expected='android:layout_marginRight="14dp"';
assert(xml.includes('<TextView '+expected+' android:id="@+id/widget_next_label"'),'Keep next-prayer label inset 14dp from right edge');
assert(xml.includes('<LinearLayout '+expected+' android:layout_width="wrap_content"'),'Keep prayer-name row inset 14dp from right edge');
assert.equal((xml.match(/android:layout_marginRight="14dp"/g)||[]).length,2,'Inset only those two text groups');
assert(xml.includes('@+id/widget_countdown')&&xml.includes('@+id/widget_location'),'Original countdown and location must remain');
for(const name of ['fajr','sunrise','dhuhr','asr','maghrib','isha'])assert(xml.includes('widget_'+name),'Six times remain on widget');
assert(html.includes('id="qVerses" class="mushaf-verses" role="region" tabindex="0"'),'Quran should be touch/keyboard scrollable');
assert(css.includes('touch-action: pan-y;'),'Quran touch scrolling must stay vertical');
assert(js.includes('continuousReading(){return true}'),'Original Quran continuous reading engine must remain');
assert(js.includes('new IntersectionObserver'),'Page preloading must remain');
assert(!html.includes('preview-sample-location-20261101'),'Production must not import demo geo code');
assert(!fs.existsSync('dist/preview-sample-location-20261101.js'),'Production must not ship demo code');
const hasForcedPriority=source=>/!\s*important\b/i.test(source);
assert(!hasForcedPriority(html+css),'No inline or canonical forced CSS priorities');
for(const injected of ['.test{color:red!important}','.test{color:red ! important}']){
 assert(hasForcedPriority(injected),'Forced-priority mutation escaped test');
}
console.log('PASS: two native widget 14dp insets, image/time layout, Quran pan-y, automatic pages, no preview location code');
