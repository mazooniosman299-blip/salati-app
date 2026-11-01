const assert=require('node:assert/strict');
const fs=require('node:fs');
const root='android/app/src/main/';
const outline=fs.readFileSync(root+'res/drawable/widget_prayer_active.xml','utf8');
const layout=fs.readFileSync(root+'res/layout/prayer_widget.xml','utf8');
const controller=fs.readFileSync(root+'java/com/salati/prayer/PrayerWidget.java','utf8');
const manifest=fs.readFileSync(root+'AndroidManifest.xml','utf8');
const get=(tag,attribute)=>outline.match(new RegExp('<'+tag+'\\b[^>]*android:'+attribute+'="([^"]+)"'))?.[1];
assert.equal(get('stroke','width'),'2dp','Active border must be 2dp and visible');
assert.equal(get('stroke','color'),'#E6FFFFFF','Active border must be high-contrast white');
assert.equal(get('solid','color'),'#FF15181D','Active fill must be solid charcoal');
assert.equal(get('corners','radius'),'3dp','Active prayer border must be rectangular, not an oval');
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
const alpha=0xE6/255,bg=[0x15,0x18,0x1D];
const mixed=bg.map(c=>(1-alpha)*c+alpha*255);
const luminance=parts=>parts.map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0);
const contrast=(luminance(mixed)+.05)/(luminance(bg)+.05);
assert(contrast>=10,'Selected border contrast below 10:1: '+contrast);
console.log('PASS: visible 2dp active-prayer border, contrast '+contrast.toFixed(2)+':1, 6 intact cells, only upcoming prayer selected, exact charcoal and original widget dimensions and colors.');
