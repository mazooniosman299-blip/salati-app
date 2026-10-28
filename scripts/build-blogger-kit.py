"""Build a reviewable, offline Blogger import kit. Does not publish or activate ads."""
from pathlib import Path
import html
import json
import uuid
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
content = json.loads((ROOT / 'blogger-kit/content.json').read_text())
output = ROOT / 'dist/downloads/salati-blogger'
output.mkdir(parents=True, exist_ok=True)
for previous in output.iterdir():
    if previous.is_file():
        previous.unlink()
escape = html.escape
atom = 'http://www.w3.org/2005/Atom'
app = 'http://www.w3.org/2007/app'
ET.register_namespace('', atom)
ET.register_namespace('app', app)
feed = ET.Element(f'{{{atom}}}feed')
def node(parent, name, text=None, **attributes):
    element = ET.SubElement(parent, f'{{{atom}}}{name}', attributes)
    element.text = text
    return element
node(feed, 'id', 'urn:uuid:' + str(uuid.uuid5(uuid.NAMESPACE_URL, content['blog_url'])))
node(feed, 'title', 'دليل صلاتي')
node(feed, 'updated', '2026-10-23T19:00:00Z')
node(feed, 'generator', 'Salati offline content kit')
author = node(feed, 'author')
node(author, 'name', 'دليل صلاتي')
index = []
for kind, key in [('post', 'posts'), ('page', 'pages')]:
    for item in content[key]:
        fragment = ''.join('<section><h2>' + escape(s['heading']) + '</h2>' + ''.join('<p>' + escape(p) + '</p>' for p in s['paragraphs']) + '</section>' for s in item['sections'])
        fragment += '<p>' + ' · '.join('<a href="' + escape(link['url'], quote=True) + '">' + escape(link['label']) + '</a>' for link in item.get('links', [])) + '</p>'
        (output / (item['id'] + '-fragment.html')).write_text(fragment)
        document = '<!doctype html><html lang="ar" dir="rtl"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>' + escape(item['title']) + '</title><style>body{max-width:760px;margin:3rem auto;padding:0 1rem;font:19px/1.9 system-ui;color:#173e35}a{color:#146c58}h1{line-height:1.5}</style><main><h1>' + escape(item['title']) + '</h1>' + fragment + '</main></html>'
        (output / (item['id'] + '.html')).write_text(document)
        entry = node(feed, 'entry')
        node(entry, 'id', 'urn:uuid:' + str(uuid.uuid5(uuid.NAMESPACE_URL, content['blog_url'] + item['id'])))
        node(entry, 'published', '2026-10-23T19:00:00Z')
        node(entry, 'updated', '2026-10-23T19:00:00Z')
        node(entry, 'category', scheme='http://schemas.google.com/g/2005#kind', term='http://schemas.google.com/blogger/2008/kind#' + kind)
        for label in item['labels']:
            node(entry, 'category', scheme='http://www.blogger.com/atom/ns#', term=label)
        node(entry, 'title', item['title'], type='text')
        node(entry, 'content', fragment, type='html')
        control = ET.SubElement(entry, f'{{{app}}}control')
        ET.SubElement(control, f'{{{app}}}draft').text = 'yes'
        index.append('<li><a href="' + item['id'] + '.html">' + escape(item['title']) + '</a> — ' + ('مقالة' if kind == 'post' else 'صفحة') + '</li>')
