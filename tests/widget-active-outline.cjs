const assert=require('node:assert/strict');
const fs=require('node:fs');
const root='android/app/src/main/';
const outline=fs.readFileSync(root+'res/drawable/widget_prayer_active.xml','utf8');
const layout=fs.readFileSync(root+'res/layout/prayer_widget.xml','utf8');
const controller=fs.readFileSync(root+'java/com/salati/prayer/PrayerWidget.java','utf8');
const manifest=fs.readFileSync(root+'AndroidManifest.xml','utf8');
const get=(tag,attribute)=>outline.match(new RegExp('<'+tag+'\\b[^>]*android:'+attribute+'="([^"]+)"'))?.[1];
assert.equal(get('stroke','width'),'1dp','Active border matches user-provided blue-slate rounded capsule reference');
assert.equal(get('stroke','color'),'#9A85878B','Active border matches user-provided blue-slate rounded capsule reference');
assert.equal(get('solid','color'),'#B35B5C60','Active fill matches user-provided charcoal reference');
assert.equal(get('corners','radius'),'20dp','Active badge must match the exact rounded user reference');
assert(!/<gradient\b/i.test(outline),'Remove washed-out gray gradient');
assert.equal(get('inset','insetLeft'),'2dp','Keep separation from adjacent prayers');
assert.equal(get('inset','insetRight'),'2dp','Keep separation from adjacent prayers');
assert.equal(get('inset','insetTop'),'1dp');
assert.equal(get('inset','insetBottom'),'1dp');
assert(!/android:stroke="#55FFFFFF"/.test(layout),'No white widget outline');
assert(layout.includes('android:id="@+id/widget_maghrib" android:layout_width="match_parent" android:layout_height="26dp"'),'Only time has a small pill viewport');
assert(controller.includes('views.setInt(cells[n],"setBackgroundResource",0)'),'Remove legacy full-height cell highlights on every update');
const strip=layout.match(/<LinearLayout android:layout_width="match_parent" android:layout_height="54dp"[\s\S]+?<\/LinearLayout><\/LinearLayout><\/FrameLayout>/)?.[0];
assert(strip,'Prayer row remains a shared strip with six cells');
const keys=['fajr','sunrise','dhuhr','asr','maghrib','isha'];
for(const key of keys) {
  assert(layout.includes('android:id="@+id/widget_cell_'+key+'"'),'Missing cell '+key);
  assert(layout.includes('android:id="@+id/widget_label_'+key+'"'),'Missing label '+key);
  assert(layout.includes('android:id="@+id/widget_'+key+'"'),'Missing time '+key);
}
assert(controller.includes('names[n].equals(upcomingKey)?R.drawable.widget_prayer_active:0'),
 'Highlight exactly one upcoming prayer; clear old selection on widget refresh');
assert(controller.includes('views.setInt(times[n],"setBackgroundResource"'),
 'RemoteViews must apply native background to the time only, not its cell');
assert(controller.includes('!"sunrise".equals(key)'),
 'Sunrise is not a prayer and cannot become active prayer');
assert(manifest.includes('android:usesCleartextTraffic="false"'),'Security policy must remain intact');
// Alpha blend #E6FFFFFF on #15181D, then WCAG contrast (no screenshot simulation).
const alpha=0.70,bg=[0x16,0x18,0x1B];
const mixed=bg.map((c,i)=>(1-alpha)*c+alpha*[0x5B,0x5C,0x60][i]);
const luminance=parts=>parts.map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0);
const contrast=(luminance(mixed)+.05)/(luminance(bg)+.05);
assert(contrast>=1.3,'Reference silver-outline contrast below 1.8:1: '+contrast);
console.log('PASS: time-only gray active-prayer capsule, contrast '+contrast.toFixed(2)+':1, 6 intact cells, only upcoming prayer selected, exact charcoal and original widget dimensions and colors.');
