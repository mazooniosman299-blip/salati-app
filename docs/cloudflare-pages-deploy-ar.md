# نشر صلاتي مجاناً على Cloudflare Pages وتحديثه تلقائياً من GitHub

**المصدر**: مستودع `mazooniosman299-blip/salati-app`، الفرع `main`. لا تنشئ مشروع ويب جديداً ولا تحذف مشروع صلاتي على ChatGPT Sites.

## ربط Cloudflare Pages مرة واحدة

1. افتح https://dash.cloudflare.com/ وسجّل دخول حسابك الشخصي.
2. Workers & Pages → Create application → Pages → **Connect to Git**.
3. اختَر GitHub، ثم امنح Cloudflare حق الوصول إلى مستودع `mazooniosman299-blip/salati-app` فقط.
4. اختَر مستودع **salati-app** والفرع الإنتاجي **main**، واكتب اسم مشروع Pages متاحاً (مثلاً `salati-world-prayer-om` إذا لم يكن محجوزاً).
5. إعدادات البناء:
   - Framework preset: **None**.
   - Build command: `npm ci && npm run build:cloudflare && npm run test:cloudflare`
   - Build output directory: `dist`
   - Root directory: **/** (جذر المستودع).
   - Node.js: **22** (أضف `NODE_VERSION=22` إن لزم).
   - لا تضف `SALATI_PUBLIC_ORIGIN` إلا إذا كان عندك دومين مخصص؛ البرنامج يأخذ دومين `*.pages.dev` تلقائياً من `CF_PAGES_URL`.
6. اضغط Save and Deploy. احصل على **الرابط الحقيقي** من لوحة Cloudflare ولا تخمّن الاسم.
7. بعد النجاح، أي push على GitHub branch `main` يبدأ نشر إصدار جديد تلقائياً. يوفّر GitHub Actions اختبارات مستقلة باسم *Salati Cloudflare Pages release QA*.

## ماذا يفعل البناء؟

- يَستخدم نفس ملفات صلاتي الفعلية في `dist`، والمصحف، والصور، والأصوات، والتصميم الداكن.
- يولّد ملفات التطبيق وصفحات المدن من المصادر الأصلية، ثم يعدّل `canonical` و`og:url` وخريطة الموقع وروابط الصفحات إلى رابط Cloudflare الصحيح.
- ينشئ `robots.txt` و`_headers` لضمان تجديد Service Worker والمحتوى عند نشر إصدار جديد.
- يرفض البناء إذا كان ملف أكبر من حد Cloudflare Pages البالغ 25 MiB.
- يختبر وجود صفحات وخطوط وأصول القرآن والمواقيت والقائمة.
- يترك ملف APK القديم دون استبدال/إعادة توقيع؛ تحديث الويب ليس تحديث Android.

## فحوص القبول المباشر بعد النشر

1. افتح الرابط الجديد من متصفح خاص، وتأكد من ظهور تصميم صلاتي الداكن وأقسام المواقيت والقرآن والقبلة والإعدادات.
2. افتح `/robots.txt` و`/sitemap.xml` وتأكّد من أن الرابط الجديد يظهر فيهما وليس `chatgpt.site`.
3. افتح `/sw.js` وابحث عن `salati-shell-v146` (إلى أن يزداد رقم ذاكرة النسخة لاحقاً).
4. افتح صفحة `/ar/prayer-times/muscat.html` وصفحة سياسة الخصوصية.
5. من الهاتف ثبّت الموقع كتطبيق PWA إن شئت. **التفضيلات المخزنة في localStorage على الرابط القديم لا تنتقل تلقائياً للرابط الجديد**؛ حدّد موقعك وإعدادات الأذان مجدداً.
6. أي تعديل جديد على GitHub `main` يجب أن يظهر في سجل Cloudflare Deployments؛ اطلب تحققاً من رابط الملف المباشر قبل إعلان نجاح النشر.

## مشكلات محتملة

- إذا لم يظهر مستودع `salati-app` في Cloudflare: من GitHub Apps اسمح بالوصول إليه، دون منح صلاحيات لجميع المستودعات.
- إذا فشل بناء الموقع بسبب متغير الدومين: تأكد من وجود `CF_PAGES_URL` في بيئة Cloudflare Pages، أو عيّن `SALATI_PUBLIC_ORIGIN=https://<عنوان-المشروع-الحقيقي>.pages.dev` **بعد إنشاء المشروع فعلاً**.
- إذا فشل فحص حجم ملف، لا تحذف الملفات الضرورية عشوائياً؛ عدّل استراتيجية نشر الأرشيفات القديمة فقط.
- إذا تعذر تسجيل الدخول أو إنشاء مشروع Pages، الملفات جاهزة في GitHub لكن النشر **لم يحدث بعد**.
- الرابط القديم على ChatGPT Sites يظل مستقلاً ولا يُحدّث تلقائياً من GitHub.
