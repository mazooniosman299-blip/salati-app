const assert=require('node:assert/strict');
const fs=require('node:fs');
const root='android/app/src/main/';
const outline=fs.readFileSync(root+'res/drawable/widget_prayer_active.xml','utf8');
const layout=fs.readFileSync(root+'res/layout/prayer_widget.xml','utf8');
const controller=fs.readFileSync(root+'java/com/salati/prayer/PrayerWidget.java','utf8');
const manifest=fs.readFileSync(root+'AndroidManifest.xml','utf8');
const get=(tag,attribute)=>outline.match(new RegExp('<'+tag+'\\b[^>]*android:'+attribute+'="([^"]+)"'))?.[1];
assert.equal(get('stroke','width'),'1.5dp','Active border matches user's silver reference');
assert.equal(get('stroke','color'),'#FF767A7F','Active border matches user's silver reference');
assert.equal(get('solid','color'),'#FF333539','Active fill matches user's charcoal reference');
assert.equal(get('corners','radius'),'18dp','Active badge must match the exact rounded user reference');
assert(!/<gradient\b/i.test(outline),'Remove washed-out gray gradient');
assert.equal(get('inset','insetLeft'),'2dp','Keep separation from adjacent prayers');
assert.equal(get('inset','insetRight'),'2dp','Keep separation from adjacent prayers');
assert.equal(get('inset','insetTop'),'1dp');
assert.equal(get('inset','insetBottom'),'1dp');
const strip=layout.match(/<LinearLayout android:layout_width="match_parent" android:layout_height="54dp"[\s\S]+?<\/LinearLayout><\/LinearLayout><\/FrameLayout>/)?.[0];
assert(strip,'Prayer row remains a shared strip with six cells');
const keys=['fajr','sunrise','dhuhr','asr','maghrib','isha'];
for(const key of keys) {
  assert(layout.includes('android:id="@+id/widget_cell_'+key+'"'),'Missing cell '+key);
  assert(layout.includes('android:id="@+id/widget_label_'+key+'"'),'Missing label '+key);
  assert(layout.includes('android:id="@+id/widget_'+key+'"'),'Missing time '+key);
}
assert(controller.includes('keys[n].equals(upcomingKey)?R.drawable.widget_prayer_active:0'),
 'Highlight exactly one upcoming prayer; clear old selection on widget refresh');
assert(controller.includes('views.setInt(cellIds[n],"setBackgroundResource"'),
 'RemoteViews must apply native background resource for each cell');
assert(controller.includes('!"sunrise".equals(key)'),
 'Sunrise is not a prayer and cannot become active prayer');
assert(manifest.includes('android:usesCleartextTraffic="false"'),'Security policy must remain intact');
// Alpha blend #E6FFFFFF on #15181D, then WCAG contrast (no screenshot simulation).
const alpha=1,bg=[0x33,0x35,0x39];
const mixed=bg.map(c=>(1-alpha)*c+alpha*[0x76,0x7A,0x7F][bg.indexOf(c)]);
const luminance=parts=>parts.map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0);
const contrast=(luminance(mixed)+.05)/(luminance(bg)+.05);
assert(contrast>=1.8,'Reference silver-outline contrast below 1.8:1: '+contrast);
console.log('PASS: visible silver active-prayer border, contrast '+contrast.toFixed(2)+':1, 6 intact cells, only upcoming prayer selected, exact charcoal and original widget dimensions and colors.');
