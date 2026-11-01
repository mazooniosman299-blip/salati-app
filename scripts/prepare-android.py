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


# Public city pages and the main page use site-root paths such as
# "/style.css" and "/ar/prayer-times/muscat.html". In Android those resolve
# to https://appassets.androidplatform.net/<path>, outside MainActivity's
# strictly validated /assets/www/ URL scope and fail to load. Rewrite only
# URLs that actually correspond to packaged local files; leave external,
# protocol-relative and download-site references untouched. The website
# source remains unchanged.
root_asset_ref=re.compile(r'(?P<attr>\b(?:href|src|poster|action)\s*=\s*)(?P<quote>["\x27])(?P<url>/[^"\x27]*)(?P=quote)',re.I)
changed_pages=0;changed_urls=0
for html in target.rglob('*.html'):
    before=html.read_text(encoding='utf-8')
    def local_asset(match):
        global changed_urls
        original=match.group('url')
        if original.startswith('//') or original.startswith('/assets/www/'):
            return match.group(0)
        relative=original.partition('?')[0].partition('#')[0].lstrip('/')
        if not relative or not (target/relative).is_file():
            return match.group(0)
        changed_urls+=1
        return match.group('attr')+match.group('quote')+'/assets/www'+original+match.group('quote')
    after=root_asset_ref.sub(local_asset,before)
    if after!=before:
        html.write_text(after,encoding='utf-8')
        changed_pages+=1
assert changed_pages>=30 and changed_urls>=140, ('Missing expected native public-page URL fixes',changed_pages,changed_urls)
for html in target.rglob('*.html'):
    text=html.read_text(encoding='utf-8')
    for match in root_asset_ref.finditer(text):
        url=match.group('url')
        if url.startswith('//') or url.startswith('/assets/www/'):continue
        target_file=target/url.partition('?')[0].partition('#')[0].lstrip('/')
        assert not target_file.is_file(), ('Existing Android asset still has broken absolute URL',html,url)
print('Fixed Android local asset URLs on',changed_pages,'HTML pages; corrected',changed_urls,'resource/navigation references.')
