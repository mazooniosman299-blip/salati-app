'use strict';
/** Modern mobile regression guard: no assertions against historical stylesheets. */
const assert=require('node:assert/strict'),fs=require('node:fs');
const read=p=>fs.readFileSync(p,'utf8');
const html=read('dist/index.html'),css=read('dist/salati-ui.css');
const quran=read('quran-controller.js'),clean=read('dist/quran-mushaf-markers-20261101.js');
const app=read('app-source.js');
assert(html.includes('href="salati-ui.css"'),'Mobile design must use active canonical stylesheet');
assert(css.includes('@layer salati-priority'),'Current live layer missing');
assert(/overflow-y:\s*auto\s*;/.test(css),'Mobile overflow handling missing from loaded CSS');
// Quranic Unicode stop/orthographic marks must NEVER be stripped from the
// reader. Legacy assertions demanded the opposite and were unsafe.
assert(!clean.includes('node.nodeValue.replace('),'Quranic verse letters/marks must not be deleted');
assert(quran.includes("makeReadingPage(index)"),'Live reader must remain present');
assert(quran.includes("quran/line-layout.json"),'Verified local Madani line map must remain attached');
assert(quran.includes("quran-madinah-line"),'Rendering should use verified line boundaries');
assert(!html.includes('id="headingValue"')&&!app.includes('headingValue'),'Retired heading must remain absent');
assert(html.includes('<div class="compass-actions"><button id="compassEnable"'),'Qibla button must remain live');
assert(quran.includes('async enterAtSurahStart()')&&!quran.includes('this.readingStart=0;this.readingNext=0;'),'Reopening Quran must retain saved reading position');
assert(app.includes('mushaf.enterAtSurahStart()'),'Navigation retains Quran reset');
assert(css.includes('--mobile-nav-height') && css.includes('header>.site-nav'),'Live mobile navigation layout tokens must remain; spatial nonoverlap is validated in real Chromium');
assert(css.includes('border-radius:24px'),'Active selected prayer capsule must remain rounded');
const widget=read('android/app/src/main/res/drawable/widget_prayer_active.xml');
assert(widget.includes('android:radius="100dp"')&&widget.includes('#FF3D3D3D'),'Native widget time capsule must be unchanged');
const layout=read('android/app/src/main/res/layout/prayer_widget.xml');
assert(layout.includes('widget_location" android:gravity="left" android:textAlignment="viewStart"'),'Native location remains physical-left');
assert(css.includes('#cancelPrayerAdjustments')&&css.includes('rgba(11,13,17,.94)'),'Cancel button retains matte contrast');
for(const id of ['times','mushaf','qibla','dhikr','tasbih','settings'])assert(html.includes('data-tab="'+id+'"'),'Missing active navigation tab '+id);
assert(!/!\s*important\b/.test(css),'No resurrection of 1,959 old force overrides');
console.log('PASS: native widget, Quran, Qibla, six tabs and mobile navigation audited against current app assets');
