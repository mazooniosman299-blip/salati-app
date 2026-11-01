'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs');
const read=p=>fs.readFileSync(p,'utf8');
const html=read('dist/index.html'),css=read('dist/eight-mobile-root-fixes-20261101.css');
const quran=read('quran-controller.js'),clean=read('dist/quran-mushaf-markers-20261101.js');
const app=read('app-source.js');
assert(html.includes('href="eight-mobile-root-fixes-20261101.css"'),'New rules loaded AFTER old CSS');
for(const ch of ['06DD','06DE','06DF','06E0']){
 assert(quran.includes('\\u'+ch),'Source Quran renderer must sanitize '+ch);
 assert(clean.includes('\\u'+ch),'Cached Quran DOM repair must sanitize '+ch);
}
assert(!html.includes('id="headingValue"')&&!app.includes('headingValue'),'Remove phone-heading node and script');
assert(html.includes('<div class="compass-actions"><button id="compassEnable"'),'Qibla button must occupy former heading position');
assert(html.indexOf('<div class="compass-actions"><button id="compassEnable"')>html.indexOf('class="qibla-reading"'));
assert(!app.includes('اتجاه هاتفك'),'Never show old phone direction phrase');
assert(quran.includes('async enterAtSurahStart()')&&quran.includes('this.readingStart=0'),'Returning to Quran starts current surah from first page');
assert(app.includes("mushaf.enterAtSurahStart()"),'Tab switch resets surah viewport');
assert(quran.includes("document.addEventListener('visibilitychange'"),'App resume returns to start');
assert(css.includes('overflow-y:auto!important')&&css.includes('margin-bottom:calc(var(--mobile-nav-height'),
 'Main content must have independent viewport above nav instead of beneath nav');
assert(!css.includes('body.dark .hero{'),'Do not restyle homepage hero');
const contract=read('dist/mobile-layout-contract-20261101.css');
assert(html.includes('href="mobile-layout-contract-20261101.css"')&&html.indexOf('href="mobile-layout-contract-20261101.css"')>html.indexOf('href="eight-mobile-root-fixes-20261101.css"'));
assert(contract.includes('border-radius:24px')&&contract.includes('#2D3D56'),'Blue-slate rounded reference prayer selection must be final CSS');
const widget=read('android/app/src/main/res/drawable/widget_prayer_active.xml');
assert(widget.includes('android:radius="100dp"')&&widget.includes('#595A5C'),'Native HOME-SCREEN widget time-only capsule matches approved reference');
const layout=read('android/app/src/main/res/layout/prayer_widget.xml');
assert(layout.includes('widget_location" android:gravity="left" android:textAlignment="viewStart"'),
 'Native location text anchored at physical left');
assert(css.includes('#cancelPrayerAdjustments')&&css.includes('#FFFFFF')&&css.includes('rgba(11,13,17,.94)'),
 'Cancel must be white over a matte dark button');
assert(!css.includes('body.dark :is([role="switch"],input[type="checkbox"])'),'No override must touch on/off toggles');
assert(!css.includes('.adjust-actions,.fields,.mushaf-tools,.audio-buttons'),'Audio play/stop buttons must not get ordinary-button styling');
console.log('PASS: eight repairs have actual source, cache, widget and accessibility invariants');