ET.ElementTree(feed).write(output / 'import.xml', encoding='utf-8', xml_declaration=True)
(output / 'content.json').write_text(json.dumps(content, ensure_ascii=False, indent=2) + '\n')
(output / 'ads.txt').write_text('google.com, pub-5086201923236113, DIRECT, f08c47fec0942fa0\n')
readme = '''حزمة دليل صلاتي — محتوى جاهز للمراجعة والاستيراد

لم تُنشر هذه المواد في حساب Blogger، ولم تُفعّل إعلانات أو تُقدّم المدونة للمراجعة من هذه البيئة. لا يوجد اتصال مصرح به بحساب Blogger هنا. لا تحتاج إلى إرسال كلمة مرور أو رمز دخول.

1. افتح لوحة salati-guide.blogspot.com بحسابك وخذ نسخة احتياطية من المحتوى الحالي قبل الاستيراد.
2. الإعدادات ← إدارة المدونة ← استيراد المحتوى. اختر import.xml وألغِ خيار النشر التلقائي إن ظهر. الحزمة تتضمن 5 مقالات و3 صفحات معلّمة كمسودات. لا تكرر الاستيراد حتى لا تتكرر المقالات.
3. راجع النصوص وبيانات الاتصال والخصوصية في المسودات، ثم انشر. إذا لم يقبل Blogger ملف Atom أو لم يستورد الصفحات، أنشئ المقالات/الصفحات من المحرر والصق محتوى ملفات *-fragment.html في وضع HTML؛ العناوين والوصف موجودة في content.json. تحقّق من صفحة الخصوصية لتطابق إعداداتك الفعلية.
4. بعد إنشاء الصفحات، أضف روابط عن المدونة/اتصل بنا/الخصوصية إلى قائمة الصفحات. الروابط الدائمة يصدرها Blogger بعد النشر؛ لم نفترضها مسبقًا.
5. من قسم الأرباح اربط حساب AdSense الحالي بالمدونة. معرّف الناشر العام: pub-5086201923236113. لا تضع شيفرة الإعلانات داخل المقالات. التفعيل والمراجعة يعتمدان على حساب Google وسياساته.
6. إذا طلب AdSense ملف ads.txt ولم تُدره إضافة Blogger تلقائيًا: الإعدادات ← تحقيق الربح ← ملف ads.txt مخصص، ثم أضف السطر الموجود في ads.txt مع الاحتفاظ بأي سجلات صحيحة قائمة. تحقّق من https://salati-guide.blogspot.com/ads.txt بعد النشر. قد يتأخر تحديث حالة الزحف.
7. في Search Console استخدم ملكية المدونة الحالية واطلب فهرسة روابط المقالات بعد نشرها، وأرسل sitemap.xml الخاص بالمدونة إذا كان متاحًا. لا يعادل نشر المحتوى قبول AdSense أو ضمان الأرباح.

ملفات HTML الكاملة للمعاينة فقط وموسومة noindex. تحقّقنا من JSON وXML وعدد المسودات والنصوص؛ لا يمكن اختبار الاستيراد الفعلي أو مراجعة محتوى المدونة الحالي دون دخول الحساب.

مراجع Google:
https://support.google.com/blogger/answer/41387?hl=ar
https://support.google.com/blogger/answer/1269077?hl=ar
'''
(output / 'README-AR.txt').write_text(readme)
(output / 'index.html').write_text('<!doctype html><html lang="ar" dir="rtl"><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><meta name="viewport" content="width=device-width, initial-scale=1"><title>مراجعة حزمة دليل صلاتي</title><style>body{max-width:850px;margin:3rem auto;padding:0 1rem;font:19px/1.9 system-ui;color:#173e35}a{color:#146c58}</style><h1>حزمة دليل صلاتي</h1><p>5 مقالات و3 صفحات جاهزة للمراجعة. لم تُنشر في Blogger.</p><p><a href="../salati-blogger-ready.zip">تنزيل الحزمة</a> · <a href="README-AR.txt">تعليمات الاستيراد والربط</a></p><ul>' + ''.join(index) + '</ul></html>')
with zipfile.ZipFile(ROOT / 'dist/downloads/salati-blogger-ready.zip', 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for file in sorted(output.iterdir()):
        if file.is_file():
            archive.write(file, 'salati-blogger/' + file.name)
entries = ET.parse(output / 'import.xml').findall(f'{{{atom}}}entry')
assert len(entries) == 8
assert all(e.find(f'{{{app}}}control/{{{app}}}draft').text == 'yes' for e in entries)
assert len({e.find(f'{{{atom}}}id').text for e in entries}) == 8
print('Blogger kit: 5 articles + 3 pages, valid Atom XML, unique offline IDs, all drafts, HTML fallbacks. Not published to Blogger.')
