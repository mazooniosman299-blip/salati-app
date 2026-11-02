'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {execFileSync}=require('node:child_process');
const read=p=>fs.readFileSync(p,'utf8');
const baseline=p=>execFileSync('git',['show','origin/production:'+p],{encoding:'utf8'});
const p='android/app/src/main/res/layout/prayer_widget.xml';
const xml=read(p),original=baseline(p);
const labelOriginal='<TextView android:id="@+id/widget_next_label"';
const nameOriginal='<LinearLayout android:layout_width="wrap_content" android:layout_height="wrap_content" android:orientation="horizontal" android:gravity="center" android:layoutDirection="rtl">';
const labelNew='<TextView android:layout_marginRight="14dp" android:id="@+id/widget_next_label"';
const nameNew='<LinearLayout android:layout_marginRight="14dp" android:layout_width="wrap_content" android:layout_height="wrap_content" android:orientation="horizontal" android:gravity="center" android:layoutDirection="rtl">';
assert(original.includes(labelOriginal)&&original.includes(nameOriginal));
assert(xml.includes(labelNew)&&xml.includes(nameNew));
assert.equal(xml.replace(labelNew,labelOriginal).replace(nameNew,nameOriginal),original,
 'Widget must change ONLY next-prayer label and prayer-name right margin; NEVER mosque/countdown/dates/prayers');
const html=read('dist/index.html'),oldHTML=baseline('dist/index.html');
const regionOld='<div id="qVerses" class="mushaf-verses"></div>';
const regionNew='<div id="qVerses" class="mushaf-verses" role="region" tabindex="0" aria-label="المصحف — مرّر عمودياً لقراءة الصفحات المتتابعة"></div>';
assert(html.includes(regionNew));
assert.equal(html.replace(regionNew,regionOld),oldHTML,'No other site layout changes');
assert(!/<button[^>]*(?:qPrev|qNext|qPagePrev|qPageNext|page-arrow)[^>]*>/i.test(html),
 'No arrow controls may be used for Quran pages');
const css=read('dist/salati-ui.css'),originalCSS=baseline('dist/salati-ui.css');
assert(css.startsWith(originalCSS),'Preserve all existing design and scroll layout exactly');
assert.match(css.slice(originalCSS.length),/touch-action:\s*pan-y/);
assert(!css.includes('!important'),'CSS cannot regress to old priority debt');
const controller=read('quran-controller.js');
assert.equal(controller,baseline('quran-controller.js'),'Preserve the existing Quran reader/recitation engine');
assert(controller.includes('continuousReading(){return true}'));
assert(controller.includes('className=\'reading-page-sentinel\''));
assert(controller.includes('new IntersectionObserver'));
assert(controller.includes('this.readingNext>=604'));
assert(html.indexOf('id="mushafPlayerSlot"')>html.indexOf('id="qSheet"'),
 'Original Quran-only audio player stays below the reader');
console.log('PASS: exactly TWO native widget text insets; unchanged original widget photo, countdown, six times; Quran vertical scrolling with automatic 604-page loading, no arrows.');
