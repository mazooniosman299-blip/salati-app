const assert=require('node:assert/strict'),fs=require('node:fs'),Module=require('node:module'),{buildSync}=require('esbuild');
function load(file){const m=new Module(file,module);m._compile(buildSync({entryPoints:[file],bundle:true,platform:'node',format:'cjs',write:false}).outputFiles[0].text,file);return m.exports;}
const {AUDIO_DEFAULTS}=load('audio-controller.js');
assert(!Object.hasOwn(AUDIO_DEFAULTS,'approachEnabled'),'Approach defaults must be removed');
assert(!Object.hasOwn(AUDIO_DEFAULTS,'approachMinutes'));
const {restoreSettings}=load('settings-restore.js');const restored=restoreSettings({name:'مسقط',count:42,audio:{...AUDIO_DEFAULTS,approachEnabled:true,approachMinutes:15,volume:.35,voice:'qatami',fajrAnnouncement:false}});
assert(!Object.hasOwn(restored.audio,'approachEnabled'));assert(!Object.hasOwn(restored.audio,'approachMinutes'));assert.equal(restored.audio.volume,.35);assert.equal(restored.audio.voice,'qatami');assert.equal(restored.audio.fajrAnnouncement,false);assert.equal(restored.count,42);
const manifest=fs.readFileSync('android/app/src/main/AndroidManifest.xml','utf8');assert(!manifest.includes('.ApproachService'));assert(manifest.includes('.FajrPreviewService'));assert(!fs.existsSync('android/app/src/main/java/com/salati/prayer/ApproachService.java'));const receiver=fs.readFileSync('android/app/src/main/java/com/salati/prayer/ApproachReceiver.java','utf8');assert(receiver.includes('cancelLegacyApproach'));assert(!receiver.includes('startForegroundService'));const mainJava=fs.readdirSync('android/app/src/main/java/com/salati/prayer').map(name=>fs.readFileSync('android/app/src/main/java/com/salati/prayer/'+name,'utf8')).join('\n');assert(!mainJava.includes('ApproachService.class'));
const {PrayerAnnouncements}=load('prayer-announcements.js');const flush=async()=>{for(let i=0;i<8;i++)await Promise.resolve()};
(async()=>{
 let settings={...AUDIO_DEFAULTS,enabled:true,prayers:{...AUDIO_DEFAULTS.prayers}};
 let said=[],cancelled=0;
 class Utterance{constructor(text){this.text=text}}
 const speech={getVoices(){return [{lang:'ar-OM'}]},speak(u){said.push(u)},cancel(){cancelled++}};
 const a=new PrayerAnnouncements({getSettings:()=>settings,speech,Utterance});
 for(const name of ['الفجر','الظهر','العصر','المغرب','العشاء'])
  assert.equal((await a.speak('اقتربت صلاة '+name)).status,'unavailable');
 assert.equal(said.length,0);
 assert.equal(typeof a.tick,'undefined','No foreground approach scheduler remains');
 for(const prayer of ['dhuhr','asr','maghrib','isha','sunrise'])
  assert.equal((await a.beforeAdhan(prayer)).status,'skipped');
 const first=a.beforeAdhan('fajr');await flush();
 assert.equal(said.length,1);
 assert.equal(said[0].text,'الصلاة خير من النوم');
 assert.equal(said[0].lang,'ar');
 assert(said[0].voice?.lang==='ar-OM');
 said[0].onend();await first;
 assert.equal(said.length,1,'Fajr phrase must never repeat automatically');
 settings.fajrAnnouncement=false;assert.equal((await a.beforeAdhan('fajr')).status,'skipped');settings.fajrAnnouncement=true;settings.prayers.fajr=false;assert.equal((await a.beforeAdhan('fajr')).status,'skipped');settings.prayers.fajr=true;settings.enabled=false;assert.equal((await a.beforeAdhan('fajr')).status,'skipped');settings.enabled=true;settings.volume=0;assert.equal((await a.speak('الصلاة خير من النوم')).status,'muted');
 const html=fs.readFileSync('dist/index.html','utf8');for(const id of ['approachToggle','approachMinutes','previewApproach'])assert(!html.includes('id="'+id+'"'));assert(html.includes('id="fajrAnnouncementToggle"')&&html.includes('id="previewFajrPhrase"'));
 console.log('PASS: removed unlicensed audio source, Fajr uses on-device Arabic TTS once; opt-out/volume respected.');
})().catch(e=>{console.error(e);process.exitCode=1});
