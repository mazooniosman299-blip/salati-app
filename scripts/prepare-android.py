from pathlib import Path
import shutil,re
root=Path(__file__).resolve().parent.parent
source=root/'dist';target=root/'android/app/src/main/assets/www'
if target.exists():shutil.rmtree(target)
shutil.copytree(source,target,ignore=shutil.ignore_patterns('downloads','sw.js'))
# Android loads the versioned entry from index.html. Omit its unreferenced compatibility copy.
entry=re.search(r'src="(app-v[\d.]+\.js)', (target/'index.html').read_text())
if entry:
    (target/'app.js').unlink(missing_ok=True)
    for old in target.glob('app-v*.js'):
        if old.name!=entry[1]:old.unlink()
# Keep only the current app styles and referenced mosque asset in the APK.
index=(target/'index.html').read_text()
stylesheet_references='\n'.join(page.read_text() for page in target.rglob('*.html'))
for style in target.glob('*.css'):
    # Canonical UI and the two separately authored public-page surfaces are
    # the ONLY stylesheet assets shipped. Old design patches are historical
    # test fixtures, never Android runtime inputs.
    if style.name in ('salati-ui.css','city-pages.css','public-pages.css'):
        continue
    if re.search(r'href="[^"]*'+re.escape(style.name)+r'"',stylesheet_references):
        continue
    style.unlink()
assert (target/'salati-ui.css').is_file(), 'Missing canonical stylesheet in Android package'
assert not any((target/n).exists() for n in ('design-restoration-v1.0.113.css','eight-mobile-root-fixes-20261101.css','mobile-layout-contract-20261101.css'))
for image in (target/'images').glob('mosque*'):
    if image.is_file() and image.suffix in ['.webp','.jpg'] and 'images/'+image.name not in index:image.unlink()

p=target/'index.html';s=p.read_text()
s=re.sub(r'data-ar="فعّل الأذان مرة واحدة؛[^"\n]+" data-en="Enable adhan once;[^"\n]+"', 'data-ar="فعّل الأذان واسمح بالإشعارات والمنبّهات الدقيقة لتشغيله في الخلفية. اتبع إعدادات توفير البطارية في هاتفك، وافتح التطبيق مجددًا بعد الإيقاف الإجباري. يعتمد التشغيل على أذونات أندرويد وصوت الجهاز." data-en="Enable adhan and allow notifications and exact alarms for background playback. Check your phone’s battery restrictions and reopen the app after a force stop. Playback depends on Android permissions and device volume."',s)
s=s.replace('الأذان والدعاء يعملان بعد تفعيل الصوت أثناء فتح التطبيق ونشاطه؛ لا توجد تنبيهات مضمونة عند إغلاقه أو قفل الشاشة.','أذان الخلفية يستخدم منبّهات أندرويد وخدمة تشغيل صوتية، ويحتاج أذونات الإشعارات والمنبّهات الدقيقة. قد تمنع قيود البطارية أو الإيقاف الإجباري تشغيله. تُحفظ جداول محسوبة لأكثر من سنة؛ افتح التطبيق دوريًا لتجديدها، وحدّث الموقع عند السفر.')
s=s.replace('Adhan and dua play after activating audio while the app is open and active; notifications with the app closed or screen locked are not guaranteed.','Background adhan uses Android alarms and a media service, with notification and exact-alarm permissions. Battery restrictions or force stop may prevent playback. More than one year of calculated schedules is stored; open the app periodically to refresh, and update your location when travelling.')
s=s.replace('تُشغَّل عبارة «الصلاة خير من النوم» مرة واحدة عند الفجر وفق إعداداتك. في المتصفح يلزم إبقاء الصفحة نشطة.','تُشغَّل عبارة «الصلاة خير من النوم» مرة واحدة عند الفجر وفق إعداداتك. يلزم السماح بالإشعارات والمنبّهات الدقيقة للتشغيل في الخلفية.')
s=s.replace('The Fajr phrase plays once according to your settings. In browsers, keep the page active.','The Fajr phrase plays once according to your settings. Allow notifications and exact alarms for background playback.')
p.write_text(s)
print('Packaged offline UI, Quran, fonts and recordings for Android.')
